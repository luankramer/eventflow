<template>
  <ion-page>
    <ion-content class="ion-padding">
      <header class="topo respeita-status">
        <h1 class="titulo-pagina">Perfil</h1>
      </header>

      <section class="cartao perfil">
        <div class="avatar">{{ iniciais(usuario?.nome) }}</div>
        <h2>{{ usuario?.nome }}</h2>
        <p>{{ usuario?.email }}</p>
      </section>

      <ion-list class="lista-cartao" lines="full">
        <ion-item>
          <ion-icon slot="start" :icon="personOutline" color="primary" />
          <ion-label>
            <p>Nome</p>
            <h3>{{ usuario?.nome }}</h3>
          </ion-label>
        </ion-item>
        <ion-item>
          <ion-icon slot="start" :icon="mailOutline" color="primary" />
          <ion-label>
            <p>E-mail</p>
            <h3>{{ usuario?.email }}</h3>
          </ion-label>
        </ion-item>
        <ion-item>
          <ion-icon slot="start" :icon="idCardOutline" color="primary" />
          <ion-label>
            <p>ID do usuário</p>
            <h3>#{{ usuario?.id }}</h3>
          </ion-label>
        </ion-item>
      </ion-list>

      <ion-button expand="block" color="danger" fill="outline" class="botao-grande sair" :disabled="saindo" @click="sair">
        <ion-icon slot="start" :icon="logOutOutline" /> Sair
      </ion-button>

      <p class="servidor">Servidor: {{ API_URL }}</p>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { computed, ref } from 'vue'
import { IonButton, IonContent, IonIcon, IonItem, IonLabel, IonList, IonPage, onIonViewWillEnter, useIonRouter } from '@ionic/vue'
import { idCardOutline, logOutOutline, mailOutline, personOutline } from 'ionicons/icons'
import { api, API_URL } from '@/services/api'
import { atualizarUsuario, limparSessao, sessao } from '@/services/sessao'
import { confirmar } from '@/services/avisos'
import { iniciais } from '@/services/formato'

const ionRouter = useIonRouter()
const usuario = computed(() => sessao.usuario)
const saindo = ref(false)

// Busca os dados atualizados do usuário logado na API.
onIonViewWillEnter(() => {
  api.eu().then(atualizarUsuario).catch(() => {})
})

async function sair() {
  if (!(await confirmar('Sair', 'Deseja encerrar sua sessão?', 'Sair'))) return
  saindo.value = true
  try {
    await api.logout()
  } catch {
    // mesmo sem internet, a sessão local é encerrada
  }
  await limparSessao()
  saindo.value = false
  ionRouter.navigate('/login', 'root', 'replace')
}
</script>

<style scoped>
.topo {
  padding-top: 8px;
  margin-bottom: 12px;
}
.perfil {
  text-align: center;
  padding: 28px 16px 22px;
  margin-bottom: 16px;
}
.avatar {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  margin: 0 auto 12px;
  display: grid;
  place-items: center;
  font-size: 30px;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
}
.perfil h2 {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 800;
}
.perfil p {
  margin: 0;
  color: var(--ion-color-medium);
}
ion-label h3 {
  font-size: 15px;
  font-weight: 600;
}
.sair {
  margin-top: 24px;
}
.servidor {
  text-align: center;
  font-size: 11px;
  color: #a3a7b6;
  margin-top: 16px;
  word-break: break-all;
}
</style>
