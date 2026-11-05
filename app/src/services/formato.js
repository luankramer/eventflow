// Formatação no padrão brasileiro.
const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export function formatarPreco(valor) {
  const n = Number(valor)
  if (!n) return 'Gratuito'
  return moeda.format(n)
}

// A API manda "2026-12-10"; convertemos sem passar por fuso horário.
export function formatarData(iso) {
  if (!iso) return ''
  const [a, m, d] = iso.slice(0, 10).split('-')
  return `${d}/${m}/${a}`
}

const DIAS = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb']
const MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

export function partesData(iso) {
  const [a, m, d] = iso.slice(0, 10).split('-').map(Number)
  const dt = new Date(a, m - 1, d)
  return { dia: String(d).padStart(2, '0'), mes: MESES[m - 1], semana: DIAS[dt.getDay()] }
}

export function formatarDataLonga(iso) {
  if (!iso) return ''
  const [a, m, d] = iso.slice(0, 10).split('-').map(Number)
  return new Date(a, m - 1, d).toLocaleDateString('pt-BR', {
    weekday: 'long', day: '2-digit', month: 'long', year: 'numeric',
  })
}

export function formatarHora(hora) {
  return hora ? hora.slice(0, 5) : ''
}

export function iniciais(nome = '') {
  const partes = nome.trim().split(/\s+/).filter(Boolean)
  if (!partes.length) return '?'
  const primeira = partes[0][0]
  const ultima = partes.length > 1 ? partes[partes.length - 1][0] : ''
  return (primeira + ultima).toUpperCase()
}
