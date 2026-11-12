<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Mapa de eventos</ion-title>
        <ion-buttons slot="end">
          <ion-button aria-label="Centralizar" @click="enquadrar">
            <ion-icon slot="icon-only" :icon="scanOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :scroll-y="false">
      <div ref="elementoMapa" class="mapa" />

      <!-- Legenda: cada cor é um tipo de evento. Tocar filtra o mapa. -->
      <div v-if="tiposNoMapa.length" class="legenda">
        <button type="button" :class="{ ativo: filtro === null }" @click="filtrar(null)">Todos</button>
        <button
          v-for="c in tiposNoMapa"
          :key="c.id"
          type="button"
          :class="{ ativo: filtro === c.id }"
          :style="{ '--tipo': corCategoria(c).cor, '--tipo-tinta': corCategoria(c).tinta }"
          @click="filtrar(c.id)"
        >
          <span class="ponto" /> {{ c.nome }}
        </button>
      </div>

      <div v-if="!carregando && !grupos.length" class="aviso-flutuante cartao">
        <ion-icon :icon="locationOutline" />
        Nenhum evento com local cadastrado ainda.
      </div>

      <transition name="subir">
        <section v-if="selecionado" class="painel cartao">
          <header class="painel-topo">
            <div class="painel-local">
              <div class="painel-icone" :style="{ background: corGrupo(selecionado), color: corCategoria(selecionado.eventos[0]?.categoria).tinta }"><ion-icon :icon="location" /></div>
              <div>
              <h2>{{ selecionado.local.nome }}</h2>
              <p v-if="selecionado.local.endereco">{{ selecionado.local.endereco }}</p>
              </div>
            </div>
            <ion-button fill="clear" color="medium" size="small" aria-label="Fechar" @click="fechar">
              <ion-icon slot="icon-only" :icon="close" />
            </ion-button>
          </header>

          <div class="painel-lista">
            <button v-for="e in selecionado.eventos" :key="e.id" type="button" class="item-evento" @click="verDetalhes(e.id)">
              <div class="item-capa"><CapaEvento :evento="e" tamanho-icone="22px" /></div>
              <div class="item-info">
                <span class="item-cat" :style="{ color: corCategoria(e.categoria).texto }">{{ e.categoria.nome }}</span>
                <h3>{{ e.nome }}</h3>
                <p>
                  <ion-icon :icon="calendarOutline" /> {{ formatarData(e.data) }}
                  <ion-icon :icon="timeOutline" class="sep" /> {{ formatarHora(e.hora) }}
                </p>
                <span class="preco" :class="{ gratuito: !Number(e.preco) }">{{ formatarPreco(e.preco) }}</span>
              </div>
              <span class="ver">Ver detalhes</span>
            </button>
          </div>
        </section>
      </transition>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { computed, ref, onBeforeUnmount } from 'vue'
import {
  IonButton, IonButtons, IonContent, IonHeader, IonIcon, IonPage, IonTitle, IonToolbar,
  onIonViewDidEnter, onIonViewWillEnter, useIonRouter,
} from '@ionic/vue'
import { calendarOutline, close, location, locationOutline, scanOutline, timeOutline } from 'ionicons/icons'
import CapaEvento from '@/components/CapaEvento.vue'
import { corCategoria } from '@/services/cores'
import { api } from '@/services/api'
import { avisarErro } from '@/services/avisos'
import { aoFalharGoogle, criarMapa } from '@/services/mapa'
import { formatarData, formatarHora, formatarPreco } from '@/services/formato'

const ionRouter = useIonRouter()
const elementoMapa = ref(null)
const todosEventos = ref([])
const grupos = ref([])
const filtro = ref(null)

// Tipos de evento presentes no mapa, para a legenda.
const tiposNoMapa = computed(() => {
  const mapa = new Map()
  for (const e of todosEventos.value) mapa.set(e.categoria.id, e.categoria)
  return [...mapa.values()].sort((a, b) => a.nome.localeCompare(b.nome))
})

function filtrar(id) {
  filtro.value = id
  selecionado.value = null
  aplicarFiltro()
  enquadrar()
}

function aplicarFiltro() {
  const lista = filtro.value === null ? todosEventos.value : todosEventos.value.filter((e) => e.categoria.id === filtro.value)
  grupos.value = agruparPorLocal(lista)
  desenharMarcadores()
}
const selecionado = ref(null)
const carregando = ref(true)

let mapa = null
let montando = false

// Cor do pino: categoria do próximo evento daquele local.
const corGrupo = (g) => corCategoria(g.eventos[0]?.categoria).cor

// Um marcador por local; cada local pode ter vários eventos.
function agruparPorLocal(eventos) {
  const porLocal = new Map()
  for (const e of eventos) {
    if (e.local?.latitude == null || e.local?.longitude == null) continue
    if (!porLocal.has(e.local.id)) porLocal.set(e.local.id, { local: e.local, eventos: [] })
    porLocal.get(e.local.id).eventos.push(e)
  }
  return [...porLocal.values()]
}

function desenharMarcadores() {
  if (!mapa) return
  mapa.limpar()
  for (const g of grupos.value) {
    mapa.marcador({
      lat: g.local.latitude,
      lng: g.local.longitude,
      cor: corGrupo(g),
      quantidade: g.eventos.length,
      selecionado: selecionado.value?.local.id === g.local.id,
      aoClicar: () => selecionar(g),
    })
  }
}

function selecionar(grupo) {
  selecionado.value = grupo
  desenharMarcadores()
  mapa.deslizar(grupo.local.latitude, grupo.local.longitude)
}

function fechar() {
  selecionado.value = null
  desenharMarcadores()
}

function enquadrar() {
  if (!mapa || !grupos.value.length) return
  mapa.enquadrar(grupos.value.map((g) => [g.local.latitude, g.local.longitude]), { margem: 70, zoomMax: 15 })
}

async function carregar() {
  carregando.value = true
  try {
    const eventos = await api.eventos()
    todosEventos.value = eventos
    if (filtro.value !== null && !eventos.some((e) => e.categoria.id === filtro.value)) filtro.value = null
    grupos.value = agruparPorLocal(filtro.value === null ? eventos : eventos.filter((e) => e.categoria.id === filtro.value))
    if (selecionado.value) {
      selecionado.value = grupos.value.find((g) => g.local.id === selecionado.value.local.id) ?? null
    }
    desenharMarcadores()
    if (!selecionado.value) enquadrar()
  } catch (erro) {
    avisarErro(erro)
  } finally {
    carregando.value = false
  }
}

const verDetalhes = (id) => ionRouter.push(`/eventos/${id}`)

onIonViewWillEnter(() => {
  carregar()
})

async function montarMapa() {
  if (montando) return
  montando = true
  try {
    mapa?.destruir()
    mapa = await criarMapa(elementoMapa.value)
    mapa.aoClicar(fechar)
    desenharMarcadores()
    enquadrar()
  } finally {
    montando = false
  }
}

// Se a chave do Google for recusada, refaz o mapa com OpenStreetMap.
const pararDeOuvir = aoFalharGoogle(() => {
  montarMapa() // apaga o mapa do Google e cria o do OpenStreetMap no lugar
})

// O mapa precisa que o elemento já esteja visível para calcular o tamanho.
onIonViewDidEnter(() => {
  if (!mapa) montarMapa()
  else mapa.atualizarTamanho()
})

onBeforeUnmount(() => {
  pararDeOuvir()
  mapa?.destruir()
  mapa = null
})
</script>

<style scoped>
.mapa {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.legenda {
  position: absolute;
  z-index: 500;
  top: 12px;
  left: 0;
  right: 0;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 0 12px 6px;
  scrollbar-width: none;
}
.legenda::-webkit-scrollbar {
  display: none;
}
.legenda button {
  --tipo: var(--ef-noite);
  --tipo-tinta: #fff;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 0;
  border-radius: 999px;
  padding: 8px 13px;
  background: #fff;
  color: var(--ef-tinta);
  font: 700 13px/1 var(--ef-fonte);
  box-shadow: 0 4px 14px rgba(30, 16, 54, 0.16);
  cursor: pointer;
}
.legenda .ponto {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--tipo);
  box-shadow: 0 0 0 2px #fff, 0 0 0 3px color-mix(in srgb, var(--tipo) 40%, transparent);
}
.legenda button.ativo {
  background: var(--tipo);
  color: var(--tipo-tinta);
}
.legenda button.ativo .ponto {
  background: var(--tipo-tinta);
  box-shadow: none;
}
.aviso-flutuante {
  position: absolute;
  top: 12px;
  left: 16px;
  right: 16px;
  z-index: 500;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--ion-color-medium);
}
.painel {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  z-index: 600;
  padding: 16px 16px 6px;
  border-radius: 24px;
  box-shadow: 0 16px 40px rgba(30, 16, 54, 0.28);
  max-height: 55%;
  display: flex;
  flex-direction: column;
}
.painel-topo {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  padding-bottom: 6px;
}
.painel-local {
  display: flex;
  gap: 12px;
  align-items: center;
  min-width: 0;
}
.painel-icone {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: 20px;
}
.painel-topo h2 {
  margin: 0;
  font-size: 19px;
  font-weight: 800;
  letter-spacing: -0.3px;
}
.painel-topo p {
  margin: 2px 0 0;
  font-size: 13px;
  color: var(--ion-color-medium);
}
.painel-lista {
  overflow-y: auto;
}
.item-evento {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border: 0;
  border-top: 1px solid #f0ebf7;
  background: none;
  font: inherit;
  color: inherit;
  text-align: left;
  cursor: pointer;
}
.item-capa {
  width: 62px;
  height: 62px;
  flex-shrink: 0;
  border-radius: 14px;
  overflow: hidden;
}
.item-info {
  flex: 1;
  min-width: 0;
}
.item-cat {
  font-size: 12px;
  font-weight: 700;
}
.item-info h3 {
  margin: 1px 0 3px;
  font-size: 16px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-info p {
  margin: 0 0 2px;
  font-size: 13px;
  color: var(--ion-color-medium);
  display: flex;
  align-items: center;
  gap: 4px;
}
.item-info p .sep {
  margin-left: 6px;
}
.item-info .preco {
  font-size: 15px;
}
.ver {
  flex-shrink: 0;
  background: var(--ef-pitaya);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  padding: 9px 12px;
  border-radius: 12px;
}
.subir-enter-active,
.subir-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.subir-enter-from,
.subir-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>
