// Mapa com Leaflet + mapa base gratuito (OpenStreetMap / CARTO), sem chave de API.
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

export const CENTRO_PADRAO = [-9.9747, -67.8076] // Rio Branco - AC

export function criarMapa(elemento, { centro = CENTRO_PADRAO, zoom = 13, interativo = true } = {}) {
  const mapa = L.map(elemento, {
    zoomControl: false,
    attributionControl: true,
    dragging: interativo,
    touchZoom: interativo,
    scrollWheelZoom: interativo,
    doubleClickZoom: interativo,
    boxZoom: interativo,
    keyboard: interativo,
  }).setView(centro, zoom)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd',
    attribution: '© OpenStreetMap · © CARTO',
  }).addTo(mapa)

  if (interativo) L.control.zoom({ position: 'bottomright' }).addTo(mapa)
  return mapa
}

/** Marcador em formato de "pino", desenhado em CSS (classe .pino no theme.css). */
export function iconePino({ quantidade = 0, selecionado = false } = {}) {
  const badge = quantidade > 1 ? `<span class="pino-badge">${quantidade}</span>` : ''
  return L.divIcon({
    className: '',
    html: `<div class="pino${selecionado ? ' pino-ativo' : ''}"><span class="pino-ponto"></span>${badge}</div>`,
    iconSize: [34, 42],
    iconAnchor: [17, 40],
  })
}

export { L }
