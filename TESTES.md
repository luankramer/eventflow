# Testes — EventFlow

O projeto tem **53 testes automatizados**, que rodam sozinhos no GitHub Actions a cada push (workflow [Testes](.github/workflows/testes.yml)):

| Conjunto | Arquivo | Testes | O que cobre |
|---|---|---|---|
| Funcionalidades da API | `api/tests/test_api.py` | 4 | Saúde, leitura pública × escrita protegida, login/logout/perfil, CRUD completo com upload |
| Segurança da API | `api/tests/test_seguranca.py` | 34 | Ataques simulados (ver [SEGURANCA.md](SEGURANCA.md)) |
| Dados de exemplo | `api/tests/test_dados_exemplo.py` | 3 | Carga da demonstração, sem duplicar, conta de teste dona dos eventos |
| Telas do app (ponta a ponta) | `app/e2e/test_telas.py` | 12 | O app aberto num navegador em tamanho de celular, conversando com a API |

A cobertura de código da API é de **93%** (relatório completo no resumo de cada execução do workflow). O pipeline também audita as dependências (`pip-audit` e `npm audit`) e gera o APK (workflow [Gerar APK](.github/workflows/apk.yml)).

## Como rodar no computador

**API** (em SQLite, ou no PostgreSQL com `TEST_DATABASE_URL`):
```bash
cd api
pip install -r requirements-dev.txt
pytest -v --cov=app
```

**Telas do app:** suba a API com os dados de exemplo, compile o app e rode os testes.
```bash
cd api && DATABASE_URL=sqlite:///./e2e.db SEED_DEMO=true uvicorn app.main:app --port 8000
cd app && VITE_API_URL=http://localhost:8000 npx vite build && npx vite preview --port 4173
pip install pytest playwright && python -m playwright install chromium
pytest app/e2e -v
```

## Casos de teste por critério da avaliação

| Critério | Casos de teste |
|---|---|
| **1. Autenticação** | Tela de login com e-mail, senha, Entrar e logo · login errado mostra aviso · sessão continua depois de recarregar · Sair volta a visitante · tela protegida pede login e volta para ela · token falso, vencido ou sem assinatura é recusado · bloqueio após 5 senhas erradas |
| **2. Listagem de eventos** | Lista mostra os 4 eventos com nome, data, preço, categoria e imagem · busca "corrida" deixa só a Corrida Noturna 5K · busca com injeção de SQL não vaza dados |
| **3. Mapa** | Pinos aparecem no mapa · tocar no pino abre o painel com nome, data, preço e "Ver detalhes" · "Ver detalhes" abre o evento · eventos de exemplo têm local com latitude e longitude |
| **4. Detalhes e cadastro/edição** | Detalhe completo com "Como chegar" · CRUD de eventos pela API com upload de imagem e leitura de volta idêntica · só o dono vê Editar/Excluir e consegue alterar (403 para os outros) · upload recusa arquivo disfarçado e acima de 5 MB |
| **5. Categorias e locais** | Lista de categorias · CRUD de categorias e locais · tocar no mapa preenche latitude e longitude · cor e coordenadas inválidas são recusadas · não exclui categoria/local em uso |
| **6. Perfil e logout** | Perfil mostra nome, e-mail e versão · Sair funciona |
| **7. API e integração** | Todas as telas acima rodam contra a API real com banco · testes da API passam no PostgreSQL 16 (o banco da produção) |
| **8. APK** | Workflow "Gerar APK" compila o APK de release a cada mudança no app e anexa à Release |

## Problema encontrado pelos testes de tela
Ao abrir o mapa direto pelo endereço (`/tabs/mapa`), o Leaflet iniciava antes de o estilo da tela carregar e o mapa ficava com 0 px de altura, com os pinos fora da área visível. Corrigido na versão 1.2 (posição e altura dos mapas definidas no próprio elemento).
