<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/tabs/cadastros" text="" />
        </ion-buttons>
        <ion-title>Locais</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <ion-refresher slot="fixed" @ionRefresh="atualizar">
        <ion-refresher-content />
      </ion-refresher>

      <div v-if="carregando && !locais.length" class="centro"><ion-spinner name="crescent" /></div>

      <ion-list v-if="locais.length" class="lista-cartao" lines="full">
        <ion-item v-for="l in locais" :key="l.id" button :detail="true" :router-link="`/locais/${l.id}/editar`">
          <div slot="start" class="bolinha"><ion-icon :icon="locationOutline" /></div>
          <ion-label>
            <h2>{{ l.nome }}</h2>
            <p v-if="l.endereco">{{ l.endereco }}</p>
            <p class="coord">{{ l.latitude.toFixed(5) }}, {{ l.longitude.toFixed(5) }}</p>
          </ion-label>
        </ion-item>
      </ion-list>

      <div v-if="!carregando && !locais.length" class="vazio">
        <ion-icon :icon="mapOutline" />
        <h3>Nenhum local</h3>
        <p>Cadastre os locais com latitude e longitude para os eventos aparecerem no mapa.</p>
        <ion-button router-link="/locais/novo">Novo local</ion-button>
      </div>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end">
        <ion-fab-button router-link="/locais/novo" aria-label="Novo local">
          <ion-icon :icon="add" />
        </ion-fab-button>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import {
  IonBackButton, IonButton, IonButtons, IonContent, IonFab, IonFabButton, IonHeader, IonIcon, IonItem, IonLabel,
  IonList, IonPage, IonRefresher, IonRefresherContent, IonSpinner, IonTitle, IonToolbar, onIonViewWillEnter,
} from '@ionic/vue'
import { add, locationOutline, mapOutline } from 'ionicons/icons'
import { api } from '@/services/api'
import { avisarErro } from '@/services/avisos'

const locais = ref([])
const carregando = ref(true)

async function carregar() {
  carregando.value = true
  try {
    locais.value = await api.locais()
  } catch (erro) {
    avisarErro(erro)
  } finally {
    carregando.value = false
  }
}

async function atualizar(ev) {
  await carregar()
  ev.target.complete()
}

onIonViewWillEnter(carregar)
</script>

<style scoped>
.centro {
  display: grid;
  place-items: center;
  padding: 40px;
}
.bolinha {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: #e7f6ec;
  display: grid;
  place-items: center;
  margin-right: 4px;
}
.bolinha ion-icon {
  color: #16a34a;
  font-size: 18px;
}
ion-label h2 {
  font-weight: 600;
  font-size: 16px;
}
.coord {
  font-size: 12px !important;
  font-variant-numeric: tabular-nums;
}
</style>
