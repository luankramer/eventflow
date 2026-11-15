"""Dados de exemplo usados na apresentação (SEED_DEMO=true)."""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", f"sqlite:///{_tmp}/exemplo.db")
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_SERVICE_KEY"] = ""
os.environ.setdefault("JWT_SECRET", "chave-so-para-testes-" + "x" * 32)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import dados_exemplo  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    Base.metadata.drop_all(bind=engine)
    dados_exemplo.popular()
    dados_exemplo.popular()  # rodar duas vezes não pode duplicar nada
    with TestClient(app) as c:
        yield c


def test_exemplo_cria_tudo_uma_vez_so(client):
    assert len(client.get("/categorias").json()) == len(dados_exemplo.CATEGORIAS)
    assert len(client.get("/locais").json()) == len(dados_exemplo.LOCAIS)
    assert len(client.get("/eventos").json()) == len(dados_exemplo.EVENTOS)


def test_eventos_de_exemplo_tem_local_com_coordenadas_e_categoria_com_cor(client):
    for e in client.get("/eventos").json():
        assert e["local"]["latitude"] is not None and e["local"]["longitude"] is not None
        assert e["categoria"]["cor"].startswith("#")


def test_conta_de_teste_entra_e_e_dona_dos_eventos(client):
    r = client.post("/auth/login", json={"email": "teste@eventflow.com", "senha": "123456"})
    assert r.status_code == 200
    uid = r.json()["usuario"]["id"]
    assert all(e["criado_por_id"] == uid for e in client.get("/eventos").json())
