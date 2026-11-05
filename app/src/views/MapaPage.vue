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

      <div v-if="!carregando && !grupos.length" class="aviso-flutuante cartao">
        <ion-icon :icon="locationOutline" />
        Nenhum evento com local cadastrado ainda.
      </div>

      <transition name="subir">
        <section v-if="selecionado" class="painel cartao">
          <header class="painel-topo">
            <div>
              <h2>{{ selecionado.local.nome }}</h2>
              <p v-if="selecionado.local.endereco">{{ selecionado.local.endereco }}</p>
            </div>
            <ion-button fill="clear" color="medium" size="small" aria-label="Fechar" @click="fechar">
              <ion-icon slot="icon-only" :icon="close" />
            </ion-button>
          </header>

          <div class="painel-lista">
            <article v-for="e in selecionado.eventos" :key="e.id" class="item-evento">
              <div class="item-info">
                <h3>{{ e.nome }}</h3>
                <p>
                  <ion-icon :icon="calendarOutline" /> {{ formatarData(e.data) }} · {{ formatarHora(e.hora) }}
                </p>
                <span class="preco" :class="{ gratuito: !Number(e.preco) }">{{ formatarPreco(e.preco) }}</span>
              </div>
              <ion-button size="small" @click="verDetalhes(e.id)">Ver detalhes</ion-button>
            </article>
          </div>
        </section>
      </transition>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import {
  IonButton, IonButtons, IonContent, IonHeader, IonIcon, IonPage, IonTitle, IonToolbar,
  onIonViewDidEnter, onIonViewWillEnter, useIonRouter,
} from '@ionic/vue'
import { calendarOutline, close, locationOutline, scanOutline } from 'ionicons/icons'
import { api } from '@/services/api'
import { avisarErro } from '@/services/avisos'
import { criarMapa, iconePino, L } from '@/services/mapa'
import { formatarData, formatarHora, formatarPreco } from '@/services/formato'

const ionRouter = useIonRouter()
const elementoMapa = ref(null)
const grupos = ref([])
const selecionado = ref(null)
const carregando = ref(true)

let mapa = null
let camada = null
const marcadores = new Map()

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
  camada.clearLayers()
  marcadores.clear()
  for (const g of grupos.value) {
    const ativo = selecionado.value?.local.id === g.local.id
    const m = L.marker([g.local.latitude, g.local.longitude], {
      icon: iconePino({ quantidade: g.eventos.length, selecionado: ativo }),
      title: g.local.nome,
    })
    m.on('click', (ev) => {
      L.DomEvent.stopPropagation(ev)
      selecionar(g)
    })
    m.addTo(camada)
    marcadores.set(g.local.id, m)
  }
}

function selecionar(grupo) {
  selecionado.value = grupo
  desenharMarcadores()
  mapa.panTo([grupo.local.latitude, grupo.local.longitude], { animate: true })
}

function fechar() {
  selecionado.value = null
  desenharMarcadores()
}

function enquadrar() {
  if (!mapa || !grupos.value.length) return
  const limites = L.latLngBounds(grupos.value.map((g) => [g.local.latitude, g.local.longitude]))
  mapa.fitBounds(limites, { padding: [60, 60], maxZoom: 15 })
}

async function carregar() {
  carregando.value = true
  try {
    const eventos = await api.eventos()
    grupos.value = agruparPorLocal(eventos)
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

// O Leaflet precisa que o elemento já esteja visível para calcular o tamanho.
onIonViewDidEnter(() => {
  if (!mapa) {
    mapa = criarMapa(elementoMapa.value)
    camada = L.layerGroup().addTo(mapa)
    mapa.on('click', fechar)
    desenharMarcadores()
    enquadrar()
  }
  mapa.invalidateSize()
})

onBeforeUnmount(() => {
  mapa?.remove()
  mapa = null
})
</script>

<style scoped>
.mapa {
  position: absolute;
  inset: 0;
  z-index: 0;
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
  padding: 14px 14px 10px 16px;
  max-height: 55%;
  display: flex;
  flex-direction: column;
}
.painel-topo {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.painel-topo h2 {
  margin: 4px 0 2px;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--ion-color-primary);
}
.painel-topo p {
  margin: 0;
  font-size: 13px;
  color: var(--ion-color-medium);
}
.painel-lista {
  overflow-y: auto;
}
.item-evento {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid var(--ef-borda);
}
.item-evento:first-child {
  border-top: 0;
}
.item-info {
  flex: 1;
  min-width: 0;
}
.item-info h3 {
  margin: 0 0 3px;
  font-size: 17px;
  font-weight: 700;
}
.item-info p {
  margin: 0 0 4px;
  font-size: 13px;
  color: var(--ion-color-medium);
  display: flex;
  align-items: center;
  gap: 4px;
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
