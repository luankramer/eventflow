// Cores e ícones dos tipos de evento (categorias).
//
// Cada categoria tem uma cor e um ícone escolhidos no cadastro da categoria e salvos na API.
// Todo evento herda a cor e o ícone da sua categoria: chip, canhoto do ingresso,
// capa sem foto e pino do mapa. Assim a cor tem significado: identifica o tipo de evento.
import {
  balloonOutline, basketballOutline, beerOutline, briefcaseOutline, colorPaletteOutline, filmOutline,
  hardwareChipOutline, heartOutline, leafOutline, micOutline, musicalNotesOutline, peopleOutline,
  restaurantOutline, schoolOutline, sparklesOutline, ticketOutline,
} from 'ionicons/icons'

/** Cores oferecidas no cadastro de categoria. */
export const CORES = [
  { nome: 'Pitaya', hex: '#E8175D' },
  { nome: 'Coral', hex: '#FF5A3C' },
  { nome: 'Laranja', hex: '#F7810F' },
  { nome: 'Ipê', hex: '#FFB800' },
  { nome: 'Mata', hex: '#3E9B2F' },
  { nome: 'Rio', hex: '#12B5A5' },
  { nome: 'Céu', hex: '#0B9BE0' },
  { nome: 'Azul', hex: '#2F6BFF' },
  { nome: 'Índigo', hex: '#5145E5' },
  { nome: 'Açaí', hex: '#6B2FA8' },
  { nome: 'Orquídea', hex: '#C026D3' },
  { nome: 'Grafite', hex: '#4B5563' },
]

/** Ícones oferecidos no cadastro de categoria (a chave é o que vai para a API). */
export const ICONES = {
  ingresso: { icone: ticketOutline, rotulo: 'Geral' },
  musica: { icone: musicalNotesOutline, rotulo: 'Música' },
  gastronomia: { icone: restaurantOutline, rotulo: 'Gastronomia' },
  esporte: { icone: basketballOutline, rotulo: 'Esporte' },
  tecnologia: { icone: hardwareChipOutline, rotulo: 'Tecnologia' },
  arte: { icone: colorPaletteOutline, rotulo: 'Arte e cultura' },
  cinema: { icone: filmOutline, rotulo: 'Cinema' },
  palestra: { icone: micOutline, rotulo: 'Palestra' },
  educacao: { icone: schoolOutline, rotulo: 'Educação' },
  festa: { icone: sparklesOutline, rotulo: 'Festa' },
  bebidas: { icone: beerOutline, rotulo: 'Bar' },
  natureza: { icone: leafOutline, rotulo: 'Natureza' },
  infantil: { icone: balloonOutline, rotulo: 'Infantil' },
  negocios: { icone: briefcaseOutline, rotulo: 'Negócios' },
  saude: { icone: heartOutline, rotulo: 'Saúde' },
  comunidade: { icone: peopleOutline, rotulo: 'Comunidade' },
}

// ---------- utilidades de cor ----------
const paraRgb = (hex) => {
  const h = hex.replace('#', '')
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16))
}
const paraHex = (rgb) => '#' + rgb.map((v) => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, '0')).join('')
const misturar = (hex, alvo, peso) => {
  const a = paraRgb(hex)
  const b = paraRgb(alvo)
  return paraHex(a.map((v, i) => v + (b[i] - v) * peso))
}
function luminancia(hex) {
  const [r, g, b] = paraRgb(hex).map((v) => {
    const c = v / 255
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}
const contraste = (a, b) => {
  const [l1, l2] = [luminancia(a), luminancia(b)].sort((x, y) => y - x)
  return (l1 + 0.05) / (l2 + 0.05)
}

const cache = new Map()
/** A partir de uma cor, calcula os tons usados na interface. */
export function tons(hex) {
  if (cache.has(hex)) return cache.get(hex)
  const suave = misturar(hex, '#FFFFFF', 0.86)
  // cor de texto legível sobre o fundo suave (escurece até ter contraste AA)
  let texto = hex
  for (let p = 0; contraste(texto, suave) < 4.5 && p < 0.8; p += 0.05) texto = misturar(hex, '#1E1036', p)
  const resultado = {
    cor: hex,
    suave,
    texto,
    escura: misturar(hex, '#1E1036', 0.38),
    // cor do texto escrito em cima da cor (branco, ou escuro em cores claras como o amarelo)
    tinta: contraste('#FFFFFF', hex) >= 2.6 ? '#FFFFFF' : '#1E1036',
  }
  cache.set(hex, resultado)
  return resultado
}

/** Tons da categoria. Categorias antigas, sem cor salva, recebem uma cor pelo id. */
export function corCategoria(categoria) {
  const salva = categoria?.cor
  if (salva && /^#[0-9A-Fa-f]{6}$/.test(salva)) return tons(salva.toUpperCase())
  const id = Number(categoria?.id ?? 1)
  return tons(CORES[Math.abs(id - 1) % CORES.length].hex)
}

const PALAVRAS = [
  [/m[uú]sic|show|banda|rock|samba|forr[oó]/i, 'musica'],
  [/gastro|comida|culin|food|feira/i, 'gastronomia'],
  [/esport|corrida|futebol|jogo|fitness/i, 'esporte'],
  [/tecno|programa|dev|hack/i, 'tecnologia'],
  [/teatro|dan[cç]a|arte|cultura|exposi/i, 'arte'],
  [/cinema|filme/i, 'cinema'],
  [/palestra|semin|confer|workshop/i, 'palestra'],
  [/educa|curso|aula|livro/i, 'educacao'],
  [/festa|balada/i, 'festa'],
  [/bar|cerveja|chopp/i, 'bebidas'],
  [/natur|ecolog|trilha/i, 'natureza'],
  [/infantil|crian[cç]a/i, 'infantil'],
  [/neg[oó]cio|empreend/i, 'negocios'],
  [/sa[uú]de|bem-estar|yoga/i, 'saude'],
]

/** Sugere um ícone pelo nome digitado (usado no cadastro de categoria). */
export function sugerirIcone(nome = '') {
  return PALAVRAS.find(([re]) => re.test(nome))?.[1] ?? 'ingresso'
}

export function iconeCategoria(categoria) {
  const chave = categoria?.icone && ICONES[categoria.icone] ? categoria.icone : sugerirIcone(categoria?.nome)
  return ICONES[chave].icone
}

/** Primeira cor da paleta que ainda não está em uso. */
export function sugerirCor(categorias = []) {
  const usadas = new Set(categorias.map((c) => (c.cor || '').toUpperCase()))
  return (CORES.find((c) => !usadas.has(c.hex)) ?? CORES[0]).hex
}
