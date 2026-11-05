<template>
  <ion-page>
    <ion-content>
      <header class="hero perfil">
        <span class="luz-ipe" />
        <div class="avatar"><span>{{ iniciais(usuario?.nome) }}</span></div>
        <h1>{{ usuario?.nome }}</h1>
        <p>{{ usuario?.email }}</p>
      </header>

      <div class="conteudo">
      <h2 class="titulo-secao">Seus dados</h2>
      <ion-list class="lista-cartao" lines="full">
        <ion-item>
          <div slot="start" class="icone-item pitaya"><ion-icon :icon="personOutline" /></div>
          <ion-label>
            <p>Nome</p>
            <h3>{{ usuario?.nome }}</h3>
          </ion-label>
        </ion-item>
        <ion-item>
          <div slot="start" class="icone-item acai"><ion-icon :icon="mailOutline" /></div>
          <ion-label>
            <p>E-mail</p>
            <h3>{{ usuario?.email }}</h3>
          </ion-label>
        </ion-item>
        <ion-item>
          <div slot="start" class="icone-item rio"><ion-icon :icon="idCardOutline" /></div>
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
      </div>
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
.perfil {
  text-align: center;
  padding-bottom: 34px;
}
.avatar {
  width: 96px;
  height: 96px;
  margin: 6px auto 14px;
  border-radius: 50%;
  padding: 4px;
  background: conic-gradient(from 200deg, var(--ef-ipe), var(--ef-pitaya), var(--ef-acai), var(--ef-ipe));
}
.avatar span {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--ef-noite);
  border: 3px solid var(--ef-noite);
  font-family: var(--ef-fonte-titulo);
  font-size: 34px;
  font-weight: 800;
  color: #fff;
  letter-spacing: -1px;
}
.perfil h1 {
  font-size: 26px;
  margin-bottom: 4px;
}
.conteudo {
  padding: 4px 16px 32px;
}
.icone-item {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 18px;
  margin-right: 4px;
}
.icone-item.pitaya {
  background: #fde7ef;
  color: var(--ef-pitaya);
}
.icone-item.acai {
  background: #efe5fa;
  color: var(--ef-acai);
}
.icone-item.rio {
  background: #dcf5f2;
  color: #0a7a6f;
}
ion-label p {
  font-size: 12px;
}
ion-label h3 {
  font-size: 16px;
  font-weight: 700;
}
.sair {
  margin-top: 24px;
  --border-width: 2px;
}
.servidor {
  text-align: center;
  font-size: 11px;
  color: #a69fb8;
  margin-top: 16px;
  word-break: break-all;
}
</style>
