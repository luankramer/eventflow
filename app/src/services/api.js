// Cliente da API do EventFlow. Todas as telas falam com o servidor por aqui.
import { sessao } from './sessao'

export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

const TIMEOUT_MS = 90000 // o servidor gratuito (Render) pode levar até ~1 min para "acordar"

let aoPerderSessao = () => {}
export function definirAoPerderSessao(callback) {
  aoPerderSessao = callback
}

export class ErroApi extends Error {
  constructor(mensagem, status = 0) {
    super(mensagem)
    this.status = status
  }
}

function mensagemDoErro(corpo, status) {
  const detalhe = corpo?.detail
  if (typeof detalhe === 'string') return detalhe
  if (Array.isArray(detalhe) && detalhe.length) {
    // erros de validação do FastAPI
    return detalhe
      .map((e) => {
        const campo = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : ''
        return campo && campo !== 'body' ? `${campo}: ${e.msg}` : e.msg
      })
      .join('\n')
  }
  return `Erro ${status} ao falar com o servidor.`
}

async function requisicao(metodo, caminho, { corpo, formData } = {}) {
  const headers = {}
  if (sessao.token) headers.Authorization = `Bearer ${sessao.token}`
  let body
  if (formData) {
    body = formData // o navegador define o Content-Type com o boundary
  } else if (corpo !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(corpo)
  }

  const controle = new AbortController()
  const timer = setTimeout(() => controle.abort(), TIMEOUT_MS)
  let resposta
  try {
    resposta = await fetch(`${API_URL}${caminho}`, { method: metodo, headers, body, signal: controle.signal })
  } catch {
    throw new ErroApi('Não foi possível conectar ao servidor. Verifique a internet e tente de novo em alguns segundos.')
  } finally {
    clearTimeout(timer)
  }

  if (resposta.status === 204) return null
  let dados = null
  try {
    dados = await resposta.json()
  } catch {
    dados = null
  }

  if (!resposta.ok) {
    if (resposta.status === 401 && sessao.token) aoPerderSessao()
    throw new ErroApi(mensagemDoErro(dados, resposta.status), resposta.status)
  }
  return dados
}

const montarQuery = (params = {}) => {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') q.append(k, v)
  })
  const s = q.toString()
  return s ? `?${s}` : ''
}

export const api = {
  // Autenticação
  login: (email, senha) => requisicao('POST', '/auth/login', { corpo: { email, senha } }),
  registrar: (nome, email, senha) => requisicao('POST', '/auth/registro', { corpo: { nome, email, senha } }),
  eu: () => requisicao('GET', '/auth/me'),
  logout: () => requisicao('POST', '/auth/logout'),

  // Eventos
  eventos: (params) => requisicao('GET', `/eventos${montarQuery(params)}`),
  evento: (id) => requisicao('GET', `/eventos/${id}`),
  criarEvento: (dados) => requisicao('POST', '/eventos', { corpo: dados }),
  editarEvento: (id, dados) => requisicao('PUT', `/eventos/${id}`, { corpo: dados }),
  excluirEvento: (id) => requisicao('DELETE', `/eventos/${id}`),

  // Categorias
  categorias: () => requisicao('GET', '/categorias'),
  categoria: (id) => requisicao('GET', `/categorias/${id}`),
  criarCategoria: (dados) => requisicao('POST', '/categorias', { corpo: dados }),
  editarCategoria: (id, dados) => requisicao('PUT', `/categorias/${id}`, { corpo: dados }),
  excluirCategoria: (id) => requisicao('DELETE', `/categorias/${id}`),

  // Locais
  locais: () => requisicao('GET', '/locais'),
  local: (id) => requisicao('GET', `/locais/${id}`),
  criarLocal: (dados) => requisicao('POST', '/locais', { corpo: dados }),
  editarLocal: (id, dados) => requisicao('PUT', `/locais/${id}`, { corpo: dados }),
  excluirLocal: (id) => requisicao('DELETE', `/locais/${id}`),

  // Upload de imagem
  enviarImagem: (blob, nomeArquivo) => {
    const form = new FormData()
    form.append('arquivo', blob, nomeArquivo)
    return requisicao('POST', '/upload', { formData: form })
  },
}
