"""Testes de ponta a ponta das telas do EventFlow (navegador Chromium em tamanho de celular).

Precisam da API rodando com os dados de exemplo e do app compilado:
    API_URL=http://localhost:8000  APP_URL=http://localhost:4173  pytest app/e2e
O GitHub Actions faz isso sozinho no workflow "Testes".
"""
import json
import os
import urllib.request

import pytest
from playwright.sync_api import expect, sync_playwright

API = os.getenv("API_URL", "http://localhost:8000")
APP = os.getenv("APP_URL", "http://localhost:4173")


def _post(rota, corpo):
    req = urllib.request.Request(API + rota, data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json"})
    try:
        return urllib.request.urlopen(req).status
    except urllib.error.HTTPError as e:
        return e.code


@pytest.fixture(scope="session")
def navegador():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.getenv("CHROME_PATH") or None, args=["--no-sandbox"])
        yield b
        b.close()


@pytest.fixture
def pagina(navegador):
    ctx = navegador.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    yield pg
    ctx.close()
    assert not erros, erros


def entrar(pg, email="teste@eventflow.com", senha="123456"):
    pg.goto(APP + "/login")
    pg.locator("ion-input").nth(0).locator("input").fill(email)
    pg.locator("ion-input").nth(1).locator("input").fill(senha)
    pg.locator("form ion-button.botao-grande").click()
    pg.wait_for_url(lambda u: "/login" not in u)


# ---------- Autenticação ----------
def test_tela_de_login_tem_email_senha_entrar_e_logo(pagina):
    pagina.goto(APP + "/login")
    expect(pagina.locator(".marca-ef")).to_be_visible()
    expect(pagina.locator("ion-input")).to_have_count(2)
    expect(pagina.locator("form ion-button.botao-grande")).to_contain_text("Entrar")


def test_login_errado_mostra_aviso(pagina):
    pagina.goto(APP + "/login")
    pagina.locator("ion-input").nth(0).locator("input").fill("ninguem@eventflow.com")
    pagina.locator("ion-input").nth(1).locator("input").fill("errada")
    pagina.locator("form ion-button.botao-grande").click()
    # o Ionic guarda o texto do aviso na propriedade "message" do <ion-toast>
    pagina.wait_for_function("[...document.querySelectorAll('ion-toast')].some(t => t.message === 'E-mail ou senha incorretos.')")


def test_sessao_continua_depois_de_recarregar_e_sair_funciona(pagina):
    entrar(pagina)
    pagina.reload()
    pagina.goto(APP + "/tabs/perfil")
    expect(pagina.locator(".perfil h1")).to_have_text("Usuário Teste")
    pagina.locator("ion-button", has_text="Sair").click()
    pagina.locator("ion-alert button", has_text="Sair").click()
    pagina.wait_for_url(lambda u: "/login" in u)
    pagina.goto(APP + "/tabs/perfil")
    expect(pagina.locator(".convite")).to_be_visible()  # voltou a ser visitante


def test_tela_protegida_pede_login_e_volta_para_ela(pagina):
    pagina.goto(APP + "/tabs/cadastros")
    pagina.wait_for_url(lambda u: "/login?voltar=" in u)
    pagina.locator("ion-input").nth(0).locator("input").fill("teste@eventflow.com")
    pagina.locator("ion-input").nth(1).locator("input").fill("123456")
    pagina.locator("form ion-button.botao-grande").click()
    pagina.wait_for_url(lambda u: u.split("?")[0].endswith("/tabs/cadastros"))


# ---------- Eventos ----------
def test_lista_mostra_nome_data_preco_categoria_e_imagem(pagina):
    pagina.goto(APP + "/")
    pagina.wait_for_url(lambda u: u.endswith("/tabs/eventos"))
    cartao = pagina.locator(".ingresso").first
    expect(cartao).to_be_visible()
    expect(pagina.locator(".ingresso")).to_have_count(4)
    texto = cartao.inner_text()
    assert "Gratuito" in texto or "R$" in texto


def test_busca_filtra_a_lista(pagina):
    pagina.goto(APP + "/tabs/eventos")
    expect(pagina.locator(".ingresso")).to_have_count(4)
    pagina.locator("ion-searchbar input").fill("corrida")
    expect(pagina.locator(".ingresso")).to_have_count(1)
    expect(pagina.locator(".ingresso").first).to_contain_text("Corrida Noturna 5K")


def test_mapa_mostra_pinos_e_ver_detalhes(pagina):
    pagina.goto(APP + "/tabs/mapa")
    pinos = pagina.locator(".pino")
    expect(pinos.first).to_be_visible(timeout=15000)
    pinos.first.click()
    painel = pagina.locator(".painel")
    expect(painel).to_be_visible()
    expect(painel.locator(".item-evento").first).to_contain_text("Ver detalhes")
    painel.locator(".item-evento").first.click()
    pagina.wait_for_url(lambda u: "/eventos/" in u)
    expect(pagina.locator(".detalhe h1")).to_be_visible()


def test_detalhe_tem_como_chegar_e_visitante_nao_edita(pagina):
    pagina.goto(APP + "/eventos/1")
    expect(pagina.locator(".detalhe h1")).to_be_visible()
    assert "google.com/maps/dir" in pagina.locator("a.como-chegar").get_attribute("href")
    expect(pagina.locator("ion-button.editar")).to_have_count(0)


def test_so_o_dono_ve_editar_e_excluir(pagina):
    _post("/auth/registro", {"nome": "Outra Pessoa", "email": "outra@teste.com", "senha": "segredo1"})
    entrar(pagina, "outra@teste.com", "segredo1")
    pagina.goto(APP + "/eventos/1")
    expect(pagina.locator(".detalhe h1")).to_be_visible()
    expect(pagina.locator("ion-button.editar")).to_have_count(0)
    pagina.goto(APP + "/eventos/1/editar")
    pagina.wait_for_url(lambda u: u.endswith("/eventos/1"))  # o formulário devolve para os detalhes

    pagina.evaluate("localStorage.clear()")
    entrar(pagina)
    pagina.goto(APP + "/eventos/1")
    expect(pagina.locator("ion-button.editar")).to_have_count(1)
    expect(pagina.locator("ion-button.excluir")).to_have_count(1)


# ---------- Locais e categorias ----------
def test_cadastro_de_local_preenche_coordenadas_ao_tocar_no_mapa(pagina):
    entrar(pagina)
    pagina.goto(APP + "/locais/novo")
    mapa = pagina.locator(".mapa-seletor")
    expect(mapa).to_be_visible()
    pagina.wait_for_timeout(800)
    mapa.click(position={"x": 200, "y": 110})
    expect(pagina.locator("#lat input")).not_to_have_value("")
    expect(pagina.locator("#lng input")).not_to_have_value("")


def test_lista_de_categorias_mostra_as_do_exemplo(pagina):
    entrar(pagina)
    pagina.goto(APP + "/categorias")
    for nome in ["Música", "Gastronomia", "Esporte", "Cultura", "Tecnologia"]:
        expect(pagina.get_by_text(nome, exact=True).first).to_be_visible()


# ---------- Perfil ----------
def test_perfil_mostra_dados_e_versao(pagina):
    entrar(pagina)
    pagina.goto(APP + "/tabs/perfil")
    expect(pagina.locator(".perfil h1")).to_have_text("Usuário Teste")
    expect(pagina.get_by_text("teste@eventflow.com").first).to_be_visible()
    expect(pagina.locator(".rodape").get_by_text("Versão")).to_be_visible()
