<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <!-- botões flutuantes sobre a capa -->
      <div class="barra-flutuante">
        <ion-back-button default-href="/tabs/eventos" text="" class="botao-vidro" />
        <ion-button v-if="evento" class="botao-vidro editar" :router-link="`/eventos/${evento.id}/editar`">
          <ion-icon slot="start" :icon="createOutline" /> Editar
        </ion-button>
      </div>

      <div v-if="carregando && !evento" class="centro"><ion-spinner name="crescent" /></div>

      <div v-if="evento" class="detalhe" :style="{ '--cat': cor.cor, '--cat-suave': cor.suave, '--cat-texto': cor.texto, '--cat-tinta': cor.tinta }">
        <div class="capa">
          <CapaEvento :evento="evento" tamanho-icone="88px" />
          <div class="veu" />
          <div class="capa-texto">
            <span class="chip-cat"><ion-icon :icon="icone" /> {{ evento.categoria.nome }}</span>
            <h1>{{ evento.nome }}</h1>
          </div>
        </div>

        <div class="corpo">
          <!-- ingresso com data, horário e preço -->
          <div class="sombra">
            <div class="ingresso">
              <div class="canhoto">
                <span>{{ data.semana }}</span>
                <strong>{{ data.dia }}</strong>
                <span>{{ data.mes }}</span>
              </div>
              <div class="dados">
                <div>
                  <span class="rotulo-dado">Data</span>
                  <strong class="capitalizar">{{ formatarDataLonga(evento.data) }}</strong>
                </div>
                <div class="dados-linha">
                  <div>
                    <span class="rotulo-dado">Horário</span>
                    <strong class="grande">{{ formatarHora(evento.hora) }}</strong>
                  </div>
                  <div>
                    <span class="rotulo-dado">Preço</span>
                    <strong class="grande preco" :class="{ gratuito: !Number(evento.preco) }">{{ formatarPreco(evento.preco) }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <section v-if="evento.descricao">
            <h2 class="titulo-secao">Sobre o evento</h2>
            <p class="descricao">{{ evento.descricao }}</p>
          </section>

          <section>
            <h2 class="titulo-secao">Onde vai ser</h2>
            <div class="local cartao">
              <div ref="elementoMapa" class="mini-mapa" />
              <div class="local-info">
                <div class="local-icone"><ion-icon :icon="location" /></div>
                <div>
                  <strong>{{ evento.local.nome }}</strong>
                  <span v-if="evento.local.endereco">{{ evento.local.endereco }}</span>
                  <small>{{ evento.local.latitude.toFixed(5) }}, {{ evento.local.longitude.toFixed(5) }}</small>
                </div>
              </div>
            </div>
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
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  IonBackButton, IonButton, IonContent, IonIcon, IonPage, IonSpinner,
  onIonViewDidEnter, onIonViewWillEnter, useIonRouter,
} from '@ionic/vue'
import { createOutline, location, trashOutline } from 'ionicons/icons'
import CapaEvento from '@/components/CapaEvento.vue'
import { api } from '@/services/api'
import { avisarErro, avisarSucesso, confirmar } from '@/services/avisos'
import { criarMapa, iconePino, L } from '@/services/mapa'
import { formatarDataLonga, formatarHora, formatarPreco, partesData } from '@/services/formato'
import { corCategoria, iconeCategoria } from '@/services/cores'

const route = useRoute()
const ionRouter = useIonRouter()
const evento = ref(null)
const carregando = ref(true)
const elementoMapa = ref(null)
let mapa = null

const cor = computed(() => corCategoria(evento.value?.categoria))
const icone = computed(() => iconeCategoria(evento.value?.categoria))
const data = computed(() => partesData(evento.value.data))

function desenharMapa() {
  if (!evento.value || !elementoMapa.value) return
  const pos = [evento.value.local.latitude, evento.value.local.longitude]
  if (!mapa) {
    mapa = criarMapa(elementoMapa.value, { centro: pos, zoom: 15, interativo: false })
  } else {
    mapa.setView(pos, 15)
    mapa.eachLayer((l) => l instanceof L.Marker && mapa.removeLayer(l))
  }
  L.marker(pos, { icon: iconePino({ cor: cor.value.cor }) }).addTo(mapa)
  mapa.invalidateSize()
}

async function carregar() {
  carregando.value = true
  try {
    evento.value = await api.evento(route.params.id)
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
.barra-flutuante {
  position: absolute;
  z-index: 10;
  top: calc(var(--ion-safe-area-top, 0px) + 10px);
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}
.botao-vidro {
  pointer-events: auto;
  --background: rgba(30, 16, 54, 0.45);
  --background-activated: rgba(30, 16, 54, 0.6);
  --color: #fff;
  --border-radius: 999px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 999px;
}
ion-back-button.botao-vidro {
  width: 44px;
  height: 44px;
  --icon-font-size: 22px;
  --padding-start: 0;
  --padding-end: 0;
  display: block;
}
.editar {
  height: 44px;
  margin: 0;
  --padding-start: 16px;
  --padding-end: 18px;
}
.centro {
  display: grid;
  place-items: center;
  height: 60%;
}
.capa {
  position: relative;
  height: 360px;
}
.veu {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(30, 16, 54, 0.45) 0%, rgba(30, 16, 54, 0) 30%, rgba(30, 16, 54, 0.15) 55%, rgba(30, 16, 54, 0.92) 100%);
}
.capa-texto {
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 56px;
  color: #fff;
}
.capa-texto .chip-cat {
  background: var(--cat);
  color: var(--cat-tinta);
}
h1 {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.8px;
  line-height: 1.08;
  margin: 10px 0 0;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.25);
}
.corpo {
  position: relative;
  margin-top: -36px;
  padding: 0 16px 36px;
}

/* ingresso */
.sombra {
  filter: drop-shadow(0 10px 22px rgba(30, 16, 54, 0.14));
}
.ingresso {
  --recorte: 10px;
  display: flex;
  background: #fff;
  border-radius: 22px;
  overflow: hidden;
  -webkit-mask:
    radial-gradient(circle at 92px 0, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) top / 100% 51% no-repeat,
    radial-gradient(circle at 92px 100%, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) bottom / 100% 51% no-repeat;
  mask:
    radial-gradient(circle at 92px 0, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) top / 100% 51% no-repeat,
    radial-gradient(circle at 92px 100%, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) bottom / 100% 51% no-repeat;
}
.canhoto {
  width: 92px;
  flex-shrink: 0;
  background: var(--cat);
  color: var(--cat-tinta);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 2px dashed rgba(255, 255, 255, 0.6);
  padding: 16px 0;
}
.canhoto span {
  font-size: 13px;
  font-weight: 700;
  opacity: 0.9;
}
.canhoto strong {
  font-family: var(--ef-fonte-titulo);
  font-size: 44px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -1.5px;
  margin: 2px 0;
}
.dados {
  flex: 1;
  min-width: 0;
  padding: 16px 16px 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.dados-linha {
  display: flex;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid #f0ebf7;
}
.rotulo-dado {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--ion-color-medium);
  margin-bottom: 2px;
}
.dados strong {
  display: block;
  font-size: 15px;
  font-weight: 700;
}
.dados strong.grande {
  font-family: var(--ef-fonte-titulo);
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.4px;
}
.capitalizar::first-letter {
  text-transform: uppercase;
}
.descricao {
  margin: 0;
  color: var(--ef-tinta-2);
  font-size: 16px;
  line-height: 1.6;
  white-space: pre-line;
}

/* local */
.local {
  overflow: hidden;
}
.mini-mapa {
  height: 160px;
}
.local-info {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 16px 16px;
}
.local-icone {
  width: 40px;
  height: 40px;
  border-radius: 13px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  background: var(--cat-suave);
  color: var(--cat);
  font-size: 20px;
}
.local-info strong {
  display: block;
  font-size: 16px;
}
.local-info span {
  display: block;
  color: var(--ef-tinta-2);
  font-size: 14px;
  margin-top: 2px;
}
.local-info small {
  display: block;
  color: var(--ion-color-medium);
  font-size: 12px;
  margin-top: 4px;
  font-variant-numeric: tabular-nums;
}
.excluir {
  margin-top: 22px;
}
</style>
