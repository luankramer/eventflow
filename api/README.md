# EventFlow API

API do aplicativo **EventFlow** (Avaliação Final — Desenvolvimento de Aplicativos).

**Stack:** FastAPI · SQLAlchemy 2 · PostgreSQL (Supabase) · JWT · Supabase Storage para as imagens.
**Hospedagem gratuita:** API no Koyeb + banco e imagens no Supabase.

---

## Rotas

Todas as rotas, exceto `/`, `/health`, `/auth/login` e `/auth/registro`, exigem o header
`Authorization: Bearer <token>`.

| Método | Rota | O que faz |
|---|---|---|
| POST | `/auth/login` | `{email, senha}` → `{access_token, usuario}` |
| POST | `/auth/registro` | `{nome, email, senha}` → cria a conta e já devolve o token |
| GET | `/auth/me` | Dados do usuário logado (tela de Perfil e validação da sessão) |
| POST | `/auth/logout` | Confirma o logout (o app apaga o token salvo) |
| GET | `/eventos?busca=` | Lista eventos com categoria e local. Busca por nome, descrição, categoria ou local. Filtros opcionais `categoria_id` e `local_id` |
| GET | `/eventos/{id}` | Detalhes completos |
| POST / PUT | `/eventos`, `/eventos/{id}` | Cadastro e edição |
| DELETE | `/eventos/{id}` | Exclusão |
| GET / POST | `/categorias` | Listar e cadastrar (`nome`, `descricao`, `cor` em `#RRGGBB`, `icone`) |
| GET / PUT / DELETE | `/categorias/{id}` | Detalhar, editar, excluir (bloqueado se houver eventos) |
| GET / POST | `/locais` | Listar e cadastrar (nome, latitude, longitude, endereço opcional) |
| GET / PUT / DELETE | `/locais/{id}` | Detalhar, editar, excluir (bloqueado se houver eventos) |
| POST | `/upload` | Envia a foto (campo `arquivo`, multipart) → `{url}` |
| GET | `/health` | Testa API + banco (usado pelo cron-job para manter tudo acordado) |

A documentação interativa fica em **`/docs`**. Para testar rotas protegidas lá: faça login em
`/auth/login`, copie o `access_token` e cole no botão **Authorize**.

### Formato de um evento

Envio (`POST`/`PUT /eventos`):

```json
{
  "nome": "Festival de Música",
  "descricao": "Bandas locais ao ar livre",
  "data": "2026-12-10",
  "hora": "19:30",
  "preco": 25.5,
  "categoria_id": 1,
  "local_id": 2,
  "imagem_url": "https://xxxx.supabase.co/storage/v1/object/public/eventos/abc.jpg"
}
```

Resposta: os mesmos campos com `id`, e `categoria` e `local` como objetos completos
(o local traz `latitude` e `longitude`, que o app usa direto nos marcadores do mapa).

### Fluxo de imagem no app

1. O usuário escolhe a foto (câmera ou galeria).
2. O app envia para `POST /upload` e recebe `{ "url": "..." }`.
3. O app manda essa URL em `imagem_url` ao salvar o evento.

No React Native/Expo:

```js
const form = new FormData();
form.append('arquivo', { uri: foto.uri, name: 'foto.jpg', type: foto.mimeType ?? 'image/jpeg' });
const resp = await fetch(`${API_URL}/upload`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}` },  // não defina Content-Type: o fetch monta o boundary
  body: form,
});
const { url } = await resp.json();
```

---

## Rodando no seu PC

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python seed.py                         # dados de exemplo + usuário teste@eventflow.com / 123456
uvicorn app.main:app --reload --host 0.0.0.0
```

Sem `.env`, a API usa SQLite (`eventflow.db`) e salva as imagens na pasta `uploads/`.
Para testar do celular na mesma rede Wi-Fi, use o IP do PC (ex.: `http://192.168.0.10:8000`).

Testes automatizados: `python -m pytest -q`

---

## Deploy gratuito (passo a passo)

### 1. Supabase (banco + imagens)

1. Crie um projeto em [supabase.com](https://supabase.com). Guarde a senha do banco.
2. **Banco:** clique em **Connect** no topo do projeto e copie a URI do **Session pooler**.
   Use esta, e não a "Direct connection" (que só funciona em IPv6). Troque `[YOUR-PASSWORD]` pela sua senha.
3. **Imagens:** vá em **Storage → New bucket**, nome `eventos`, marque **Public bucket**.
4. **Chave:** em **Project Settings → API Keys**, copie a chave secreta (`sb_secret_...`)
   ou, na aba de chaves legadas, a `service_role`. Copie também a **Project URL**.

As tabelas são criadas sozinhas quando a API sobe pela primeira vez.

> Se o seu banco foi criado **antes** da versão com cor e ícone nas categorias, rode uma vez no
> **SQL Editor** do Supabase:
> ```sql
> ALTER TABLE categorias ADD COLUMN IF NOT EXISTS cor varchar(7), ADD COLUMN IF NOT EXISTS icone varchar(40);
> ```

### 2. Repositório

Suba o repositório do projeto (pasta raiz, com `api/` e `app/`) para o GitHub. O Koyeb faz o deploy a partir dele.
O `.gitignore` já impede que o `.env` com suas chaves vá junto.

### 3. Koyeb (API)

1. Crie a conta em [koyeb.com](https://www.koyeb.com) e clique em **Create Web Service → GitHub**.
2. Escolha o repositório. Em **Builder**, selecione **Dockerfile** e, em **Work directory**, informe `api`.
3. Em **Instance**, escolha a **Free**.
4. Em **Environment variables**, cadastre: `DATABASE_URL`, `JWT_SECRET`, `SUPABASE_URL`,
   `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET` (veja o `.env.example`).
5. Em **Ports**, confirme a porta `8000`, e em **Health checks** use o caminho `/health`.
6. Deploy. A URL fica parecida com `https://eventflow-seunome.koyeb.app`. Abra `/docs` para conferir.

### 4. Dados iniciais

No seu PC, crie o `.env` com o mesmo `DATABASE_URL` do Supabase e rode `python seed.py`.
Assim o banco de produção já tem o usuário de teste, categorias, locais e eventos para a apresentação.

### 5. Manter acordado

Em [cron-job.org](https://cron-job.org), crie um job `GET https://SUA-API.koyeb.app/health`
a cada 30 minutos. Isso evita a hibernação do Koyeb e a pausa por inatividade do Supabase.

**No dia da apresentação:** abra `https://SUA-API.koyeb.app/health` uns minutos antes e confira
se retorna `{"status": "ok", "banco": "ok"}`.
