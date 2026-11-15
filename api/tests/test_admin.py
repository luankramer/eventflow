"""Área do administrador: moderação de eventos, denúncias, palavras proibidas, bloqueio
de usuários e eventos encerrados ("Indisponível")."""
import os
import tempfile
from datetime import date, timedelta

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", f"sqlite:///{_tmp}/admin.db")
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_SERVICE_KEY"] = ""
os.environ.setdefault("JWT_SECRET", "chave-so-para-testes-" + "x" * 32)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import config, main  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seguranca_login import limitador  # noqa: E402

SENHA_ADM = "senha-do-adm-para-testes"


@pytest.fixture(scope="module")
def client():
    Base.metadata.drop_all(bind=engine)
    config.ADMIN_SENHA = SENHA_ADM
    with TestClient(app) as c:  # ao subir, a API cria a conta ADM e a lista de palavras
        yield c
    config.ADMIN_SENHA = ""


@pytest.fixture(autouse=True)
def zera_limitador():
    limitador.limpar()


def _login(client, email, senha):
    r = client.post("/auth/login", json={"email": email, "senha": senha})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}, r.json()["usuario"]


def _conta(client, email):
    r = client.post("/auth/registro", json={"nome": email.split("@")[0].title(), "email": email, "senha": "segredo1"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}, r.json()["usuario"]["id"]


@pytest.fixture(scope="module")
def adm(client):
    h, usuario = _login(client, "admin@eventflow.com", SENHA_ADM)
    assert usuario["admin"] is True
    return h


@pytest.fixture(scope="module")
def maria(client):
    return _conta(client, "maria@teste.com")


@pytest.fixture(scope="module")
def joao(client):
    return _conta(client, "joao@teste.com")


@pytest.fixture(scope="module")
def base(client, maria):
    h = maria[0]
    cat = client.post("/categorias", headers=h, json={"nome": "Shows"}).json()
    loc = client.post("/locais", headers=h, json={"nome": "Arena", "latitude": -9.97, "longitude": -67.8}).json()
    return cat["id"], loc["id"]


def _evento(client, h, base, nome, descricao="Descrição completa do evento, com detalhes.", dias=10, imagem=True):
    corpo = {
        "nome": nome, "descricao": descricao, "data": str(date.today() + timedelta(days=dias)), "hora": "19:00",
        "preco": 0, "categoria_id": base[0], "local_id": base[1],
        "imagem_url": "https://exemplo.com/foto.png" if imagem else None,
    }
    r = client.post("/eventos", headers=h, json=corpo)
    assert r.status_code == 201, r.text
    return r.json()["id"]


# ---------- Conta ADM ----------
def test_conta_adm_criada_pela_variavel_de_ambiente(adm, client):
    assert client.get("/auth/me", headers=adm).json()["admin"] is True


def test_ninguem_cria_conta_comum_com_o_email_do_adm(client):
    r = client.post("/auth/registro", json={"nome": "Falso", "email": "ADMIN@eventflow.com", "senha": "segredo1"})
    assert r.status_code == 409


def test_trocar_a_senha_no_render_atualiza_a_conta(client):
    config.ADMIN_SENHA = "nova-senha-do-adm-123"
    main._garantir_admin()
    assert client.post("/auth/login", json={"email": "admin@eventflow.com", "senha": SENHA_ADM}).status_code == 401
    _login(client, "admin@eventflow.com", "nova-senha-do-adm-123")
    config.ADMIN_SENHA = SENHA_ADM
    main._garantir_admin()


def test_senha_do_adm_curta_e_recusada():
    config.ADMIN_SENHA = "curta"
    with pytest.raises(RuntimeError):
        main._garantir_admin()
    config.ADMIN_SENHA = SENHA_ADM


def test_usuario_comum_nao_acessa_a_area_adm(client, maria):
    for rota in ["/admin/resumo", "/admin/eventos", "/admin/usuarios", "/admin/palavras"]:
        assert client.get(rota, headers=maria[0]).status_code == 403
        assert client.get(rota).status_code == 401


# ---------- Filtro de diretrizes ----------
def test_filtro_encontra_palavras_proibidas_sem_acento_e_palavra_inteira(client, adm, maria, base):
    ruim = _evento(client, maria[0], base, "Festa com PIX ANTECIPADO", "Garanta já, pague no pix antecipado e ganhe brinde.")
    ok = _evento(client, maria[0], base, "Feira do Armazém", "Produtos do armazém da cidade, com degustação.")
    ids = {e["id"]: e for e in client.get("/admin/eventos", headers=adm, params={"filtro": "palavras"}).json()}
    assert ruim in ids and ok not in ids  # "arma" não marca "armazém"
    assert "pix antecipado" in ids[ruim]["problemas"][0]["detalhe"]


def test_filtro_encontra_cadastro_incompleto(client, adm, maria, base):
    sem_foto = _evento(client, maria[0], base, "Sem foto", imagem=False)
    curta = _evento(client, maria[0], base, "Descrição curta", descricao="Vem!")
    ids = [e["id"] for e in client.get("/admin/eventos", headers=adm, params={"filtro": "incompletos"}).json()]
    assert sem_foto in ids and curta in ids


def test_palavra_nova_na_lista_passa_a_marcar_eventos(client, adm, maria, base):
    eid = _evento(client, maria[0], base, "Rifa beneficente", "Rifa com prêmios para ajudar a escola do bairro.")
    assert eid not in [e["id"] for e in client.get("/admin/eventos", headers=adm, params={"filtro": "palavras"}).json()]
    r = client.post("/admin/palavras", headers=adm, json={"termo": "  Rifa "})
    assert r.status_code == 201 and r.json()["termo"] == "rifa"
    assert client.post("/admin/palavras", headers=adm, json={"termo": "rifa"}).status_code == 409
    assert eid in [e["id"] for e in client.get("/admin/eventos", headers=adm, params={"filtro": "palavras"}).json()]
    assert client.delete(f"/admin/palavras/{r.json()['id']}", headers=adm).status_code == 204
    assert eid not in [e["id"] for e in client.get("/admin/eventos", headers=adm, params={"filtro": "palavras"}).json()]


# ---------- Denúncias ----------
def test_denuncia_aparece_para_o_adm_e_pode_ser_descartada(client, adm, maria, joao, base):
    eid = _evento(client, maria[0], base, "Show suspeito")
    corpo = {"motivo": "Golpe ou fraude", "detalhe": "Pedem pagamento por fora."}
    assert client.post(f"/eventos/{eid}/denuncias", json=corpo).status_code == 401  # visitante
    assert client.post(f"/eventos/{eid}/denuncias", headers=maria[0], json=corpo).status_code == 400  # o próprio
    assert client.post(f"/eventos/{eid}/denuncias", headers=joao[0], json={"motivo": "Qualquer"}).status_code == 422
    assert client.post(f"/eventos/{eid}/denuncias", headers=joao[0], json=corpo).status_code == 201
    assert client.post(f"/eventos/{eid}/denuncias", headers=joao[0], json=corpo).status_code == 409  # uma por pessoa

    lista = client.get("/admin/eventos", headers=adm, params={"filtro": "denuncias"}).json()
    assert lista[0]["id"] == eid and lista[0]["total_denuncias"] == 1  # mais denunciados primeiro
    detalhes = client.get(f"/admin/eventos/{eid}/denuncias", headers=adm).json()
    assert detalhes[0]["motivo"] == "Golpe ou fraude" and detalhes[0]["usuario"]["email"] == "joao@teste.com"

    assert client.delete(f"/admin/eventos/{eid}/denuncias", headers=adm).status_code == 204
    assert eid not in [e["id"] for e in client.get("/admin/eventos", headers=adm, params={"filtro": "denuncias"}).json()]


# ---------- Ocultar e excluir ----------
def test_ocultar_tira_da_lista_publica_e_mostrar_devolve(client, adm, maria, base):
    eid = _evento(client, maria[0], base, "Evento para ocultar")
    r = client.put(f"/admin/eventos/{eid}/ocultar", headers=adm, json={"oculto": True})
    assert r.status_code == 200 and r.json()["oculto"] is True
    assert eid not in [e["id"] for e in client.get("/eventos").json()]
    assert client.get(f"/eventos/{eid}").status_code == 404
    assert eid in [e["id"] for e in client.get("/admin/eventos", headers=adm, params={"filtro": "ocultos"}).json()]
    client.put(f"/admin/eventos/{eid}/ocultar", headers=adm, json={"oculto": False})
    assert client.get(f"/eventos/{eid}").status_code == 200


def test_adm_exclui_evento_de_qualquer_pessoa(client, adm, maria, joao, base):
    eid = _evento(client, maria[0], base, "Evento da Maria")
    client.post(f"/eventos/{eid}/denuncias", headers=joao[0], json={"motivo": "Spam ou repetido"})
    assert client.delete(f"/eventos/{eid}", headers=joao[0]).status_code == 403
    assert client.delete(f"/admin/eventos/{eid}", headers=adm).status_code == 204  # apaga junto as denúncias
    assert client.get(f"/eventos/{eid}").status_code == 404
    eid2 = _evento(client, maria[0], base, "Outro da Maria")
    assert client.delete(f"/eventos/{eid2}", headers=adm).status_code == 204  # também pela rota normal


# ---------- Bloqueio de usuários ----------
def test_bloquear_usuario_impede_login_e_cadastro(client, adm, base):
    h, uid = _conta(client, "bloqueado@teste.com")
    r = client.put(f"/admin/usuarios/{uid}/bloqueio", headers=adm, json={"bloqueado": True})
    assert r.status_code == 200 and r.json()["bloqueado"] is True
    assert client.post("/auth/login", json={"email": "bloqueado@teste.com", "senha": "segredo1"}).status_code == 403
    assert client.post("/categorias", headers=h, json={"nome": "Nova"}).status_code == 403  # token antigo também
    assert client.post("/auth/login", json={"email": "bloqueado@teste.com", "senha": "errada"}).status_code == 401
    client.put(f"/admin/usuarios/{uid}/bloqueio", headers=adm, json={"bloqueado": False})
    _login(client, "bloqueado@teste.com", "segredo1")


def test_adm_nao_pode_ser_bloqueado(client, adm):
    usuarios = client.get("/admin/usuarios", headers=adm).json()
    admin = next(u for u in usuarios if u["admin"])
    assert usuarios[0]["admin"] is True  # ADM aparece primeiro
    assert client.put(f"/admin/usuarios/{admin['id']}/bloqueio", headers=adm, json={"bloqueado": True}).status_code == 400


def test_resumo_conta_os_problemas(client, adm):
    r = client.get("/admin/resumo", headers=adm).json()
    assert r["fora_das_diretrizes"] >= r["com_palavras"] >= 1
    assert r["incompletos"] >= 2 and r["usuarios"] >= 4


# ---------- Eventos encerrados ("Indisponível") ----------
def test_eventos_passados_ficam_encerrados_e_tem_filtro(client, maria, base):
    passado = _evento(client, maria[0], base, "Já aconteceu", dias=-3)
    futuro = _evento(client, maria[0], base, "Ainda vai acontecer", dias=3)
    todos = {e["id"]: e for e in client.get("/eventos").json()}
    assert todos[passado]["encerrado"] is True and todos[futuro]["encerrado"] is False
    proximos = [e["id"] for e in client.get("/eventos", params={"periodo": "proximos"}).json()]
    encerrados = [e["id"] for e in client.get("/eventos", params={"periodo": "encerrados"}).json()]
    assert futuro in proximos and passado not in proximos
    assert passado in encerrados and futuro not in encerrados
    assert client.get(f"/eventos/{passado}").json()["encerrado"] is True
    assert client.get("/eventos", params={"periodo": "ontem"}).status_code == 422
