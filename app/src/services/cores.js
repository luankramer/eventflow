// Cor e ícone de cada categoria. A cor é fixa pelo id da categoria,
// então "Música" tem sempre a mesma cor no chip, no ingresso e no pino do mapa.
import {
  basketballOutline, colorPaletteOutline, hardwareChipOutline, libraryOutline, micOutline,
  musicalNotesOutline, restaurantOutline, sparklesOutline, ticketOutline, beerOutline, leafOutline,
} from 'ionicons/icons'

export const PALETA = [
  { nome: 'pitaya', cor: '#E8175D', texto: '#B0104A', suave: '#FDE7EF', escura: '#8E0B3B' },
  { nome: 'ipe', cor: '#FFB800', texto: '#8A5A00', suave: '#FFF3D1', escura: '#B87F00', tinta: '#1E1036' },
  { nome: 'rio', cor: '#12B5A5', texto: '#0A7A6F', suave: '#DCF5F2', escura: '#0A7A6F' },
  { nome: 'acai', cor: '#6B2FA8', texto: '#5A2690', suave: '#EFE5FA', escura: '#3F1A66' },
  { nome: 'coral', cor: '#FF6B4A', texto: '#C23E1F', suave: '#FFE9E3', escura: '#B2381C' },
  { nome: 'azul', cor: '#2F6BFF', texto: '#1F4FCC', suave: '#E4ECFF', escura: '#1A3F9E' },
]

// `tinta` é a cor do texto sobre `cor`: branco, exceto no amarelo-ipê (contraste).
export function corCategoria(categoria) {
  const id = Number(categoria?.id ?? 0)
  const c = PALETA[Math.abs(id - 1) % PALETA.length]
  return { tinta: '#FFFFFF', ...c }
}

const ICONES = [
  [/m[uú]sic|show|banda|rock|samba|forr[oó]/i, musicalNotesOutline],
  [/gastro|comida|culin|food|feira/i, restaurantOutline],
  [/esport|corrida|futebol|jogo|fitness/i, basketballOutline],
  [/tecno|programa|dev|hack|ti\b/i, hardwareChipOutline],
  [/teatro|dan[cç]a|arte|cultura|exposi/i, colorPaletteOutline],
  [/palestra|semin|confer|workshop|curso/i, micOutline],
  [/educa|livro|leitura|literat/i, libraryOutline],
  [/festa|balada|night/i, sparklesOutline],
  [/bar|cerveja|chopp/i, beerOutline],
  [/natur|ecolog|trilha|meio ambiente/i, leafOutline],
]

export function iconeCategoria(categoria) {
  const nome = categoria?.nome || ''
  return ICONES.find(([re]) => re.test(nome))?.[1] ?? ticketOutline
}
