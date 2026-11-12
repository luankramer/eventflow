"""Testes de segurança da API do EventFlow.

Cada teste simula um ataque comum contra a API rodando localmente (banco temporário)
e confere que ela se defende. Rodar: `pytest tests/test_seguranca.py -v`.
"""
import io
import os
import tempfile
from datetime import datetime, timedelta, timezone

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", f"sqlite:///{_tmp}/seguranca.db")
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_SERVICE_KEY"] = ""
os.environ.setdefault("JWT_SECRET", "chave-so-para-testes-" + "x" * 32)

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import config  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seguranca_login import limitador  # noqa: E402

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture(scope="module")
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:
        yield c


def _conta(client, email):
    r = client.post("/auth/registro", json={"nome": "Pessoa", "email": email, "senha": "segredo1"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}, r.json()["usuario"]["id"]


@pytest.fixture(scope="module")
def ana(client):
    return _conta(client, "ana@teste.com")


@pytest.fixture(scope="module")
def beto(client):
    return _conta(client, "beto@teste.com")


@pytest.fixture(scope="module")
def evento_da_ana(client, ana):
    h, _ = ana
    cat = client.post("/categorias", json={"nome": "Música"}, headers=h).json()
    loc = client.post("/locais", json={"nome": "Praça", "latitude": -9.97, "longitude": -67.81}, headers=h).json()
    r = client.post("/eventos", headers=h, json={
        "nome": "Show da Ana", "data": "2030-01-10", "hora": "20:00", "preco": 10,
        "categoria_id": cat["id"], "local_id": loc["id"],
    })
    assert r.status_code == 201, r.text
    return r.json(), cat, loc


@pytest.fixture(autouse=True)
def zera_limitador():
    limitador.limpar()
    yield
    limitador.limpar()


# ---------- 1. Token JWT ----------
def test_token_assinado_com_outra_chave_e_recusado(client, ana):
    _, uid = ana
    falso = jwt.encode({"sub": str(uid), "exp": datetime.now(timezone.utc) + timedelta(days=1)}, "chave-do-atacante", algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_sem_assinatura_alg_none_e_recusado(client, ana):
    _, uid = ana
    sem_assinatura = jwt.encode({"sub": str(uid)}, None, algorithm="none")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {sem_assinatura}"}).status_code == 401


def test_token_expirado_e_recusado(client, ana):
    _, uid = ana
    vencido = jwt.encode({"sub": str(uid), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, config.JWT_SECRET, algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {vencido}"}).status_code == 401


def test_token_sem_validade_e_recusado(client, ana):
    _, uid = ana
    eterno = jwt.encode({"sub": str(uid)}, config.JWT_SECRET, algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {eterno}"}).status_code == 401


def test_token_de_usuario_inexistente_e_recusado(client):
    t = jwt.encode({"sub": "999999", "exp": datetime.now(timezone.utc) + timedelta(days=1)}, config.JWT_SECRET, algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {t}"}).status_code == 401


# ---------- 2. Senhas e login ----------
def test_senha_e_guardada_com_hash_bcrypt(client, ana):
    from app.database import SessionLocal
    from app.models import Usuario

    with SessionLocal() as db:
        u = db.get(Usuario, ana[1])
        assert u.senha_hash.startswith("$2b$") and "segredo1" not in u.senha_hash


def test_resposta_nunca_devolve_hash_da_senha(client, ana):
    corpo = client.get("/auth/me", headers=ana[0]).text
    assert "senha" not in corpo and "$2b$" not in corpo


def test_senha_com_mais_de_72_bytes_e_recusada_sem_erro_500(client):
    # 40 letras "é" = 80 bytes: passa no limite de caracteres, mas estoura o limite do bcrypt.
    r = client.post("/auth/registro", json={"nome": "Longa", "email": "longa@teste.com", "senha": "é" * 40})
    assert r.status_code == 422


def test_login_com_senha_gigante_nao_derruba_a_api(client, ana):
    r = client.post("/auth/login", json={"email": "ana@teste.com", "senha": "x" * 5000})
    assert r.status_code in (401, 422)


def test_login_errado_nao_revela_se_o_email_existe(client, ana):
    existe = client.post("/auth/login", json={"email": "ana@teste.com", "senha": "errada"})
    nao_existe = client.post("/auth/login", json={"email": "ninguem@teste.com", "senha": "errada"})
    assert existe.status_code == nao_existe.status_code == 401
    assert existe.json() == nao_existe.json()


def test_forca_bruta_no_login_e_bloqueada(client, ana):
    codigos = [client.post("/auth/login", json={"email": "ana@teste.com", "senha": f"chute{i}"}).status_code for i in range(12)]
    assert 429 in codigos, codigos
    # mesmo a senha certa fica bloqueada até o tempo de espera passar
    certa = client.post("/auth/login", json={"email": "ana@teste.com", "senha": "segredo1"})
    assert certa.status_code == 429
    assert "Retry-After" in certa.headers


# ---------- 3. Autorização (um usuário não mexe no evento do outro) ----------
def test_outro_usuario_nao_edita_evento_alheio(client, beto, evento_da_ana):
    evento, cat, loc = evento_da_ana
    r = client.put(f"/eventos/{evento['id']}", headers=beto[0], json={
        "nome": "Hackeado", "data": "2030-01-10", "hora": "20:00", "preco": 0,
        "categoria_id": cat["id"], "local_id": loc["id"],
    })
    assert r.status_code == 403
    assert client.get(f"/eventos/{evento['id']}").json()["nome"] == "Show da Ana"


def test_outro_usuario_nao_exclui_evento_alheio(client, beto, evento_da_ana):
    evento, _, _ = evento_da_ana
    assert client.delete(f"/eventos/{evento['id']}", headers=beto[0]).status_code == 403
    assert client.get(f"/eventos/{evento['id']}").status_code == 200


def test_campos_extras_nao_trocam_o_dono_do_evento(client, ana, beto, evento_da_ana):
    _, cat, loc = evento_da_ana
    r = client.post("/eventos", headers=beto[0], json={
        "nome": "Do Beto", "data": "2030-02-01", "hora": "10:00", "preco": 0,
        "categoria_id": cat["id"], "local_id": loc["id"], "criado_por_id": ana[1], "id": 1,
    })
    assert r.status_code == 201
    # a Ana não consegue apagar, porque o dono continua sendo o Beto
    assert client.delete(f"/eventos/{r.json()['id']}", headers=ana[0]).status_code == 403


# ---------- 4. Injeção de SQL ----------
@pytest.mark.parametrize("ataque", ["' OR '1'='1", "%' OR 1=1 --", "'; DROP TABLE eventos; --", "\\", "%_%"])
def test_busca_com_injecao_de_sql_nao_vaza_dados(client, evento_da_ana, ataque):
    r = client.get("/eventos", params={"busca": ataque})
    assert r.status_code == 200
    assert r.json() == []
    assert client.get("/eventos").status_code == 200  # tabela continua lá


def test_filtro_numerico_rejeita_texto_malicioso(client):
    assert client.get("/eventos", params={"categoria_id": "1 OR 1=1"}).status_code == 422


def test_ids_absurdos_nao_derrubam_a_api(client):
    for rota in ["/eventos/99999999999999999999", "/eventos/-1", "/categorias/99999999999999999999", "/locais/0"]:
        assert client.get(rota).status_code in (404, 422), rota


# ---------- 5. Upload de imagens ----------
def test_arquivo_html_disfarcado_de_png_e_recusado(client, ana):
    falso = b"<html><script>alert(document.cookie)</script></html>"
    r = client.post("/upload", headers=ana[0], files={"arquivo": ("foto.png", io.BytesIO(falso), "image/png")})
    assert r.status_code == 400


def test_svg_nao_e_aceito_como_imagem(client, ana):
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>'
    r = client.post("/upload", headers=ana[0], files={"arquivo": ("x.svg", io.BytesIO(svg), "image/svg+xml")})
    assert r.status_code == 400


def test_imagem_grande_demais_e_recusada(client, ana):
    grande = PNG + b"\0" * (config.UPLOAD_MAX_MB * 1024 * 1024 + 1)
    r = client.post("/upload", headers=ana[0], files={"arquivo": ("g.png", io.BytesIO(grande), "image/png")})
    assert r.status_code == 413


def test_imagem_servida_com_protecao_contra_sniffing(client, ana):
    r = client.post("/upload", headers=ana[0], files={"arquivo": ("ok.png", io.BytesIO(PNG), "image/png")})
    assert r.status_code == 200, r.text
    nome = r.json()["url"].rsplit("/", 1)[1]
    img = client.get(f"/imagens/{nome}")
    assert img.headers["content-type"] == "image/png"
    assert img.headers.get("x-content-type-options") == "nosniff"


def test_caminho_de_arquivo_nao_escapa_da_pasta(client):
    for nome in ["..%2F..%2Fetc%2Fpasswd", "....//etc/passwd", "%00.png"]:
        assert client.get(f"/imagens/{nome}").status_code == 404


# ---------- 6. Dados de entrada ----------
def test_html_no_nome_do_evento_volta_como_texto_puro(client, ana, evento_da_ana):
    _, cat, loc = evento_da_ana
    xss = "<img src=x onerror=alert(1)>"
    r = client.post("/eventos", headers=ana[0], json={
        "nome": xss, "data": "2030-03-01", "hora": "10:00", "preco": 0, "categoria_id": cat["id"], "local_id": loc["id"],
    })
    assert r.status_code == 201
    assert r.headers["content-type"].startswith("application/json")
    assert r.json()["nome"] == xss  # guardado como texto; o app (Vue) mostra escapado


def test_link_de_imagem_so_aceita_http(client, ana, evento_da_ana):
    _, cat, loc = evento_da_ana
    r = client.post("/eventos", headers=ana[0], json={
        "nome": "Link estranho", "data": "2030-03-01", "hora": "10:00", "preco": 0,
        "categoria_id": cat["id"], "local_id": loc["id"], "imagem_url": "javascript:alert(1)",
    })
    assert r.status_code == 422


def test_descricao_gigante_e_recusada(client, ana, evento_da_ana):
    _, cat, loc = evento_da_ana
    r = client.post("/eventos", headers=ana[0], json={
        "nome": "Texto enorme", "descricao": "a" * 200_000, "data": "2030-03-01", "hora": "10:00", "preco": 0,
        "categoria_id": cat["id"], "local_id": loc["id"],
    })
    assert r.status_code == 422


def test_cor_da_categoria_nao_aceita_codigo(client, ana):
    r = client.post("/categorias", headers=ana[0], json={"nome": "Ataque", "cor": "red;background:url(//x)"})
    assert r.status_code == 422


def test_preco_negativo_e_coordenada_invalida_sao_recusados(client, ana, evento_da_ana):
    _, cat, loc = evento_da_ana
    assert client.post("/locais", headers=ana[0], json={"nome": "Fora", "latitude": 91, "longitude": 0}).status_code == 422
    assert client.post("/eventos", headers=ana[0], json={
        "nome": "Negativo", "data": "2030-03-01", "hora": "10:00", "preco": -5, "categoria_id": cat["id"], "local_id": loc["id"],
    }).status_code == 422


# ---------- 7. Configuração ----------
def test_cabecalhos_de_seguranca_nas_respostas(client):
    r = client.get("/health")
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert r.headers.get("x-frame-options") == "DENY"
    assert r.headers.get("referrer-policy") == "no-referrer"


def test_erros_nao_mostram_detalhes_internos(client):
    r = client.post("/auth/login", content=b"{json quebrado", headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert "Traceback" not in r.text and "sqlalchemy" not in r.text.lower()


def test_producao_nao_sobe_com_chave_jwt_padrao():
    assert config.chave_jwt_insegura("postgresql+psycopg://u:p@h/db", config.CHAVE_JWT_PADRAO)
    assert config.chave_jwt_insegura("postgresql+psycopg://u:p@h/db", "curta")
    assert not config.chave_jwt_insegura("postgresql+psycopg://u:p@h/db", "x" * 40)
    assert not config.chave_jwt_insegura("sqlite:///./local.db", config.CHAVE_JWT_PADRAO)  # desenvolvimento ok
