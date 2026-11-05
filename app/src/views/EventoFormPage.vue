<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button :default-href="editando ? `/eventos/${idEvento}` : '/tabs/eventos'" text="" />
        </ion-buttons>
        <ion-title>{{ editando ? 'Editar evento' : 'Novo evento' }}</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div v-if="carregandoDados" class="centro"><ion-spinner name="crescent" /></div>

      <form v-else class="formulario" @submit.prevent="salvar">
        <!-- Imagem -->
        <button type="button" class="seletor-imagem" :class="{ comImagem: previa }" @click="selecionarImagem">
          <img v-if="previa" :src="previa" alt="" />
          <div v-else class="placeholder">
            <ion-icon :icon="cameraOutline" />
            <strong>Adicionar imagem</strong>
            <span>Câmera ou galeria</span>
          </div>
          <span v-if="previa" class="trocar"><ion-icon :icon="cameraOutline" /> Trocar imagem</span>
        </button>

        <div>
          <label class="rotulo" for="nome">Nome do evento *</label>
          <ion-input id="nome" v-model="form.nome" fill="outline" placeholder="Ex.: Festival de Música" :maxlength="150" />
        </div>

        <div>
          <label class="rotulo" for="descricao">Descrição</label>
          <ion-textarea
            id="descricao"
            v-model="form.descricao"
            fill="outline"
            placeholder="Conte um pouco sobre o evento"
            :auto-grow="true"
            :rows="3"
          />
        </div>

        <div class="campo-grupo data-hora">
          <div>
            <span class="rotulo">Data *</span>
            <div class="campo-data">
              <ion-icon :icon="calendarOutline" class="icone-campo" />
              <ion-datetime-button :datetime="`data-${uid}`" />
            </div>
          </div>
          <div>
            <span class="rotulo">Hora *</span>
            <div class="campo-data">
              <ion-icon :icon="timeOutline" class="icone-campo" />
              <ion-datetime-button :datetime="`hora-${uid}`" />
            </div>
          </div>
        </div>

        <ion-modal :keep-contents-mounted="true">
          <ion-datetime
            :id="`data-${uid}`"
            presentation="date"
            locale="pt-BR"
            :value="dataHora"
            :show-default-buttons="true"
            done-text="OK"
            cancel-text="Cancelar"
            @ionChange="mudarDataHora"
          />
        </ion-modal>
        <ion-modal :keep-contents-mounted="true">
          <ion-datetime
            :id="`hora-${uid}`"
            presentation="time"
            locale="pt-BR"
            hour-cycle="h23"
            :value="dataHora"
            :show-default-buttons="true"
            done-text="OK"
            cancel-text="Cancelar"
            @ionChange="mudarDataHora"
          />
        </ion-modal>

        <div>
          <label class="rotulo" for="preco">Preço (R$)</label>
          <ion-input id="preco" v-model="form.preco" fill="outline" inputmode="decimal" placeholder="0,00 = gratuito">
            <span slot="start" class="prefixo">R$</span>
          </ion-input>
        </div>

        <div>
          <div class="rotulo-linha">
            <span class="rotulo">Categoria *</span>
            <router-link to="/categorias/nova" class="link-novo">+ Nova</router-link>
          </div>
          <ion-select
            v-model="form.categoria_id"
            fill="outline"
            interface="action-sheet"
            placeholder="Selecione a categoria"
            cancel-text="Cancelar"
            :interface-options="{ header: 'Categoria' }"
          >
            <ion-select-option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nome }}</ion-select-option>
          </ion-select>
        </div>

        <div>
          <div class="rotulo-linha">
            <span class="rotulo">Local *</span>
            <router-link to="/locais/novo" class="link-novo">+ Novo</router-link>
          </div>
          <ion-select
            v-model="form.local_id"
            fill="outline"
            interface="action-sheet"
            placeholder="Selecione o local"
            cancel-text="Cancelar"
            :interface-options="{ header: 'Local' }"
          >
            <ion-select-option v-for="l in locais" :key="l.id" :value="l.id">{{ l.nome }}</ion-select-option>
          </ion-select>
          <p class="dica">O local define onde o evento aparece no mapa.</p>
        </div>

        <ion-button type="submit" expand="block" class="botao-grande" :disabled="salvando">
          <ion-spinner v-if="salvando" name="crescent" />
          <span v-else>{{ editando ? 'Salvar alterações' : 'Cadastrar evento' }}</span>
        </ion-button>
      </form>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  IonBackButton, IonButton, IonButtons, IonContent, IonDatetime, IonDatetimeButton, IonHeader, IonIcon,
  IonInput, IonModal, IonPage, IonSelect, IonSelectOption, IonSpinner, IonTextarea, IonTitle, IonToolbar,
  onIonViewWillEnter, useIonRouter,
} from '@ionic/vue'
import { calendarOutline, cameraOutline, timeOutline } from 'ionicons/icons'
import { api } from '@/services/api'
import { voltarPara } from '@/services/navegacao'
import { avisar, avisarErro, avisarSucesso } from '@/services/avisos'
import { escolherFoto } from '@/services/foto'

const route = useRoute()
const ionRouter = useIonRouter()
const uid = Math.random().toString(36).slice(2, 8) // ids únicos para os seletores de data/hora

const idEvento = route.params.id
const editando = computed(() => Boolean(idEvento))

function amanhaAs19() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T19:00`
}

const form = reactive({ nome: '', descricao: '', preco: '', categoria_id: null, local_id: null, imagem_url: null })
const dataHora = ref(amanhaAs19())
const categorias = ref([])
const locais = ref([])
const previa = ref(null)
const novaImagem = ref(null) // blob ainda não enviado
const carregandoDados = ref(true)
const salvando = ref(false)

function mudarDataHora(ev) {
  const valor = ev.detail.value
  if (typeof valor === 'string') dataHora.value = valor.slice(0, 16)
}

async function carregarListas() {
  const [cats, locs] = await Promise.all([api.categorias(), api.locais()])
  categorias.value = cats
  locais.value = locs
}

async function carregarEvento() {
  const e = await api.evento(idEvento)
  Object.assign(form, {
    nome: e.nome,
    descricao: e.descricao || '',
    preco: Number(e.preco) ? Number(e.preco).toFixed(2).replace('.', ',') : '',
    categoria_id: e.categoria.id,
    local_id: e.local.id,
    imagem_url: e.imagem_url,
  })
  dataHora.value = `${e.data}T${e.hora.slice(0, 5)}`
  previa.value = e.imagem_url
}

onMounted(async () => {
  try {
    await Promise.all([carregarListas(), editando.value ? carregarEvento() : Promise.resolve()])
  } catch (erro) {
    avisarErro(erro)
  } finally {
    carregandoDados.value = false
  }
})

// Ao voltar de "+ Nova categoria"/"+ Novo local", atualiza as opções.
let primeiraEntrada = true
onIonViewWillEnter(() => {
  if (primeiraEntrada) {
    primeiraEntrada = false
    return
  }
  carregarListas().catch(() => {})
})

async function selecionarImagem() {
  try {
    const foto = await escolherFoto()
    if (!foto) return
    novaImagem.value = foto.blob
    previa.value = foto.previa
  } catch (erro) {
    avisarErro(erro)
  }
}

function lerPreco() {
  const texto = String(form.preco ?? '').trim().replace(/\s|R\$/g, '')
  if (!texto) return 0
  // aceita "1.250,50", "1250,50" e "1250.50"
  const normalizado = texto.includes(',') ? texto.replace(/\./g, '').replace(',', '.') : texto
  const n = Number(normalizado)
  return Number.isFinite(n) ? n : NaN
}

async function salvar() {
  if (salvando.value) return
  const preco = lerPreco()
  if (form.nome.trim().length < 2) return avisar('Informe o nome do evento.')
  if (Number.isNaN(preco) || preco < 0) return avisar('Preço inválido.')
  if (!form.categoria_id) return avisar('Selecione uma categoria.')
  if (!form.local_id) return avisar('Selecione um local.')

  salvando.value = true
  try {
    let imagemUrl = form.imagem_url
    if (novaImagem.value) {
      const tipo = novaImagem.value.type || 'image/jpeg'
      const ext = tipo.split('/')[1] || 'jpg'
      const { url } = await api.enviarImagem(novaImagem.value, `evento.${ext}`)
      imagemUrl = url
      form.imagem_url = url
      novaImagem.value = null
    }

    const dados = {
      nome: form.nome.trim(),
      descricao: form.descricao.trim() || null,
      data: dataHora.value.slice(0, 10),
      hora: dataHora.value.slice(11, 16),
      preco,
      categoria_id: form.categoria_id,
      local_id: form.local_id,
      imagem_url: imagemUrl,
    }

    if (editando.value) {
      await api.editarEvento(idEvento, dados)
      avisarSucesso('Evento atualizado.')
      voltarPara(ionRouter, `/eventos/${idEvento}`)
    } else {
      const criado = await api.criarEvento(dados)
      avisarSucesso('Evento cadastrado.')
      ionRouter.navigate(`/eventos/${criado.id}`, 'forward', 'replace')
    }
  } catch (erro) {
    avisarErro(erro)
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.centro {
  display: grid;
  place-items: center;
  height: 60%;
}
.seletor-imagem {
  position: relative;
  width: 100%;
  height: 180px;
  border-radius: var(--ef-raio);
  border: 2px dashed #c9cbe6;
  background: #fff;
  overflow: hidden;
  padding: 0;
  cursor: pointer;
  font: inherit;
}
.seletor-imagem.comImagem {
  border: 0;
}
.seletor-imagem img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--ion-color-medium);
}
.placeholder ion-icon {
  font-size: 36px;
  color: var(--ion-color-primary);
  margin-bottom: 4px;
}
.placeholder strong {
  color: var(--ion-text-color);
  font-size: 15px;
}
.placeholder span {
  font-size: 13px;
}
.trocar {
  position: absolute;
  right: 10px;
  bottom: 10px;
  background: rgba(17, 20, 45, 0.7);
  color: #fff;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.icone-campo {
  color: var(--ion-color-primary);
  font-size: 18px;
  margin-left: 6px;
}
.prefixo {
  color: var(--ion-color-medium);
  margin-right: 6px;
}
.rotulo-linha {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.link-novo {
  font-size: 13px;
  font-weight: 600;
  color: var(--ion-color-primary);
  text-decoration: none;
}
.dica {
  font-size: 12px;
  color: var(--ion-color-medium);
  margin: 6px 2px 0;
}
ion-button.botao-grande {
  margin-top: 8px;
}
</style>
