// Camada única de mapa usada pelas telas (Mapa, Detalhes do evento e Cadastro de local).
//
// - Com VITE_GOOGLE_MAPS_KEY definida: usa o Google Maps (Maps JavaScript API).
// - Sem chave, ou se a chave falhar: usa Leaflet + OpenStreetMap (gratuito, sem chave).
// As telas não sabem qual provedor está em uso: falam só com o objeto que criarMapa() devolve.
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

export const CENTRO_PADRAO = [-9.9747, -67.8076] // Rio Branco - AC

const CHAVE_GOOGLE = (import.meta.env.VITE_GOOGLE_MAPS_KEY || '').trim()
const EVENTO_FALHA = 'ef-mapa-google-falhou'
let googleFalhou = false
let carregandoGoogle = null

// ---------------------------------------------------------------- pino (HTML/CSS em theme.css)
function htmlPino({ cor = '#E8175D', quantidade = 0, selecionado = false } = {}) {
  // O pino é montado como HTML: aceita só cor hexadecimal e número, nunca texto livre.
  if (!/^#[0-9a-fA-F]{6}$/.test(cor)) cor = '#E8175D'
  quantidade = Number.parseInt(quantidade, 10) || 0
  const badge = quantidade > 1 ? `<span class="pino-badge">${quantidade}</span>` : ''
  return `<div class="pino${selecionado ? ' pino-ativo' : ''}" style="--pino-cor:${cor}"><span class="pino-ponto"></span>${badge}</div>`
}
const PINO_LARGURA = 36
const PINO_ALTURA = 44
const PINO_PONTA = 42 // distância do topo até a ponta do pino

/** Link oficial do Google Maps (Maps URLs, não precisa de chave): abre a rota no app do Google Maps. */
export function linkRotaGoogleMaps(latitude, longitude) {
  return `https://www.google.com/maps/dir/?api=1&destination=${latitude}%2C${longitude}`
}

/** Avisa a tela quando a chave do Google for recusada, para ela recriar o mapa com OpenStreetMap. */
export function aoFalharGoogle(callback) {
  window.addEventListener(EVENTO_FALHA, callback)
  return () => window.removeEventListener(EVENTO_FALHA, callback)
}

export async function criarMapa(elemento, opcoes = {}) {
  if (CHAVE_GOOGLE && !googleFalhou) {
    try {
      await carregarGoogle()
      return criarMapaGoogle(elemento, opcoes)
    } catch {
      googleFalhou = true
    }
  }
  return criarMapaOsm(elemento, opcoes)
}

// ================================================================= Google Maps
function carregarGoogle() {
  if (window.google?.maps?.Map) return Promise.resolve()
  if (carregandoGoogle) return carregandoGoogle
  carregandoGoogle = new Promise((resolve, reject) => {
    // chamada pelo Google quando a chave é inválida ou não autorizada
    window.gm_authFailure = () => {
      googleFalhou = true
      window.dispatchEvent(new Event(EVENTO_FALHA))
    }
    window.__efGoogleMapsPronto = () => resolve()
    const script = document.createElement('script')
    const params = new URLSearchParams({
      key: CHAVE_GOOGLE,
      v: 'weekly',
      language: 'pt-BR',
      region: 'BR',
      loading: 'async',
      callback: '__efGoogleMapsPronto',
    })
    script.src = `https://maps.googleapis.com/maps/api/js?${params}`
    script.async = true
    script.onerror = () => reject(new Error('Não foi possível carregar o Google Maps'))
    document.head.appendChild(script)
    setTimeout(() => reject(new Error('Tempo esgotado ao carregar o Google Maps')), 15000)
  }).catch((erro) => {
    carregandoGoogle = null
    throw erro
  })
  return carregandoGoogle
}

// Visual mais limpo: esconde comércios e ícones de pontos de interesse que competem com os pinos.
const ESTILO_GOOGLE = [
  { featureType: 'poi.business', stylers: [{ visibility: 'off' }] },
  { featureType: 'poi', elementType: 'labels.icon', stylers: [{ visibility: 'off' }] },
  { featureType: 'transit', elementType: 'labels.icon', stylers: [{ visibility: 'off' }] },
]

let ClassePinoGoogle = null
function classePinoGoogle() {
  if (ClassePinoGoogle) return ClassePinoGoogle
  const g = window.google.maps

  // Marcador em HTML desenhado sobre o mapa (OverlayView), para reaproveitar o pino do app.
  ClassePinoGoogle = class PinoGoogle extends g.OverlayView {
    constructor(mapa, { lat, lng, aoClicar, arrastavel, aoArrastar, ...visual }) {
      super()
      this.posicao = new g.LatLng(lat, lng)
      this.aoClicar = aoClicar
      this.arrastavel = arrastavel
      this.aoArrastar = aoArrastar
      this.div = document.createElement('div')
      this.div.style.cssText = `position:absolute;width:${PINO_LARGURA}px;height:${PINO_ALTURA}px;cursor:pointer;touch-action:none;`
      this.div.innerHTML = htmlPino(visual)
      g.OverlayView.preventMapHitsAndGesturesFrom(this.div)
      this.div.addEventListener('click', (e) => {
        e.stopPropagation()
        if (!this.arrastou) this.aoClicar?.()
        this.arrastou = false
      })
      if (arrastavel) this.ligarArraste()
      this.setMap(mapa)
    }

    ligarArraste() {
      const g = window.google.maps
      this.div.addEventListener('pointerdown', (e) => {
        e.preventDefault()
        this.div.setPointerCapture(e.pointerId)
        // distância entre o dedo e a ponta do pino, para a ponta acompanhar o dedo
        const r = this.div.getBoundingClientRect()
        this.ajusteX = r.left + PINO_LARGURA / 2 - e.clientX
        this.ajusteY = r.top + PINO_PONTA - e.clientY
        this.arrastando = true
        this.arrastou = false
      })
      this.div.addEventListener('pointermove', (e) => {
        if (!this.arrastando) return
        const caixa = this.getMap().getDiv().getBoundingClientRect()
        const ponto = new g.Point(e.clientX - caixa.left + this.ajusteX, e.clientY - caixa.top + this.ajusteY)
        const pos = this.getProjection().fromContainerPixelToLatLng(ponto)
        if (pos) {
          this.arrastou = true
          this.posicao = pos
          this.draw()
        }
      })
      const soltar = () => {
        if (!this.arrastando) return
        this.arrastando = false
        if (this.arrastou) this.aoArrastar?.(this.posicao.lat(), this.posicao.lng())
      }
      this.div.addEventListener('pointerup', soltar)
      this.div.addEventListener('pointercancel', soltar)
    }

    onAdd() {
      this.getPanes().overlayMouseTarget.appendChild(this.div)
    }

    draw() {
      const p = this.getProjection()?.fromLatLngToDivPixel(this.posicao)
      if (!p) return
      this.div.style.left = `${p.x - PINO_LARGURA / 2}px`
      this.div.style.top = `${p.y - PINO_PONTA}px`
    }

    onRemove() {
      this.div.remove()
    }
  }
  return ClassePinoGoogle
}

function criarMapaGoogle(elemento, { centro = CENTRO_PADRAO, zoom = 13, interativo = true } = {}) {
  const g = window.google.maps
  const mapa = new g.Map(elemento, {
    center: { lat: centro[0], lng: centro[1] },
    zoom,
    disableDefaultUI: true,
    zoomControl: interativo,
    clickableIcons: false,
    gestureHandling: interativo ? 'greedy' : 'none',
    keyboardShortcuts: interativo,
    styles: ESTILO_GOOGLE,
  })
  const Pino = classePinoGoogle()
  const pinos = new Set()

  return {
    provedor: 'google',
    marcador(dados) {
      const pino = new Pino(mapa, dados)
      pinos.add(pino)
      return {
        mover(lat, lng) {
          pino.posicao = new g.LatLng(lat, lng)
          pino.draw()
        },
        remover() {
          pino.setMap(null)
          pinos.delete(pino)
        },
      }
    },
    limpar() {
      pinos.forEach((p) => p.setMap(null))
      pinos.clear()
    },
    centralizar(lat, lng, z) {
      mapa.setCenter({ lat, lng })
      if (z) mapa.setZoom(z)
    },
    deslizar(lat, lng) {
      mapa.panTo({ lat, lng })
    },
    enquadrar(pontos, { margem = 60, zoomMax = 15 } = {}) {
      if (!pontos.length) return
      const limites = new g.LatLngBounds()
      pontos.forEach(([lat, lng]) => limites.extend({ lat, lng }))
      mapa.fitBounds(limites, margem)
      g.event.addListenerOnce(mapa, 'idle', () => {
        if (mapa.getZoom() > zoomMax) mapa.setZoom(zoomMax)
      })
    },
    aoClicar(callback) {
      mapa.addListener('click', (e) => callback(e.latLng.lat(), e.latLng.lng()))
    },
    zoom: () => mapa.getZoom(),
    atualizarTamanho() {
      g.event.trigger(mapa, 'resize')
    },
    destruir() {
      this.limpar()
      g.event.clearInstanceListeners(mapa)
      elemento.innerHTML = ''
    },
  }
}

// ================================================================= Leaflet + OpenStreetMap
const FONTES_OSM = [
  {
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    opcoes: { maxZoom: 19, attribution: '© OpenStreetMap' },
  },
  {
    // reserva: servidor comunitário OSM França (estilo humanitário)
    url: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    opcoes: { maxZoom: 19, subdomains: 'abc', attribution: '© OpenStreetMap · OSM France' },
  },
]

function adicionarMapaBase(mapa, indice = 0) {
  const fonte = FONTES_OSM[indice]
  const camada = L.tileLayer(fonte.url, fonte.opcoes)
  let falhas = 0
  camada.on('tileerror', () => {
    falhas += 1
    if (falhas === 4 && indice + 1 < FONTES_OSM.length) {
      mapa.removeLayer(camada)
      adicionarMapaBase(mapa, indice + 1)
    }
  })
  camada.addTo(mapa)
}

function iconeLeaflet(visual) {
  return L.divIcon({
    className: '',
    html: htmlPino(visual),
    iconSize: [PINO_LARGURA, PINO_ALTURA],
    iconAnchor: [PINO_LARGURA / 2, PINO_PONTA],
  })
}

function criarMapaOsm(elemento, { centro = CENTRO_PADRAO, zoom = 13, interativo = true } = {}) {
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
  mapa.attributionControl.setPrefix(false)
  adicionarMapaBase(mapa)
  if (interativo) L.control.zoom({ position: 'bottomright' }).addTo(mapa)
  const camada = L.layerGroup().addTo(mapa)

  return {
    provedor: 'osm',
    marcador({ lat, lng, aoClicar, arrastavel, aoArrastar, ...visual }) {
      const m = L.marker([lat, lng], { icon: iconeLeaflet(visual), draggable: Boolean(arrastavel) })
      if (aoClicar) {
        m.on('click', (ev) => {
          L.DomEvent.stopPropagation(ev)
          aoClicar()
        })
      }
      if (aoArrastar) {
        m.on('dragend', () => {
          const p = m.getLatLng()
          aoArrastar(p.lat, p.lng)
        })
      }
      m.addTo(camada)
      return {
        mover: (la, ln) => m.setLatLng([la, ln]),
        remover: () => camada.removeLayer(m),
      }
    },
    limpar: () => camada.clearLayers(),
    centralizar: (lat, lng, z) => mapa.setView([lat, lng], z ?? mapa.getZoom()),
    deslizar: (lat, lng) => mapa.panTo([lat, lng], { animate: true }),
    enquadrar(pontos, { margem = 60, zoomMax = 15 } = {}) {
      if (!pontos.length) return
      mapa.fitBounds(L.latLngBounds(pontos), { padding: [margem, margem], maxZoom: zoomMax })
    },
    aoClicar: (callback) => mapa.on('click', (e) => callback(e.latlng.lat, e.latlng.lng)),
    zoom: () => mapa.getZoom(),
    atualizarTamanho: () => mapa.invalidateSize(),
    destruir: () => mapa.remove(),
  }
}
