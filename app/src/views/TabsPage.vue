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
import { calendar as calendarOutline, grid as gridOutline, map as mapOutline, personCircle as personCircleOutline } from 'ionicons/icons'
</script>

<style scoped>
ion-tab-bar {
  height: 70px;
  box-shadow: 0 -6px 24px rgba(30, 16, 54, 0.06);
  border-top: 0;
}
ion-tab-button {
  --ripple-color: transparent;
}
ion-tab-button ion-icon {
  font-size: 22px;
  width: 52px;
  height: 30px;
  padding: 4px 0;
  border-radius: 999px;
  transition: background 0.15s;
}
ion-tab-button.tab-selected ion-icon {
  background: var(--ef-suave);
}
ion-tab-button ion-label {
  font-size: 12px;
  font-weight: 700;
  margin-top: 3px;
}
</style>
