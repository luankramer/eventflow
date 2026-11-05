<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/tabs/cadastros" text="" />
        </ion-buttons>
        <ion-title>Categorias</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <ion-refresher slot="fixed" @ionRefresh="atualizar">
        <ion-refresher-content />
      </ion-refresher>

      <div v-if="carregando && !categorias.length" class="centro"><ion-spinner name="crescent" /></div>

      <ion-list v-if="categorias.length" class="lista-cartao" lines="full">
        <ion-item v-for="c in categorias" :key="c.id" button :detail="true" :router-link="`/categorias/${c.id}/editar`">
          <div slot="start" class="bolinha"><ion-icon :icon="pricetagOutline" /></div>
          <ion-label>
            <h2>{{ c.nome }}</h2>
            <p v-if="c.descricao">{{ c.descricao }}</p>
          </ion-label>
        </ion-item>
      </ion-list>

      <div v-if="!carregando && !categorias.length" class="vazio">
        <ion-icon :icon="pricetagsOutline" />
        <h3>Nenhuma categoria</h3>
        <p>Crie categorias como Música, Esporte ou Cultura.</p>
        <ion-button router-link="/categorias/nova">Nova categoria</ion-button>
      </div>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end">
        <ion-fab-button router-link="/categorias/nova" aria-label="Nova categoria">
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
import { add, pricetagOutline, pricetagsOutline } from 'ionicons/icons'
import { api } from '@/services/api'
import { avisarErro } from '@/services/avisos'

const categorias = ref([])
const carregando = ref(true)

async function carregar() {
  carregando.value = true
  try {
    categorias.value = await api.categorias()
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
  background: var(--ef-suave);
  display: grid;
  place-items: center;
  margin-right: 4px;
}
.bolinha ion-icon {
  color: var(--ion-color-primary);
  font-size: 18px;
}
ion-label h2 {
  font-weight: 600;
  font-size: 16px;
}
</style>
