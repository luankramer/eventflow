// Sessão do usuário: token JWT + dados do usuário, salvos no aparelho com Capacitor Preferences.
// Fica salva entre aberturas do app até o usuário tocar em "Sair".
import { reactive } from 'vue'
import { Preferences } from '@capacitor/preferences'

const CHAVE = 'eventflow.sessao'

export const sessao = reactive({
  token: null,
  usuario: null,
  carregada: false,
})

export async function carregarSessao() {
  if (sessao.carregada) return
  try {
    const { value } = await Preferences.get({ key: CHAVE })
    if (value) {
      const dados = JSON.parse(value)
      sessao.token = dados.token ?? null
      sessao.usuario = dados.usuario ?? null
    }
  } catch {
    // sessão corrompida: começa deslogado
  }
  sessao.carregada = true
}

export async function salvarSessao(token, usuario) {
  sessao.token = token
  sessao.usuario = usuario
  await Preferences.set({ key: CHAVE, value: JSON.stringify({ token, usuario }) })
}

export async function atualizarUsuario(usuario) {
  sessao.usuario = usuario
  await Preferences.set({ key: CHAVE, value: JSON.stringify({ token: sessao.token, usuario }) })
}

export async function limparSessao() {
  sessao.token = null
  sessao.usuario = null
  await Preferences.remove({ key: CHAVE })
}

export const estaLogado = () => Boolean(sessao.token)
