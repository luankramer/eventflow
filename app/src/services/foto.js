// Escolha da imagem do evento: câmera ou galeria.
// No celular usa o plugin de câmera do Capacitor; no navegador cai num seletor de arquivo.
import { Capacitor } from '@capacitor/core'
import { Camera, MediaTypeSelection } from '@capacitor/camera'
import { actionSheetController } from '@ionic/vue'
import { cameraOutline, imagesOutline, close } from 'ionicons/icons'

const OPCOES_IMAGEM = { quality: 75, targetWidth: 1280, targetHeight: 1280, correctOrientation: true }

function escolherArquivoNoNavegador() {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = () => resolve(input.files?.[0] ?? null)
    input.click()
  })
}

async function blobDoCaminho(webPath) {
  const resp = await fetch(webPath)
  return resp.blob()
}

/** Retorna { blob, previa } ou null se o usuário cancelar. */
export async function escolherFoto() {
  if (!Capacitor.isNativePlatform()) {
    const arquivo = await escolherArquivoNoNavegador()
    return arquivo ? { blob: arquivo, previa: URL.createObjectURL(arquivo) } : null
  }

  const folha = await actionSheetController.create({
    header: 'Imagem do evento',
    buttons: [
      { text: 'Tirar foto', icon: cameraOutline, data: 'camera' },
      { text: 'Escolher da galeria', icon: imagesOutline, data: 'galeria' },
      { text: 'Cancelar', icon: close, role: 'cancel' },
    ],
  })
  await folha.present()
  const { data } = await folha.onDidDismiss()
  if (!data) return null

  try {
    let resultado
    if (data === 'camera') {
      resultado = await Camera.takePhoto(OPCOES_IMAGEM)
    } else {
      const galeria = await Camera.chooseFromGallery({ ...OPCOES_IMAGEM, mediaType: MediaTypeSelection.Photo, limit: 1 })
      resultado = galeria.results?.[0]
    }
    if (!resultado?.webPath) return null
    return { blob: await blobDoCaminho(resultado.webPath), previa: resultado.webPath }
  } catch (erro) {
    const msg = String(erro?.message || erro).toLowerCase()
    if (msg.includes('cancel')) return null // usuário fechou a câmera/galeria
    throw new Error('Não foi possível obter a imagem. Verifique a permissão de câmera/fotos.')
  }
}
