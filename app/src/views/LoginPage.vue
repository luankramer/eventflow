<template>
  <ion-page>
    <ion-content class="ion-padding">
      <div class="login respeita-status">
        <div class="marca">
          <div class="logo"><ion-icon :icon="calendar" /></div>
          <h1>EventFlow</h1>
          <p>{{ modoCadastro ? 'Crie sua conta para começar' : 'Entre para ver e organizar seus eventos' }}</p>
        </div>

        <form class="formulario" @submit.prevent="enviar">
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
        </form>

        <p class="alternar">
          {{ modoCadastro ? 'Já tem conta?' : 'Ainda não tem conta?' }}
          <a href="#" @click.prevent="modoCadastro = !modoCadastro">
            {{ modoCadastro ? 'Entrar' : 'Criar conta' }}
          </a>
        </p>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import { IonButton, IonContent, IonIcon, IonInput, IonInputPasswordToggle, IonPage, IonSpinner, useIonRouter } from '@ionic/vue'
import { calendar } from 'ionicons/icons'
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
.login {
  max-width: 420px;
  margin: 0 auto;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px 4px;
}
.marca {
  text-align: center;
  margin-bottom: 32px;
}
.logo {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  margin: 0 auto 16px;
  display: grid;
  place-items: center;
  background: var(--ion-color-primary);
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.3);
}
.logo ion-icon {
  font-size: 36px;
  color: #fff;
}
.marca h1 {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.6px;
  margin: 0 0 6px;
}
.marca p {
  color: var(--ion-color-medium);
  margin: 0;
}
.formulario ion-button {
  margin-top: 8px;
}
.alternar {
  text-align: center;
  color: var(--ion-color-medium);
  margin-top: 24px;
  font-size: 14px;
}
.alternar a {
  color: var(--ion-color-primary);
  font-weight: 600;
  text-decoration: none;
}
</style>
