<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/locais" text="" />
        </ion-buttons>
        <ion-title>{{ editando ? 'Editar local' : 'Novo local' }}</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <form class="formulario" @submit.prevent="salvar">
        <div>
          <label class="rotulo" for="nome-local">Nome *</label>
          <ion-input id="nome-local" v-model="form.nome" fill="outline" placeholder="Ex.: Parque da Maternidade" :maxlength="120" />
        </div>

        <div>
          <div class="rotulo-linha">
            <span class="rotulo">Posição no mapa *</span>
            <ion-button size="small" fill="clear" :disabled="localizando" @click="usarMinhaLocalizacao">
              <ion-spinner v-if="localizando" name="crescent" />
              <template v-else><ion-icon slot="start" :icon="locateOutline" /> Minha localização</template>
            </ion-button>
          </div>
          <div ref="elementoMapa" class="mapa-seletor cartao" />
          <p class="dica">Toque no mapa ou arraste o marcador para ajustar.</p>
        </div>

        <div class="campo-grupo">
          <div>
            <label class="rotulo" for="lat">Latitude *</label>
            <ion-input id="lat" v-model="form.latitude" fill="outline" inputmode="decimal" placeholder="-9.97470" @ionBlur="sincronizarMarcador" />
          </div>
          <div>
            <label class="rotulo" for="lng">Longitude *</label>
            <ion-input id="lng" v-model="form.longitude" fill="outline" inputmode="decimal" placeholder="-67.80760" @ionBlur="sincronizarMarcador" />
          </div>
        </div>

        <div>
          <label class="rotulo" for="endereco">Endereço (opcional)</label>
          <ion-input id="endereco" v-model="form.endereco" fill="outline" placeholder="Rua, número, bairro" :maxlength="255" />
        </div>

        <ion-button type="submit" expand="block" class="botao-grande" :disabled="salvando || carregando">
          <ion-spinner v-if="salvando" name="crescent" />
          <span v-else>{{ editando ? 'Salvar alterações' : 'Cadastrar local' }}</span>
        </ion-button>
        <ion-button v-if="editando" expand="block" fill="clear" color="danger" @click="excluir">
          <ion-icon slot="start" :icon="trashOutline" /> Excluir local
        </ion-button>
      </form>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  IonBackButton, IonButton, IonButtons, IonContent, IonHeader, IonIcon, IonInput, IonPage, IonSpinner,
  IonTitle, IonToolbar, onIonViewDidEnter, useIonRouter,
} from '@ionic/vue'
import { locateOutline, trashOutline } from 'ionicons/icons'
import { Geolocation } from '@capacitor/geolocation'
import { api } from '@/services/api'
import { voltarPara } from '@/services/navegacao'
import { avisar, avisarErro, avisarSucesso, confirmar } from '@/services/avisos'
import { CENTRO_PADRAO, aoFalharGoogle, criarMapa } from '@/services/mapa'

const route = useRoute()
const ionRouter = useIonRouter()
const id = route.params.id
const editando = computed(() => Boolean(id))

const form = reactive({ nome: '', latitude: '', longitude: '', endereco: '' })
const carregando = ref(Boolean(id))
const salvando = ref(false)
const localizando = ref(false)
const elementoMapa = ref(null)

let mapa = null
let marcador = null

const numero = (v) => {
  const n = Number(String(v ?? '').trim().replace(',', '.'))
  return String(v ?? '').trim() === '' || !Number.isFinite(n) ? null : n
}

function definirPosicao(lat, lng, centralizar = true) {
  form.latitude = lat.toFixed(6)
  form.longitude = lng.toFixed(6)
  if (!mapa) return
  if (!marcador) {
    marcador = mapa.marcador({
      lat,
      lng,
      arrastavel: true,
      aoArrastar: (la, ln) => definirPosicao(la, ln, false),
    })
  } else {
    marcador.mover(lat, lng)
  }
  if (centralizar) mapa.centralizar(lat, lng, Math.max(mapa.zoom(), 15))
}

function sincronizarMarcador() {
  const lat = numero(form.latitude)
  const lng = numero(form.longitude)
  if (lat === null || lng === null || Math.abs(lat) > 90 || Math.abs(lng) > 180) return
  definirPosicao(lat, lng)
}

let montando = false
async function iniciarMapa() {
  if (mapa || montando || !elementoMapa.value) return
  montando = true
  try {
    mapa = await criarMapa(elementoMapa.value, { zoom: 13 })
    mapa.aoClicar((lat, lng) => definirPosicao(lat, lng, false))
    marcador = null
    sincronizarMarcador()
  } finally {
    montando = false
  }
}

// Se a chave do Google for recusada, refaz o mapa com OpenStreetMap.
const pararDeOuvir = aoFalharGoogle(() => {
  mapa?.destruir()
  mapa = null
  iniciarMapa()
})

async function usarMinhaLocalizacao() {
  localizando.value = true
  try {
    const pos = await Geolocation.getCurrentPosition({ enableHighAccuracy: true, timeout: 15000 })
    definirPosicao(pos.coords.latitude, pos.coords.longitude)
  } catch {
    avisar('Não foi possível obter sua localização. Verifique se o GPS e a permissão estão ativos.')
  } finally {
    localizando.value = false
  }
}

onMounted(async () => {
  if (!id) return
  try {
    const l = await api.local(id)
    form.nome = l.nome
    form.endereco = l.endereco || ''
    form.latitude = String(l.latitude)
    form.longitude = String(l.longitude)
    sincronizarMarcador()
  } catch (erro) {
    avisarErro(erro)
  } finally {
    carregando.value = false
  }
})

onIonViewDidEnter(async () => {
  await iniciarMapa()
  mapa?.atualizarTamanho()
  if (!marcador && !id) mapa?.centralizar(CENTRO_PADRAO[0], CENTRO_PADRAO[1], 13)
})

onBeforeUnmount(() => {
  pararDeOuvir()
  mapa?.destruir()
})

async function salvar() {
  const latitude = numero(form.latitude)
  const longitude = numero(form.longitude)
  if (form.nome.trim().length < 2) return avisar('Informe o nome do local.')
  if (latitude === null || latitude < -90 || latitude > 90) return avisar('Latitude inválida (entre -90 e 90).')
  if (longitude === null || longitude < -180 || longitude > 180) return avisar('Longitude inválida (entre -180 e 180).')

  salvando.value = true
  try {
    const dados = { nome: form.nome.trim(), latitude, longitude, endereco: form.endereco.trim() || null }
    if (editando.value) await api.editarLocal(id, dados)
    else await api.criarLocal(dados)
    avisarSucesso(editando.value ? 'Local atualizado.' : 'Local cadastrado.')
    voltarPara(ionRouter, '/locais')
  } catch (erro) {
    avisarErro(erro)
  } finally {
    salvando.value = false
  }
}

async function excluir() {
  if (!(await confirmar('Excluir local', `Excluir "${form.nome}"?`, 'Excluir'))) return
  try {
    await api.excluirLocal(id)
    avisarSucesso('Local excluído.')
    voltarPara(ionRouter, '/locais')
  } catch (erro) {
    avisarErro(erro)
  }
}
</script>

<style scoped>
.rotulo-linha {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.rotulo-linha ion-button {
  margin: 0;
  --padding-end: 0;
  height: 28px;
  font-size: 13px;
}
.mapa-seletor {
  height: 220px;
}
.dica {
  font-size: 12px;
  color: var(--ion-color-medium);
  margin: 6px 2px 0;
}
</style>
