<template>
  <ion-page>
    <ion-tabs>
      <ion-router-outlet />
      <ion-tab-bar slot="bottom">
        <ion-tab-button tab="eventos" href="/tabs/eventos">
          <ion-icon :icon="calendarOutline" />
          <ion-label>Eventos</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="mapa" href="/tabs/mapa">
          <ion-icon :icon="mapOutline" />
          <ion-label>Mapa</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="cadastros" href="/tabs/cadastros">
          <ion-icon :icon="gridOutline" />
          <ion-label>Cadastros</ion-label>
        </ion-tab-button>
        <ion-tab-button tab="perfil" href="/tabs/perfil">
          <ion-icon :icon="personCircleOutline" />
          <ion-label>Perfil</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  </ion-page>
</template>

<script setup>
import { IonIcon, IonLabel, IonPage, IonRouterOutlet, IonTabBar, IonTabButton, IonTabs } from '@ionic/vue'
import { calendarOutline, gridOutline, mapOutline, personCircleOutline } from 'ionicons/icons'
</script>

<style scoped>
ion-tab-bar {
  height: 64px;
}
ion-tab-button ion-label {
  font-size: 12px;
  font-weight: 600;
}
</style>
