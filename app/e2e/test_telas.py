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
# senha da conta ADM da API de teste (a mesma passada em ADMIN_SENHA ao subir a API)
SENHA_ADM = os.getenv("E2E_ADMIN_SENHA", "senha-adm-dos-testes")


def _post(rota, corpo, token=None):
    cab = {"Content-Type": "application/json"}
    if token:
        cab["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + rota, data=json.dumps(corpo).encode(), headers=cab)
    try:
        resposta = urllib.request.urlopen(req)
        return resposta.status, json.loads(resposta.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, None


def _token(email, senha):
    return _post("/auth/login", {"email": email, "senha": senha})[1]["access_token"]


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


# ---------- Eventos encerrados ----------
def test_encerrados_aparecem_como_indisponivel(pagina):
    pagina.goto(APP + "/tabs/eventos")
    expect(pagina.locator(".ingresso")).to_have_count(4)  # padrão: só os próximos
    expect(pagina.locator(".indisponivel")).to_have_count(0)
    pagina.locator(".periodo button", has_text="Encerrados").click()
    expect(pagina.locator(".ingresso")).to_have_count(1)
    expect(pagina.locator(".indisponivel")).to_contain_text("Indisponível")
    pagina.locator(".ingresso").first.click()
    expect(pagina.locator(".aviso-encerrado")).to_contain_text("indisponível")


# ---------- Denúncia e administração ----------
def test_usuario_denuncia_evento(pagina):
    _post("/auth/registro", {"nome": "Outra Pessoa", "email": "outra@teste.com", "senha": "segredo1"})
    entrar(pagina, "outra@teste.com", "segredo1")
    pagina.goto(APP + "/eventos/2")
    pagina.locator("ion-button.denunciar").click()
    pagina.locator("ion-action-sheet button", has_text="Golpe ou fraude").click()
    pagina.wait_for_function("[...document.querySelectorAll('ion-toast')].some(t => (t.message || '').startsWith('Denúncia enviada'))")


def test_usuario_comum_nao_abre_a_administracao(pagina):
    entrar(pagina)
    pagina.goto(APP + "/admin")
    pagina.wait_for_url(lambda u: u.endswith("/tabs/perfil"))
    expect(pagina.locator(".atalho-adm")).to_have_count(0)


def test_adm_ve_denunciados_oculta_e_mostra_evento(pagina):
    outra = _token("outra@teste.com", "segredo1") if _post("/auth/registro", {"nome": "Outra Pessoa", "email": "outra@teste.com", "senha": "segredo1"})[0] != 201 else None
    _post("/eventos/3/denuncias", {"motivo": "Informação falsa"}, outra or _token("outra@teste.com", "segredo1"))
    entrar(pagina, "admin@eventflow.com", SENHA_ADM)
    pagina.goto(APP + "/tabs/perfil")
    pagina.locator(".atalho-adm").click()
    pagina.wait_for_url(lambda u: u.endswith("/admin"))
    expect(pagina.locator(".numero.alerta strong")).not_to_have_text("0")

    pagina.locator(".filtros button", has_text="Denunciados").click()
    item = pagina.locator(".evento-adm").first
    expect(item.locator(".selo.denuncias")).to_be_visible()
    item.locator("ion-button", has_text="Denúncias").click()
    expect(item.locator(".denuncia").first).to_be_visible()

    nome = item.locator("h3").inner_text()
    item.locator("ion-button.botao-ocultar").click()
    pagina.wait_for_function("[...document.querySelectorAll('ion-toast')].some(t => t.message === 'Evento ocultado do app.')")
    with urllib.request.urlopen(API + "/eventos") as r:
        assert nome not in [e["nome"] for e in json.load(r)]

    pagina.locator(".filtros button", has_text="Ocultos").click()
    pagina.locator(".evento-adm", has_text=nome).locator("ion-button.botao-ocultar").click()
    pagina.wait_for_function("[...document.querySelectorAll('ion-toast')].some(t => t.message === 'Evento visível de novo no app.')")
    with urllib.request.urlopen(API + "/eventos") as r:
        assert nome in [e["nome"] for e in json.load(r)]


def test_adm_bloqueia_usuario_e_edita_palavras(pagina):
    _post("/auth/registro", {"nome": "Pessoa Bloqueada", "email": "bloq@teste.com", "senha": "segredo1"})
    entrar(pagina, "admin@eventflow.com", SENHA_ADM)
    pagina.goto(APP + "/admin")
    pagina.locator("ion-segment-button", has_text="Usuários").click()
    linha = pagina.locator("ion-item.usuario", has_text="bloq@teste.com")
    linha.locator("ion-toggle").click()
    expect(linha.locator(".selo", has_text="Bloqueado")).to_be_visible()
    assert _post("/auth/login", {"email": "bloq@teste.com", "senha": "segredo1"})[0] == 403
    linha.locator("ion-toggle").click()
    expect(linha.locator(".selo", has_text="Bloqueado")).to_have_count(0)
    assert _post("/auth/login", {"email": "bloq@teste.com", "senha": "segredo1"})[0] == 200

    pagina.locator("ion-segment-button", has_text="Palavras").click()
    pagina.locator(".nova-palavra input").fill("show clandestino")
    pagina.locator(".nova-palavra ion-button").click()
    chip = pagina.locator(".palavra", has_text="show clandestino")
    expect(chip).to_be_visible()
    chip.locator("button").click()
    expect(chip).to_have_count(0)
