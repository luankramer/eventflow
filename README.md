<p align="center"><img src="marca/png/logo-horizontal.png" alt="EventFlow" width="360"></p>

# EventFlow

Avaliação Final — **Desenvolvimento de Aplicativos** (UniNorte)

Aplicativo Android para listar, mapear e gerenciar eventos, com API própria.

| Parte | Tecnologias | Pasta |
|---|---|---|
| App | Vue 3, Vite, Ionic, Capacitor, Google Maps (OpenStreetMap de reserva) | [`app/`](app/README.md) |
| API | Python, FastAPI, SQLAlchemy, JWT | [`api/`](api/README.md) |
| Banco e imagens | PostgreSQL (Supabase); as fotos ficam no próprio banco | — |
| Hospedagem da API | Render (gratuito, sem cartão) | — |
| APK | Gerado automaticamente pelo GitHub Actions | `.github/workflows/apk.yml` |

## Funcionalidades

- **Login** com e-mail e senha, sessão mantida no aparelho e **logout**
- **Lista de eventos** com miniatura, nome, data, preço e categoria, **busca** e filtro por categoria
- **Mapa** com um marcador por local; ao tocar, mostra nome, data, preço e **Ver detalhes**
- **Detalhes** completos do evento, com mapa do local
- **Cadastro e edição de eventos** com imagem pela **câmera ou galeria**
- **Categorias** (tipos de evento): listar, cadastrar, editar e excluir, com **cor e ícone** escolhidos no cadastro. Todo evento herda a cor da sua categoria, e o mapa mostra uma legenda
- **Locais**: listar, cadastrar, editar e excluir, com latitude e longitude escolhidas no mapa ou pelo GPS
- **Perfil** com os dados do usuário e botão **Sair**

## Segurança

A API passou por uma revisão de segurança com **34 testes de ataque automatizados**: força bruta, token falsificado, injeção de SQL, upload disfarçado, um usuário mexendo no evento de outro e outros. Os problemas encontrados foram corrigidos. Detalhes em [SEGURANCA.md](SEGURANCA.md).

- Só quem cadastrou um evento pode editá-lo ou excluí-lo (403 para os demais)
- Login bloqueado por 15 min após 5 senhas erradas (429)
- Senhas com bcrypt, token JWT com validade, imagens conferidas pela assinatura do arquivo
- APK de release (não depurável) e sem backup dos dados do app

```bash
cd api && pip install -r requirements.txt && pytest   # 38 testes
```

## Identidade visual

O logo (pasta [`marca/`](marca)) é um pino de localização com um ingresso dentro, e um trajeto pontilhado chega até ele: **evento + mapa + fluxo**. As cores são as mesmas do app: pitaya `#E8175D`, ipê `#FFB800` e noite `#1E1036`.

## Colocando no ar (ordem)

1. **Supabase**: crie o projeto e copie o endereço de conexão do banco (Session pooler). Detalhes no [README da API](api/README.md#1-supabase-banco--imagens).
2. **GitHub**: suba esta pasta inteira para um repositório.
3. **Render**: crie o Web Service apontando para o repositório, com **Root Directory** = `api`, runtime Docker, instância Free, e cadastre as variáveis de ambiente, incluindo `SEED_DEMO=true` para criar os dados de exemplo. Detalhes no [README da API](api/README.md#3-render-api).
4. **URL da API no app**: coloque a URL do Render em `app/.env.production` (ex.: `VITE_API_URL=https://eventflow-vnl4.onrender.com`, sem barra no final) e faça o push.
5. **APK**: o push do passo 4 dispara o workflow **Gerar APK**. Em uns 5 minutos, o APK aparece em **Actions → Gerar APK → Artifacts**.
6. **Versão de entrega**: no GitHub, vá em **Releases → Draft a new release**, crie a tag `v1.0` e clique em
   **Publish release**. O workflow anexa o `EventFlow.apk` à release em uns 5 minutos, com um link fixo para entregar.

O workflow **Manter online** chama `/health` a cada 10 minutos, para a API e o banco não hibernarem.
Ele começa a funcionar sozinho assim que a URL do passo 4 estiver no repositório.

Login de teste (criado com `SEED_DEMO=true`): **teste@eventflow.com** / **123456**

## Instalando o APK no celular

Baixe o `EventFlow.apk` no celular e toque para instalar. O Android vai pedir para permitir
"instalar apps de fontes desconhecidas" para o navegador ou gerenciador de arquivos. Basta permitir.

## Roteiro para a apresentação

| Critério | O que mostrar |
|---|---|
| 1. Autenticação | Senha errada mostra o erro → login → fechar e reabrir o app (continua logado) |
| 2. Listagem | Lista com miniaturas → buscar "parque" → filtrar por categoria |
| 3. Mapa | Aba Mapa → tocar num marcador → Ver detalhes |
| 4. Detalhes e cadastro | Detalhes → Editar → criar evento novo tirando foto com a câmera |
| 5. Categorias e locais | Cadastros → nova categoria → novo local tocando no mapa ou em "Minha localização" |
| 6. Perfil | Aba Perfil → Sair → app volta ao login |
| 7. API | Abrir `https://eventflow-vnl4.onrender.com/docs` e mostrar que o evento criado no app está lá |
| 8. APK | Mostrar a Release no GitHub e o app instalado |

**Antes de apresentar:** abra `https://eventflow-vnl4.onrender.com/health` e confira `{"status":"ok","banco":"ok"}`.
