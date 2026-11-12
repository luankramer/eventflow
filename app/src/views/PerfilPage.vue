<template>
  <ion-page>
    <ion-content>
      <header class="hero perfil">
        <span class="luz-ipe" />
        <div class="avatar">
          <span v-if="usuario">{{ iniciais(usuario.nome) }}</span>
          <span v-else><ion-icon :icon="person" /></span>
        </div>
        <h1>{{ usuario ? usuario.nome : 'Visitante' }}</h1>
        <p>{{ usuario ? usuario.email : 'Você está vendo os eventos sem entrar.' }}</p>
      </header>

      <div v-if="!usuario" class="conteudo">
        <section class="convite cartao">
          <h2>Entre para organizar eventos</h2>
          <p>Com uma conta você cadastra e edita eventos, categorias e locais.</p>
          <ion-button expand="block" class="botao-grande" router-link="/login?voltar=/tabs/perfil">
            <ion-icon slot="start" :icon="logInOutline" /> Entrar ou criar conta
          </ion-button>
        </section>
      </div>

      <div v-else class="conteudo">
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

      <footer class="rodape">
        <MarcaEventFlow :tamanho="34" />
        <span>Versão {{ VERSAO }}</span>
      </footer>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { computed, ref } from 'vue'
import { IonButton, IonContent, IonIcon, IonItem, IonLabel, IonList, IonPage, onIonViewWillEnter, useIonRouter } from '@ionic/vue'
import { idCardOutline, logInOutline, logOutOutline, mailOutline, person, personOutline } from 'ionicons/icons'
import { api, API_URL } from '@/services/api'
import { atualizarUsuario, limparSessao, sessao } from '@/services/sessao'
import { confirmar } from '@/services/avisos'
import { iniciais } from '@/services/formato'
import MarcaEventFlow from '@/components/MarcaEventFlow.vue'

const VERSAO = __APP_VERSION__

const ionRouter = useIonRouter()
const usuario = computed(() => sessao.usuario)
const saindo = ref(false)

// Busca os dados atualizados do usuário logado na API.
onIonViewWillEnter(() => {
  if (sessao.token) api.eu().then(atualizarUsuario).catch(() => {})
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
.avatar ion-icon {
  font-size: 40px;
  color: rgba(255, 255, 255, 0.85);
}
.convite {
  margin-top: 20px;
  padding: 22px 18px 18px;
  text-align: center;
}
.convite h2 {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.3px;
}
.convite p {
  margin: 0 0 18px;
  color: var(--ion-color-medium);
  font-size: 15px;
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
.rodape {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 0 28px;
  opacity: 0.8;
}
.rodape span {
  font-size: 11px;
  color: #a69fb8;
}
.servidor {
  text-align: center;
  font-size: 11px;
  color: #a69fb8;
  margin-top: 16px;
  word-break: break-all;
}
</style>
