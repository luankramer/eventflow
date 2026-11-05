import { alertController, toastController } from '@ionic/vue'

export async function avisar(mensagem, cor = 'dark') {
  const toast = await toastController.create({
    message: mensagem,
    duration: 2600,
    position: 'top',
    color: cor,
  })
  await toast.present()
}

export const avisarErro = (erro) => avisar(erro?.message || String(erro), 'danger')
export const avisarSucesso = (mensagem) => avisar(mensagem, 'success')

export async function confirmar(titulo, mensagem, textoConfirmar = 'Confirmar', destrutivo = true) {
  const alerta = await alertController.create({
    header: titulo,
    message: mensagem,
    buttons: [
      { text: 'Cancelar', role: 'cancel' },
      { text: textoConfirmar, role: 'confirm', cssClass: destrutivo ? 'botao-perigo' : '' },
    ],
  })
  await alerta.present()
  const { role } = await alerta.onDidDismiss()
  return role === 'confirm'
}
