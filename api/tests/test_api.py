import io
import os
import tempfile

# Banco temporário, configurado antes de importar o app.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", f"sqlite:///{_tmp}/teste.db")
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_SERVICE_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    # Começa sempre com o banco vazio. Por isso TEST_DATABASE_URL deve ser um banco
    # só para testes — nunca aponte para o banco do Supabase usado na apresentação.
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth(client):
    r = client.post("/auth/registro", json={"nome": "Luan", "email": "luan@teste.com", "senha": "segredo1"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["banco"] == "ok"


def test_rotas_protegidas_sem_token(client):
    for rota in ["/eventos", "/categorias", "/locais", "/auth/me"]:
        assert client.get(rota).status_code == 401
    assert client.get("/eventos", headers={"Authorization": "Bearer token-falso"}).status_code == 401


def test_login_logout_e_perfil(client, auth):
    assert client.post("/auth/login", json={"email": "luan@teste.com", "senha": "errada"}).status_code == 401
    r = client.post("/auth/login", json={"email": "LUAN@teste.com", "senha": "segredo1"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json() == {"id": me.json()["id"], "nome": "Luan", "email": "luan@teste.com"}
    assert client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"}).status_code == 204
    assert client.post("/auth/registro", json={"nome": "X", "email": "luan@teste.com", "senha": "123456"}).status_code in (409, 422)


def test_fluxo_completo(client, auth):
    # Categoria: criar, editar, nome duplicado
    cat = client.post("/categorias", json={"nome": "Show"}, headers=auth).json()
    r = client.put(f"/categorias/{cat['id']}", json={"nome": "Música", "descricao": "Shows", "cor": "#e8175d", "icone": "musica"}, headers=auth)
    assert r.status_code == 200 and r.json()["nome"] == "Música"
    assert r.json()["cor"] == "#E8175D" and r.json()["icone"] == "musica"
    assert client.post("/categorias", json={"nome": "Cor ruim", "cor": "vermelho"}, headers=auth).status_code == 422
    assert client.post("/categorias", json={"nome": "música"}, headers=auth).status_code == 409

    # Local: validação de coordenadas, criar, editar
    assert client.post("/locais", json={"nome": "Errado", "latitude": 200, "longitude": 0}, headers=auth).status_code == 422
    loc = client.post("/locais", json={"nome": "Gameleira", "latitude": -9.9696, "longitude": -67.8094}, headers=auth).json()
    r = client.put(f"/locais/{loc['id']}", json={"nome": "Gameleira", "latitude": -9.97, "longitude": -67.81, "endereco": "Centro"}, headers=auth)
    assert r.json()["endereco"] == "Centro"

    # Upload de imagem (salvamento local, sem Supabase)
    png = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 100)
    up = client.post("/upload", files={"arquivo": ("foto.png", png, "image/png")}, headers=auth)
    assert up.status_code == 200, up.text
    url = up.json()["url"]
    assert "/imagens/" in url and url.endswith(".png")
    img = client.get(url.replace("http://testserver", ""))  # pública: sem token
    assert img.status_code == 200 and img.headers["content-type"] == "image/png"
    assert img.content == b"\x89PNG\r\n\x1a\n" + b"0" * 100
    assert client.get("/imagens/naoexiste.png").status_code == 404
    assert client.post("/upload", files={"arquivo": ("a.txt", io.BytesIO(b"oi"), "text/plain")}, headers=auth).status_code == 400

    # Evento: relações inválidas, criar, editar, buscar
    base = {"nome": "Festival", "descricao": "Bandas locais", "data": "2026-12-10", "hora": "19:30",
            "preco": 25.5, "categoria_id": cat["id"], "local_id": loc["id"], "imagem_url": url}
    assert client.post("/eventos", json={**base, "local_id": 999}, headers=auth).status_code == 400
    ev = client.post("/eventos", json=base, headers=auth)
    assert ev.status_code == 201, ev.text
    ev = ev.json()
    assert ev["preco"] == 25.5 and ev["categoria"]["nome"] == "Música" and ev["categoria"]["cor"] == "#E8175D"
    assert ev["local"]["latitude"] == -9.97 and ev["hora"] == "19:30:00"

    r = client.put(f"/eventos/{ev['id']}", json={**base, "nome": "Festival de Verão", "preco": 0}, headers=auth)
    assert r.status_code == 200 and r.json()["nome"] == "Festival de Verão" and r.json()["preco"] == 0

    assert len(client.get("/eventos?busca=verão", headers=auth).json()) == 1
    assert len(client.get("/eventos?busca=música", headers=auth).json()) == 1  # busca pela categoria
    assert len(client.get("/eventos?busca=gamel", headers=auth).json()) == 1   # busca pelo local
    assert client.get("/eventos?busca=inexistente", headers=auth).json() == []
    assert client.get(f"/eventos/{ev['id']}", headers=auth).json()["descricao"] == "Bandas locais"

    # Não pode excluir categoria/local em uso; depois de excluir o evento, pode
    assert client.delete(f"/categorias/{cat['id']}", headers=auth).status_code == 409
    assert client.delete(f"/locais/{loc['id']}", headers=auth).status_code == 409
    assert client.delete(f"/eventos/{ev['id']}", headers=auth).status_code == 204
    assert client.get(f"/eventos/{ev['id']}", headers=auth).status_code == 404
    assert client.delete(f"/categorias/{cat['id']}", headers=auth).status_code == 204
    assert client.delete(f"/locais/{loc['id']}", headers=auth).status_code == 204
