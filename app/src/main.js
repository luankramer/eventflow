import { createApp } from 'vue'
import { IonicVue } from '@ionic/vue'

import App from './App.vue'
import router from './router'
import { api, definirAoPerderSessao } from './services/api'
import { atualizarUsuario, carregarSessao, limparSessao, sessao } from './services/sessao'
import { avisar } from './services/avisos'

/* CSS base do Ionic */
import '@ionic/vue/css/core.css'
import '@ionic/vue/css/normalize.css'
import '@ionic/vue/css/structure.css'
import '@ionic/vue/css/typography.css'
import '@ionic/vue/css/padding.css'
import '@ionic/vue/css/flex-utils.css'
import '@ionic/vue/css/display.css'
import '@ionic/vue/css/text-alignment.css'

/* Tema do EventFlow */
import './theme.css'

// Se o token expirar ou ficar inválido, a API responde 401: limpa a sessão e volta ao login.
definirAoPerderSessao(async () => {
  await limparSessao()
  await router.replace('/login')
  avisar('Sua sessão expirou. Entre novamente.')
})

const app = createApp(App)
  .use(IonicVue, { mode: 'md' })
  .use(router)

async function iniciar() {
  await carregarSessao()
  // Valida a sessão salva em segundo plano e atualiza os dados do usuário.
  if (sessao.token) {
    api.eu().then(atualizarUsuario).catch(() => {})
  }
  await router.isReady()
  app.mount('#app')
}

iniciar()
