<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/tabs/eventos" text="" />
        </ion-buttons>
        <ion-title>Detalhes</ion-title>
        <ion-buttons v-if="evento" slot="end">
          <ion-button :router-link="`/eventos/${evento.id}/editar`">
            <ion-icon slot="start" :icon="createOutline" /> Editar
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content>
      <div v-if="carregando && !evento" class="centro"><ion-spinner name="crescent" /></div>

      <div v-if="evento" class="detalhe">
        <div class="capa">
          <img v-if="evento.imagem_url && !falhouImagem" :src="evento.imagem_url" alt="" @error="falhouImagem = true" />
          <div v-else class="capa-vazia"><ion-icon :icon="imageOutline" /></div>
        </div>

        <div class="corpo">
          <span class="chip-cat">{{ evento.categoria.nome }}</span>
          <h1>{{ evento.nome }}</h1>

          <div class="infos cartao">
            <div class="info">
              <div class="icone"><ion-icon :icon="calendarOutline" /></div>
              <div>
                <span>Data</span>
                <strong class="capitalizar">{{ formatarDataLonga(evento.data) }}</strong>
              </div>
            </div>
            <div class="info">
              <div class="icone"><ion-icon :icon="timeOutline" /></div>
              <div>
                <span>Horário</span>
                <strong>{{ formatarHora(evento.hora) }}</strong>
              </div>
            </div>
            <div class="info">
              <div class="icone"><ion-icon :icon="pricetagOutline" /></div>
              <div>
                <span>Preço</span>
                <strong class="preco" :class="{ gratuito: !Number(evento.preco) }">{{ formatarPreco(evento.preco) }}</strong>
              </div>
            </div>
            <div class="info">
              <div class="icone"><ion-icon :icon="locationOutline" /></div>
              <div>
                <span>Local</span>
                <strong>{{ evento.local.nome }}</strong>
                <small v-if="evento.local.endereco">{{ evento.local.endereco }}</small>
              </div>
            </div>
          </div>

          <section v-if="evento.descricao">
            <h2>Sobre o evento</h2>
            <p class="descricao">{{ evento.descricao }}</p>
          </section>

          <section>
            <h2>Localização</h2>
            <div ref="elementoMapa" class="mini-mapa cartao" />
            <p class="coordenadas">{{ evento.local.latitude.toFixed(5) }}, {{ evento.local.longitude.toFixed(5) }}</p>
          </section>

          <ion-button expand="block" fill="clear" color="danger" class="excluir" @click="excluir">
            <ion-icon slot="start" :icon="trashOutline" /> Excluir evento
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  IonBackButton, IonButton, IonButtons, IonContent, IonHeader, IonIcon, IonPage, IonSpinner,
  IonTitle, IonToolbar, onIonViewDidEnter, onIonViewWillEnter, useIonRouter,
} from '@ionic/vue'
import {
  calendarOutline, createOutline, imageOutline, locationOutline, pricetagOutline, timeOutline, trashOutline,
} from 'ionicons/icons'
import { api } from '@/services/api'
import { avisarErro, avisarSucesso, confirmar } from '@/services/avisos'
import { criarMapa, iconePino, L } from '@/services/mapa'
import { formatarDataLonga, formatarHora, formatarPreco } from '@/services/formato'

const route = useRoute()
const ionRouter = useIonRouter()
const evento = ref(null)
const carregando = ref(true)
const falhouImagem = ref(false)
const elementoMapa = ref(null)
let mapa = null

function desenharMapa() {
  if (!evento.value || !elementoMapa.value) return
  const pos = [evento.value.local.latitude, evento.value.local.longitude]
  if (!mapa) {
    mapa = criarMapa(elementoMapa.value, { centro: pos, zoom: 15, interativo: false })
  } else {
    mapa.setView(pos, 15)
    mapa.eachLayer((l) => l instanceof L.Marker && mapa.removeLayer(l))
  }
  L.marker(pos, { icon: iconePino() }).addTo(mapa)
  mapa.invalidateSize()
}

async function carregar() {
  carregando.value = true
  try {
    evento.value = await api.evento(route.params.id)
    falhouImagem.value = false
    await nextTick()
    desenharMapa()
  } catch (erro) {
    avisarErro(erro)
    if (erro.status === 404) ionRouter.navigate('/tabs/eventos', 'back', 'replace')
  } finally {
    carregando.value = false
  }
}

async function excluir() {
  const ok = await confirmar('Excluir evento', `Tem certeza que deseja excluir "${evento.value.nome}"?`, 'Excluir')
  if (!ok) return
  try {
    await api.excluirEvento(evento.value.id)
    avisarSucesso('Evento excluído.')
    ionRouter.navigate('/tabs/eventos', 'back', 'replace')
  } catch (erro) {
    avisarErro(erro)
  }
}

onIonViewWillEnter(carregar)
onIonViewDidEnter(() => mapa?.invalidateSize())
onBeforeUnmount(() => mapa?.remove())
</script>

<style scoped>
.centro {
  display: grid;
  place-items: center;
  height: 60%;
}
.capa {
  height: 230px;
  background: var(--ef-suave);
}
.capa img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.capa-vazia {
  height: 100%;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
}
.capa-vazia ion-icon {
  font-size: 56px;
  color: rgba(255, 255, 255, 0.7);
}
.corpo {
  padding: 20px 16px 32px;
  margin-top: -20px;
  border-radius: 22px 22px 0 0;
  background: var(--ion-background-color);
  position: relative;
}
h1 {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.4px;
  margin: 10px 0 16px;
  line-height: 1.2;
}
h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 24px 0 8px;
}
.infos {
  padding: 4px 16px;
}
.info {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--ef-borda);
}
.info:last-child {
  border-bottom: 0;
}
.icone {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--ef-suave);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.icone ion-icon {
  font-size: 20px;
  color: var(--ion-color-primary);
}
.info span {
  display: block;
  font-size: 12px;
  color: var(--ion-color-medium);
}
.info strong {
  display: block;
  font-size: 15px;
}
.info small {
  display: block;
  color: var(--ion-color-medium);
  font-size: 13px;
  margin-top: 2px;
}
.capitalizar::first-letter {
  text-transform: uppercase;
}
.descricao {
  margin: 0;
  color: #4a4f61;
  line-height: 1.55;
  white-space: pre-line;
}
.mini-mapa {
  height: 170px;
}
.coordenadas {
  font-size: 12px;
  color: var(--ion-color-medium);
  margin: 6px 2px 0;
}
.excluir {
  margin-top: 24px;
}
</style>
