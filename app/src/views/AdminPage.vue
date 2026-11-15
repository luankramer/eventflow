<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start"><ion-back-button default-href="/tabs/perfil" text="" /></ion-buttons>
        <ion-title>Administração</ion-title>
      </ion-toolbar>
      <ion-toolbar class="abas">
        <ion-segment v-model="aba" @ionChange="carregarAba">
          <ion-segment-button value="eventos"><ion-label>Eventos</ion-label></ion-segment-button>
          <ion-segment-button value="usuarios"><ion-label>Usuários</ion-label></ion-segment-button>
          <ion-segment-button value="palavras"><ion-label>Palavras</ion-label></ion-segment-button>
        </ion-segment>
      </ion-toolbar>
    </ion-header>

    <ion-content>
      <ion-refresher slot="fixed" @ionRefresh="atualizar"><ion-refresher-content /></ion-refresher>

      <!-- Resumo da moderação -->
      <div v-if="resumo" class="resumo">
        <button type="button" class="numero alerta" @click="escolherFiltro('fora')">
          <strong>{{ resumo.fora_das_diretrizes }}</strong><span>fora das diretrizes</span>
        </button>
        <button type="button" class="numero" @click="escolherFiltro('denuncias')">
          <strong>{{ resumo.denunciados }}</strong><span>denunciados</span>
        </button>
        <button type="button" class="numero" @click="escolherFiltro('ocultos')">
          <strong>{{ resumo.ocultos }}</strong><span>ocultos</span>
        </button>
        <button type="button" class="numero" @click="aba = 'usuarios'; carregarAba()">
          <strong>{{ resumo.usuarios_bloqueados }}</strong><span>bloqueados</span>
        </button>
      </div>

      <!-- ===================== EVENTOS ===================== -->
      <section v-if="aba === 'eventos'">
        <div class="filtros">
          <button v-for="f in FILTROS" :key="f.valor" type="button" :class="{ ativo: filtro === f.valor }" @click="escolherFiltro(f.valor)">
            <ion-icon :icon="f.icone" /> {{ f.nome }}
          </button>
        </div>
        <ion-searchbar v-model="busca" placeholder="Buscar por evento ou autor" :debounce="350" @ionInput="carregarEventos" @ionClear="carregarEventos" />

        <div v-if="carregando && !eventos.length" class="centro"><ion-spinner name="crescent" /></div>

        <article v-for="e in eventos" :key="e.id" class="evento-adm cartao" :class="{ oculto: e.oculto }">
          <div class="evento-adm-topo">
            <div class="capa"><CapaEvento :evento="e" tamanho-icone="22px" /></div>
            <div class="info">
              <h3>{{ e.nome }}</h3>
              <p>{{ formatarData(e.data) }} · {{ e.criado_por ? e.criado_por.nome : 'sem autor' }}</p>
              <div class="selos">
                <span v-if="e.oculto" class="selo cinza"><ion-icon :icon="eyeOffOutline" /> Oculto</span>
                <span v-if="e.encerrado" class="selo cinza">Encerrado</span>
                <span v-for="p in e.problemas" :key="p.tipo" class="selo" :class="p.tipo">
                  <ion-icon :icon="ICONE_PROBLEMA[p.tipo]" /> {{ NOME_PROBLEMA[p.tipo] }}
                </span>
                <span v-if="!e.problemas.length && !e.oculto" class="selo ok"><ion-icon :icon="checkmarkCircleOutline" /> Dentro das diretrizes</span>
              </div>
            </div>
          </div>

          <ul v-if="e.problemas.length" class="motivos">
            <li v-for="p in e.problemas" :key="p.tipo">{{ p.detalhe }}</li>
          </ul>

          <div v-if="aberto === e.id" class="denuncias">
            <div v-if="!denuncias.length" class="vazio-pequeno">Carregando…</div>
            <div v-for="d in denuncias" :key="d.id" class="denuncia">
              <strong>{{ d.motivo }}</strong>
              <span>{{ d.usuario.nome }} · {{ d.usuario.email }}</span>
              <p v-if="d.detalhe">{{ d.detalhe }}</p>
            </div>
            <ion-button size="small" fill="clear" color="medium" @click="descartar(e)">
              <ion-icon slot="start" :icon="checkmarkDoneOutline" /> Evento ok: descartar denúncias
            </ion-button>
          </div>

          <div class="acoes">
            <ion-button v-if="e.total_denuncias" size="small" fill="clear" @click="verDenuncias(e)">
              <ion-icon slot="start" :icon="flagOutline" /> Denúncias ({{ e.total_denuncias }})
            </ion-button>
            <ion-button v-if="!e.oculto" size="small" fill="clear" color="medium" :router-link="`/eventos/${e.id}`">
              <ion-icon slot="start" :icon="openOutline" /> Ver
            </ion-button>
            <ion-button size="small" fill="clear" color="medium" class="botao-ocultar" @click="alternarOculto(e)">
              <ion-icon slot="start" :icon="e.oculto ? eyeOutline : eyeOffOutline" /> {{ e.oculto ? 'Mostrar' : 'Ocultar' }}
            </ion-button>
            <ion-button size="small" fill="clear" color="danger" class="botao-excluir" @click="excluir(e)">
              <ion-icon slot="start" :icon="trashOutline" /> Excluir
            </ion-button>
          </div>
        </article>

        <div v-if="!carregando && !eventos.length" class="vazio">
          <div class="vazio-icone"><ion-icon :icon="shieldCheckmarkOutline" /></div>
          <h3>Nada por aqui</h3>
          <p>{{ filtro === 'fora' ? 'Todos os eventos estão dentro das diretrizes.' : 'Nenhum evento neste filtro.' }}</p>
        </div>
      </section>

      <!-- ===================== USUÁRIOS ===================== -->
      <section v-if="aba === 'usuarios'">
        <p class="dica">Usuário bloqueado não consegue entrar nem cadastrar nada. Os eventos dele continuam até você decidir.</p>
        <ion-list class="lista-cartao" lines="full">
          <ion-item v-for="u in usuarios" :key="u.id" class="usuario">
            <div slot="start" class="avatar" :class="{ adm: u.admin, bloqueado: u.bloqueado }">{{ iniciais(u.nome) }}</div>
            <ion-label>
              <h3>{{ u.nome }} <span v-if="u.admin" class="selo adm">ADM</span><span v-if="u.bloqueado" class="selo palavras">Bloqueado</span></h3>
              <p>{{ u.email }}</p>
              <p>{{ u.total_eventos }} evento(s)</p>
            </ion-label>
            <ion-toggle
              v-if="!u.admin"
              slot="end"
              :checked="u.bloqueado"
              color="danger"
              :aria-label="`Bloquear ${u.nome}`"
              @ionChange="bloquear(u, $event.detail.checked)"
            >Bloquear</ion-toggle>
          </ion-item>
        </ion-list>
      </section>

      <!-- ===================== PALAVRAS ===================== -->
      <section v-if="aba === 'palavras'">
        <p class="dica">Eventos com estas palavras no nome ou na descrição aparecem em "Fora das diretrizes". Acentos e maiúsculas não importam.</p>
        <form class="nova-palavra cartao" @submit.prevent="adicionarPalavra">
          <ion-input v-model="novaPalavra" placeholder="Nova palavra ou expressão" :maxlength="60" aria-label="Nova palavra" />
          <ion-button type="submit" :disabled="(novaPalavra || '').trim().length < 2">
            <ion-icon slot="start" :icon="add" /> Adicionar
          </ion-button>
        </form>
        <div class="palavras">
          <span v-for="p in palavras" :key="p.id" class="palavra">
            {{ p.termo }}
            <button type="button" :aria-label="`Remover ${p.termo}`" @click="removerPalavra(p)"><ion-icon :icon="close" /></button>
          </span>
        </div>
      </section>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import {
  IonBackButton, IonButton, IonButtons, IonContent, IonHeader, IonIcon, IonInput, IonItem, IonLabel, IonList,
  IonPage, IonRefresher, IonRefresherContent, IonSearchbar, IonSegment, IonSegmentButton, IonSpinner, IonTitle,
  IonToggle, IonToolbar, onIonViewWillEnter,
} from '@ionic/vue'
import {
  add, alertCircleOutline, chatbubblesOutline, checkmarkCircleOutline, checkmarkDoneOutline, close, documentTextOutline,
  eyeOffOutline, eyeOutline, flagOutline, listOutline, openOutline, shieldCheckmarkOutline, textOutline, trashOutline,
} from 'ionicons/icons'
import CapaEvento from '@/components/CapaEvento.vue'
import { api } from '@/services/api'
import { avisarErro, avisarSucesso, confirmar } from '@/services/avisos'
import { formatarData, iniciais } from '@/services/formato'

const FILTROS = [
  { valor: 'fora', nome: 'Fora das diretrizes', icone: alertCircleOutline },
  { valor: 'denuncias', nome: 'Denunciados', icone: flagOutline },
  { valor: 'palavras', nome: 'Palavras proibidas', icone: textOutline },
  { valor: 'incompletos', nome: 'Incompletos', icone: documentTextOutline },
  { valor: 'ocultos', nome: 'Ocultos', icone: eyeOffOutline },
  { valor: 'todos', nome: 'Todos', icone: listOutline },
]
const NOME_PROBLEMA = { palavras: 'Palavras proibidas', denuncias: 'Denunciado', incompleto: 'Incompleto' }
const ICONE_PROBLEMA = { palavras: textOutline, denuncias: chatbubblesOutline, incompleto: documentTextOutline }

const aba = ref('eventos')
const filtro = ref('fora')
const busca = ref('')
const resumo = ref(null)
const eventos = ref([])
const usuarios = ref([])
const palavras = ref([])
const novaPalavra = ref('')
const carregando = ref(true)
const aberto = ref(null)
const denuncias = ref([])

async function carregarResumo() {
  try {
    resumo.value = await api.admin.resumo()
  } catch (erro) {
    avisarErro(erro)
  }
}

let pedidoAtual = 0
async function carregarEventos() {
  // trocando de filtro rápido, só a resposta do último pedido vale
  const pedido = ++pedidoAtual
  carregando.value = true
  try {
    const lista = await api.admin.eventos(filtro.value, busca.value?.trim())
    if (pedido === pedidoAtual) eventos.value = lista
  } catch (erro) {
    if (pedido === pedidoAtual) avisarErro(erro)
  } finally {
    if (pedido === pedidoAtual) carregando.value = false
  }
}

async function carregarAba() {
  try {
    if (aba.value === 'eventos') await carregarEventos()
    if (aba.value === 'usuarios') usuarios.value = await api.admin.usuarios()
    if (aba.value === 'palavras') palavras.value = await api.admin.palavras()
  } catch (erro) {
    avisarErro(erro)
  }
}

function escolherFiltro(valor) {
  aba.value = 'eventos'
  filtro.value = valor
  aberto.value = null
  carregarEventos()
}

async function atualizar(ev) {
  await Promise.all([carregarResumo(), carregarAba()])
  ev.target.complete()
}

async function verDenuncias(e) {
  if (aberto.value === e.id) {
    aberto.value = null
    return
  }
  aberto.value = e.id
  denuncias.value = []
  try {
    denuncias.value = await api.admin.denuncias(e.id)
  } catch (erro) {
    avisarErro(erro)
  }
}

async function descartar(e) {
  try {
    await api.admin.descartarDenuncias(e.id)
    aberto.value = null
    avisarSucesso('Denúncias descartadas.')
    await Promise.all([carregarEventos(), carregarResumo()])
  } catch (erro) {
    avisarErro(erro)
  }
}

async function alternarOculto(e) {
  try {
    await api.admin.ocultar(e.id, !e.oculto)
    avisarSucesso(e.oculto ? 'Evento visível de novo no app.' : 'Evento ocultado do app.')
    await Promise.all([carregarEventos(), carregarResumo()])
  } catch (erro) {
    avisarErro(erro)
  }
}

async function excluir(e) {
  const ok = await confirmar('Excluir evento', `Excluir "${e.nome}" de vez? As denúncias dele também serão apagadas.`, 'Excluir')
  if (!ok) return
  try {
    await api.admin.excluir(e.id)
    avisarSucesso('Evento excluído.')
    await Promise.all([carregarEventos(), carregarResumo()])
  } catch (erro) {
    avisarErro(erro)
  }
}

async function bloquear(u, bloqueado) {
  if (bloqueado === u.bloqueado) return
  try {
    const atualizado = await api.admin.bloquear(u.id, bloqueado)
    Object.assign(u, atualizado)
    avisarSucesso(bloqueado ? `${u.nome} foi bloqueado.` : `${u.nome} foi desbloqueado.`)
    carregarResumo()
  } catch (erro) {
    avisarErro(erro)
    usuarios.value = await api.admin.usuarios()
  }
}

async function adicionarPalavra() {
  try {
    await api.admin.adicionarPalavra(novaPalavra.value)
    novaPalavra.value = ''
    palavras.value = await api.admin.palavras()
    carregarResumo()
  } catch (erro) {
    avisarErro(erro)
  }
}

async function removerPalavra(p) {
  try {
    await api.admin.removerPalavra(p.id)
    palavras.value = palavras.value.filter((x) => x.id !== p.id)
    carregarResumo()
  } catch (erro) {
    avisarErro(erro)
  }
}

onIonViewWillEnter(() => {
  carregarResumo()
  carregarAba()
})
</script>

<style scoped>
.abas {
  --min-height: 48px;
  padding: 0 12px 8px;
}
.resumo {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 14px 16px 4px;
}
.numero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 10px;
  border: 0;
  border-radius: 14px;
  background: #fff;
  color: var(--ef-tinta);
  font: inherit;
  text-align: left;
  box-shadow: 0 4px 12px rgba(30, 16, 54, 0.07);
  cursor: pointer;
}
.numero strong {
  font: 800 22px/1 var(--ef-fonte-titulo);
}
.numero span {
  font-size: 11px;
  line-height: 1.2;
  color: var(--ef-tinta-2);
}
.numero.alerta {
  background: var(--ef-pitaya);
  color: #fff;
}
.numero.alerta span {
  color: rgba(255, 255, 255, 0.85);
}
.filtros {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 12px 16px 2px;
  scrollbar-width: none;
}
.filtros::-webkit-scrollbar {
  display: none;
}
.filtros button {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid var(--ef-borda);
  border-radius: 999px;
  background: #fff;
  color: var(--ef-tinta);
  font: 700 13px/1 var(--ef-fonte);
  cursor: pointer;
}
.filtros button.ativo {
  background: var(--ef-noite);
  border-color: var(--ef-noite);
  color: #fff;
}
ion-searchbar {
  padding: 8px 10px 0;
}
.evento-adm {
  margin: 10px 16px;
  padding: 12px 12px 4px;
}
.evento-adm.oculto {
  background: #f3f0f8;
}
.evento-adm-topo {
  display: flex;
  gap: 12px;
}
.capa {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
}
.info {
  min-width: 0;
  flex: 1;
}
.info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.info p {
  margin: 2px 0 6px;
  font-size: 13px;
  color: var(--ef-tinta-2);
}
.selos {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.selo {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  vertical-align: middle;
}
.selo.palavras {
  background: #fde7ef;
  color: #a3123f;
}
.selo.denuncias {
  background: #fff3d1;
  color: #7a5200;
}
.selo.incompleto {
  background: #e6f0ff;
  color: #1d4fb8;
}
.selo.cinza {
  background: #ece8f2;
  color: #5b5470;
}
.selo.ok {
  background: #ddf6f2;
  color: #0b6e64;
}
.selo.adm {
  background: var(--ef-noite);
  color: #fff;
  margin-left: 4px;
}
.motivos {
  margin: 10px 0 0;
  padding-left: 18px;
  font-size: 13px;
  color: var(--ef-tinta-2);
}
.denuncias {
  margin-top: 10px;
  padding: 10px 12px 2px;
  border-radius: 12px;
  background: #fffaf0;
}
.denuncia {
  padding: 6px 0;
  border-bottom: 1px solid #f3e7c8;
  font-size: 13px;
}
.denuncia strong {
  display: block;
}
.denuncia span {
  color: var(--ef-tinta-2);
}
.denuncia p {
  margin: 4px 0 0;
}
.acoes {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  margin-top: 6px;
  border-top: 1px solid #f0ebf7;
}
.dica {
  margin: 14px 16px 4px;
  font-size: 13px;
  color: var(--ef-tinta-2);
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--ef-suave);
  color: var(--ef-pitaya);
  font-weight: 800;
  font-size: 14px;
}
.avatar.adm {
  background: var(--ef-noite);
  color: #fff;
}
.avatar.bloqueado {
  background: #ece8f2;
  color: #8a829c;
}
.usuario h3 {
  font-weight: 700;
}
.nova-palavra {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 16px;
  padding: 4px 4px 4px 14px;
}
.palavras {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 16px 24px;
}
.palavra {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 6px 6px 12px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--ef-borda);
  font-size: 14px;
  font-weight: 600;
}
.palavra button {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border: 0;
  border-radius: 50%;
  background: #f3f0f8;
  color: var(--ef-tinta-2);
  cursor: pointer;
}
.centro {
  display: grid;
  place-items: center;
  padding: 40px;
}
.vazio {
  text-align: center;
  padding: 36px 24px;
}
.vazio-icone {
  width: 64px;
  height: 64px;
  margin: 0 auto 10px;
  border-radius: 20px;
  display: grid;
  place-items: center;
  background: #ddf6f2;
  color: #0b6e64;
  font-size: 30px;
}
.vazio h3 {
  margin: 0 0 4px;
  font-weight: 800;
}
.vazio p {
  margin: 0;
  color: var(--ef-tinta-2);
}
.vazio-pequeno {
  font-size: 13px;
  color: var(--ef-tinta-2);
}
</style>
