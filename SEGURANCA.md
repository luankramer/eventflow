# Relatório de segurança — EventFlow 1.2

Revisão do código da API e do app, com **testes de ataque automatizados** rodando contra uma cópia local da API (banco temporário, sem tocar no servidor de produção).

```bash
cd api
pytest tests/test_seguranca.py -v      # 34 testes de ataque
pytest                                  # todos os testes (38)
```

Os testes rodam em SQLite e também em PostgreSQL 16, o mesmo banco da produção (Supabase).

## Resumo

| # | Problema encontrado | Gravidade | Situação |
|---|---|---|---|
| 1 | Qualquer usuário logado conseguia **editar ou excluir eventos de outra pessoa** | Alta | Corrigido |
| 2 | Login sem limite de tentativas (**força bruta** de senha) | Média | Corrigido |
| 3 | Upload aceitava **HTML/script disfarçado de imagem** (só olhava o tipo informado pelo celular) | Baixa | Corrigido |
| 4 | APK de entrega era a versão **depurável** e permitia **backup** dos dados do app | Baixa | Corrigido |
| 5 | **Erro 500** com senha de mais de 72 bytes, id gigante na URL ou byte nulo no nome da imagem | Baixa | Corrigido |
| 6 | Faltavam **cabeçalhos de segurança** (nosniff, frame, referrer, HSTS) | Baixa | Corrigido |
| 7 | Token **sem data de validade** era aceito (só se alguém tivesse a chave secreta) | Informativo | Corrigido |
| 8 | Sem limite de tamanho na descrição; link da imagem aceitava `javascript:`; `%` e `_` na busca viravam curinga | Informativo | Corrigido |
| 9 | A API subiria com a **chave JWT padrão** se a variável faltasse em produção | Informativo | Corrigido |

Dependências verificadas com `pip-audit` (API) e `npm audit` (app): **nenhuma vulnerabilidade conhecida**.
Histórico do Git verificado: **nenhuma senha ou chave secreta** foi commitada (só exemplos como `[YOUR-PASSWORD]`).

## Detalhes e correções

### 1. Controle de acesso nos eventos (Alta)
**Antes:** `PUT /eventos/{id}` e `DELETE /eventos/{id}` só exigiam estar logado. Como qualquer pessoa pode criar conta, qualquer uma podia apagar todos os eventos do sistema.
**Teste:** a conta "Beto" tentou editar e excluir o evento da "Ana" e conseguiu (200/204).
**Correção:** a API compara o dono do evento (`criado_por_id`) com o usuário do token e responde **403** se forem diferentes (`api/app/routers/eventos.py`, `_exigir_dono`). Mandar `criado_por_id` no corpo não troca o dono. O app só mostra *Editar* e *Excluir* para quem cadastrou o evento.

### 2. Força bruta no login (Média)
**Antes:** dava para testar senhas sem limite.
**Teste:** 12 senhas erradas seguidas, todas responderam 401.
**Correção:** depois de **5 erros em 15 minutos** para o mesmo e-mail e IP (ou 20 erros para o mesmo e-mail vindos de qualquer IP), a API responde **429** com `Retry-After`, mesmo que a senha esteja certa (`api/app/seguranca_login.py`). O app mostra "Muitas tentativas de login. Tente de novo em 14 min."

### 3. Upload disfarçado (Baixa)
**Antes:** um arquivo HTML com `<script>` enviado como `image/png` era aceito e servido pela API.
**Correção:** a API confere a **assinatura binária** do arquivo (JPEG, PNG, WEBP, HEIC) e ignora o tipo declarado. Ela também lê o arquivo em pedaços e para assim que passa de 5 MB. As imagens são servidas com `nosniff` e `Content-Security-Policy: sandbox`, e só são aceitos nomes no formato que a própria API gera.

### 4. APK (Baixa)
**Antes:** o GitHub Actions gerava `assembleDebug`. Num APK depurável, quem tem o celular em mãos consegue ler pelo cabo USB os dados do app, incluindo o token de login, e inspecionar o WebView.
**Correção:** agora o APK é de **release** (`debuggable false`), com `allowBackup="false"` e `usesCleartextTraffic="false"`. Ele é assinado com a chave de testes do Android, o que basta para instalar fora da Play Store.

### 5 a 9. Robustez e configuração
- A senha agora é limitada em **bytes** (letras com acento ocupam 2 bytes), e não só em caracteres.
- Ids na URL são validados (1 a 2.147.483.647). Um id inválido recebe 422, sem erro 500.
- Todas as respostas levam os cabeçalhos `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` e `Strict-Transport-Security`.
- Tokens precisam ter `exp` e `sub`. A biblioteca já recusava `alg: none`, outra chave e token vencido; os testes confirmam isso.
- Limites: descrição até 5.000 caracteres, busca até 100 e preço até 1.000.000. `imagem_url` precisa começar com `http(s)://`.
- Com PostgreSQL, a API **se recusa a subir** se `JWT_SECRET` for a chave padrão ou tiver menos de 32 caracteres. A chave de produção no Render tem 64.
- CORS: o app usa token no cabeçalho, não cookies. Por isso, liberar a origem não expõe a sessão de ninguém. Métodos e cabeçalhos ficaram restritos aos que o app usa.

## O que foi atacado e já estava seguro
- **Injeção de SQL** na busca (`' OR '1'='1`, `'; DROP TABLE eventos; --`) e nos filtros: o SQLAlchemy sempre usa parâmetros ligados.
- **Token falsificado** (outra chave, `alg: none`, vencido, usuário inexistente): recusado com 401.
- **Senhas**: guardadas com bcrypt (`$2b$`); o hash nunca volta nas respostas.
- **Mensagem de login** igual para e-mail inexistente e senha errada.
- **XSS**: textos como `<img src=x onerror=...>` são guardados como texto e o Vue mostra escapado. O app não usa `v-html`. O único HTML montado à mão, o pino do mapa, só aceita cor hexadecimal e número.
- **Cor da categoria** só aceita `#RRGGBB`; coordenadas fora do intervalo e preço negativo são recusados.
- **Caminho de arquivo** (`../../etc/passwd`): as imagens vêm do banco por id, sem acesso a disco.
- Erros de validação não mostram rastreamento interno.

## Limites conhecidos (aceitos para o escopo do trabalho)
- **Categorias e locais são um catálogo compartilhado**: qualquer usuário logado pode editá-los, como pede o enunciado. Excluir é bloqueado se houver eventos usando o item.
- O limite de tentativas fica na **memória** da API: zera quando o Render reinicia, o que é suficiente com uma instância só.
- `POST /auth/registro` responde 409 para e-mail já cadastrado, o que permite descobrir se um e-mail tem conta. É o comportamento esperado numa tela de cadastro.
- O token fica salvo no **Preferences** do Capacitor, protegido pelo sandbox do Android mas sem criptografia extra. O logout apaga o token do aparelho; o token vence em 30 dias.
- A chave do Google Maps fica dentro do APK, como em todo app de mapa. Para uso real, ela deve ser restrita ao pacote `br.uninorte.eventflow` no Google Cloud.
