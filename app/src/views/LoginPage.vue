<template>
  <ion-page>
    <ion-content class="fundo-noite">
      <div class="luzes" aria-hidden="true"><span /><span /><span /></div>
      <div class="login respeita-status">
        <div class="marca">
          <div class="logo"><ion-icon :icon="ticket" /></div>
          <span class="nome-app">EventFlow</span>
          <h1>{{ modoCadastro ? 'Crie sua conta e comece a organizar' : 'Shows, feiras e festas num só lugar' }}</h1>
        </div>

        <form class="formulario cartao-login" @submit.prevent="enviar">
          <h2>{{ modoCadastro ? 'Criar conta' : 'Entrar' }}</h2>
          <ion-input
            v-if="modoCadastro"
            v-model="nome"
            label="Nome"
            label-placement="floating"
            fill="outline"
            autocomplete="name"
          />
          <ion-input
            v-model="email"
            type="email"
            label="E-mail"
            label-placement="floating"
            fill="outline"
            inputmode="email"
            autocomplete="email"
            autocapitalize="off"
          />
          <ion-input
            v-model="senha"
            type="password"
            label="Senha"
            label-placement="floating"
            fill="outline"
            autocomplete="current-password"
            @keyup.enter="enviar"
          >
            <ion-input-password-toggle slot="end" />
          </ion-input>

          <ion-button type="submit" expand="block" class="botao-grande" :disabled="carregando">
            <ion-spinner v-if="carregando" name="crescent" />
            <span v-else>{{ modoCadastro ? 'Criar conta' : 'Entrar' }}</span>
          </ion-button>
          <p class="alternar">
          {{ modoCadastro ? 'Já tem conta?' : 'Ainda não tem conta?' }}
          <a href="#" @click.prevent="modoCadastro = !modoCadastro">
            {{ modoCadastro ? 'Entrar' : 'Criar conta' }}
          </a>
          </p>
        </form>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { IonButton, IonContent, IonIcon, IonInput, IonInputPasswordToggle, IonPage, IonSpinner, toastController, useIonRouter } from '@ionic/vue'
import { ticket } from 'ionicons/icons'
import { api } from '@/services/api'
import { salvarSessao } from '@/services/sessao'
import { avisar, avisarErro } from '@/services/avisos'

const ionRouter = useIonRouter()
const modoCadastro = ref(false)
const nome = ref('')
const email = ref('')
const senha = ref('')
const carregando = ref(false)

async function enviar() {
  if (carregando.value) return
  if (!email.value.trim() || !senha.value) return avisar('Informe e-mail e senha.')
  if (modoCadastro.value && nome.value.trim().length < 2) return avisar('Informe seu nome.')

  carregando.value = true
  try {
    const resposta = modoCadastro.value
      ? await api.registrar(nome.value.trim(), email.value.trim(), senha.value)
      : await api.login(email.value.trim(), senha.value)
    await salvarSessao(resposta.access_token, resposta.usuario)
    toastController.dismiss().catch(() => {}) // fecha avisos de erro anteriores
    senha.value = ''
    ionRouter.navigate('/tabs/eventos', 'root', 'replace')
  } catch (erro) {
    avisarErro(erro)
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.fundo-noite {
  --background: var(--ef-noite);
}
.luzes span {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  pointer-events: none;
}
.luzes span:nth-child(1) {
  width: 280px;
  height: 280px;
  top: -90px;
  right: -110px;
  background: var(--ef-pitaya);
  opacity: 0.7;
}
.luzes span:nth-child(2) {
  width: 220px;
  height: 220px;
  top: 180px;
  left: -120px;
  background: var(--ef-acai);
  opacity: 0.8;
}
.luzes span:nth-child(3) {
  width: 160px;
  height: 160px;
  top: 90px;
  right: 30px;
  background: var(--ef-ipe);
  opacity: 0.35;
}
.login {
  position: relative;
  max-width: 440px;
  margin: 0 auto;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 24px 16px calc(var(--ion-safe-area-bottom, 0px) + 20px);
}
.marca {
  color: #fff;
  padding: 0 6px 26px;
}
.logo {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: linear-gradient(140deg, #ff3d7f, var(--ef-pitaya) 50%, var(--ef-acai));
  box-shadow: 0 12px 28px rgba(232, 23, 93, 0.45);
  transform: rotate(-8deg);
  margin-bottom: 22px;
}
.logo ion-icon {
  font-size: 30px;
  color: #fff;
  transform: rotate(8deg);
}
.nome-app {
  display: block;
  font-family: var(--ef-fonte-titulo);
  font-weight: 800;
  font-size: 18px;
  color: var(--ef-ipe);
  margin-bottom: 6px;
}
.marca h1 {
  font-size: 38px;
  font-weight: 800;
  line-height: 1.02;
  letter-spacing: -1.4px;
  margin: 0;
  max-width: 330px;
  font-variation-settings: 'wdth' 85;
}
.cartao-login {
  background: #fff;
  border-radius: 28px;
  padding: 24px 20px 18px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
}
.cartao-login h2 {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin: 0 0 2px;
}
.formulario ion-button {
  margin-top: 4px;
}
.alternar {
  text-align: center;
  color: var(--ion-color-medium);
  margin: 6px 0 0;
  font-size: 14px;
}
.alternar a {
  color: var(--ef-pitaya);
  font-weight: 700;
  text-decoration: none;
}
</style>
