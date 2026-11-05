# EventFlow

Avaliação Final — **Desenvolvimento de Aplicativos** (UniNorte)

Aplicativo Android para listar, mapear e gerenciar eventos, com API própria.

| Parte | Tecnologias | Pasta |
|---|---|---|
| App | Vue 3, Vite, Ionic, Capacitor, Leaflet | [`app/`](app/README.md) |
| API | Python, FastAPI, SQLAlchemy, JWT | [`api/`](api/README.md) |
| Banco e imagens | PostgreSQL + Storage (Supabase) | — |
| Hospedagem da API | Koyeb (gratuito) | — |
| APK | Gerado automaticamente pelo GitHub Actions | `.github/workflows/apk.yml` |

## Funcionalidades

- **Login** com e-mail e senha, sessão mantida no aparelho e **logout**
- **Lista de eventos** com miniatura, nome, data, preço e categoria, **busca** e filtro por categoria
- **Mapa** com um marcador por local; ao tocar, mostra nome, data, preço e **Ver detalhes**
- **Detalhes** completos do evento, com mapa do local
- **Cadastro e edição de eventos** com imagem pela **câmera ou galeria**
- **Categorias**: listar, cadastrar, editar e excluir
- **Locais**: listar, cadastrar, editar e excluir, com latitude e longitude escolhidas no mapa ou pelo GPS
- **Perfil** com os dados do usuário e botão **Sair**

## Colocando no ar (ordem)

1. **Supabase**: crie o projeto, o bucket público `eventos` e copie as chaves. Detalhes no [README da API](api/README.md#1-supabase-banco--imagens).
2. **GitHub**: suba esta pasta inteira para um repositório.
3. **Koyeb**: crie o serviço apontando para o repositório, com **Work directory** = `api`, e cadastre as variáveis de ambiente. Detalhes no [README da API](api/README.md#3-koyeb-api).
4. **Dados de exemplo**: no seu PC, rode `python seed.py` dentro de `api/` com o `DATABASE_URL` do Supabase.
5. **URL da API no GitHub**: em **Settings → Secrets and variables → Actions → Variables**, crie `API_URL` com a URL do Koyeb (ex.: `https://eventflow-seunome.koyeb.app`, sem barra no final).
6. **APK**: vá em **Actions → Gerar APK → Run workflow**. Em uns 5 minutos, o APK aparece em **Artifacts** dentro da execução.
7. **Versão de entrega**: crie uma tag para publicar o APK em **Releases** com link fixo:
   ```bash
   git tag v1.0
   git push origin v1.0
   ```
8. **Manter acordado**: cron-job.org chamando `https://SUA-API.koyeb.app/health` a cada 30 minutos.

Login de teste criado pelo seed: **teste@eventflow.com** / **123456**

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
| 7. API | Abrir `https://SUA-API.koyeb.app/docs` e mostrar que o evento criado no app está lá |
| 8. APK | Mostrar a Release no GitHub e o app instalado |

**Antes de apresentar:** abra `https://SUA-API.koyeb.app/health` e confira `{"status":"ok","banco":"ok"}`.
