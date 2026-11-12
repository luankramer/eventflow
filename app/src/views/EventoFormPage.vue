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

      <form v-else class="formulario" :style="estiloCor" @submit.prevent="salvar">
        <!-- Imagem -->
        <button type="button" class="seletor-imagem" :class="{ comImagem: previa }" @click="selecionarImagem">
          <img v-if="previa" :src="previa" alt="" />
          <div v-else class="placeholder">
            <span class="placeholder-icone"><ion-icon :icon="cameraOutline" /></span>
            <strong>Adicionar imagem</strong>
            <span>Tire uma foto ou escolha da galeria</span>
          </div>
          <span v-if="previa" class="trocar"><ion-icon :icon="cameraOutline" /> Trocar imagem</span>
        </button>

        <section class="bloco">
          <h2><ion-icon :icon="documentTextOutline" /> Informações</h2>
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
              placeholder="O que vai acontecer, atrações, o que levar…"
              :auto-grow="true"
              :rows="3"
            />
          </div>
        </section>

        <section class="bloco">
          <h2><ion-icon :icon="pricetagsOutline" /> Tipo de evento *</h2>
          <p class="explica">A cor e o ícone do evento vêm da categoria escolhida.</p>
          <div class="tipos" role="radiogroup" aria-label="Categoria">
            <button
              v-for="c in categorias"
              :key="c.id"
              type="button"
              role="radio"
              class="tipo"
              :class="{ ativo: form.categoria_id === c.id }"
              :aria-checked="form.categoria_id === c.id"
              :style="{ '--tipo': corCategoria(c).cor, '--tipo-suave': corCategoria(c).suave, '--tipo-texto': corCategoria(c).texto, '--tipo-tinta': corCategoria(c).tinta }"
              @click="form.categoria_id = c.id"
            >
              <ion-icon :icon="iconeCategoria(c)" /> {{ c.nome }}
            </button>
            <router-link to="/categorias/nova" class="tipo novo"><ion-icon :icon="add" /> Nova</router-link>
          </div>
        </section>

        <section class="bloco">
          <h2><ion-icon :icon="calendarOutline" /> Quando *</h2>
          <div class="campo-grupo data-hora">
            <div>
              <span class="rotulo">Data</span>
              <div class="campo-data">
                <ion-icon :icon="calendarOutline" class="icone-campo" />
                <ion-datetime-button :datetime="`data-${uid}`" />
              </div>
            </div>
            <div>
              <span class="rotulo">Hora</span>
              <div class="campo-data">
                <ion-icon :icon="timeOutline" class="icone-campo" />
                <ion-datetime-button :datetime="`hora-${uid}`" />
              </div>
            </div>
          </div>
        </section>

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

        <section class="bloco">
          <h2><ion-icon :icon="locationOutline" /> Onde *</h2>
          <div class="rotulo-linha">
            <span class="rotulo">Local</span>
            <router-link to="/locais/novo" class="link-novo">+ Novo local</router-link>
          </div>
          <ion-select
            v-model="form.local_id"
            fill="outline"
            interface="action-sheet"
            placeholder="Selecione o local"
            cancel-text="Cancelar"
            :interface-options="{ header: 'Local do evento' }"
          >
            <ion-select-option v-for="l in locais" :key="l.id" :value="l.id">{{ l.nome }}</ion-select-option>
          </ion-select>
          <p class="explica">É pelo local que o evento aparece no mapa.</p>
        </section>

        <section class="bloco">
          <h2><ion-icon :icon="cashOutline" /> Preço</h2>
          <div class="preco-linha">
            <ion-input id="preco" v-model="form.preco" fill="outline" inputmode="decimal" placeholder="0,00">
              <span slot="start" class="prefixo">R$</span>
            </ion-input>
            <button type="button" class="gratuito-botao" :class="{ ativo: ehGratuito }" @click="form.preco = ''">
              <ion-icon :icon="ehGratuito ? checkmarkCircle : ellipseOutline" /> Gratuito
            </button>
          </div>
        </section>
      </form>
    </ion-content>

    <ion-footer v-if="!carregandoDados" class="ion-no-border rodape">
      <ion-button expand="block" class="botao-grande" :disabled="salvando" @click="salvar">
        <ion-spinner v-if="salvando" name="crescent" />
        <span v-else>{{ editando ? 'Salvar alterações' : 'Cadastrar evento' }}</span>
      </ion-button>
    </ion-footer>
  </ion-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  IonBackButton, IonButton, IonButtons, IonContent, IonDatetime, IonDatetimeButton, IonFooter, IonHeader, IonIcon,
  IonInput, IonModal, IonPage, IonSelect, IonSelectOption, IonSpinner, IonTextarea, IonTitle, IonToolbar,
  onIonViewWillEnter, useIonRouter,
} from '@ionic/vue'
import {
  add, calendarOutline, cameraOutline, cashOutline, checkmarkCircle, documentTextOutline, ellipseOutline,
  locationOutline, pricetagsOutline, timeOutline,
} from 'ionicons/icons'
import { corCategoria, iconeCategoria } from '@/services/cores'
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

const categoriaAtual = computed(() => categorias.value.find((c) => c.id === form.categoria_id))
// O formulário assume a cor da categoria escolhida (botões e destaques).
const estiloCor = computed(() => {
  const c = corCategoria(categoriaAtual.value ?? { cor: '#E8175D' })
  return { '--cat': c.cor, '--cat-suave': c.suave }
})
const ehGratuito = computed(() => !String(form.preco ?? '').trim() || lerPreco() === 0)

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
.formulario {
  padding-bottom: 12px;
}
.bloco {
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.bloco h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 17px;
  font-weight: 700;
}
.bloco h2 ion-icon {
  color: var(--cat);
  font-size: 19px;
  transition: color 0.2s;
}
.explica {
  margin: -6px 0 0;
  font-size: 13px;
  color: var(--ion-color-medium);
}
.bloco .explica:last-child {
  margin: -4px 2px 0;
  font-size: 12px;
}

/* imagem */
.seletor-imagem {
  position: relative;
  width: 100%;
  height: 190px;
  border-radius: 22px;
  border: 2px dashed color-mix(in srgb, var(--cat) 45%, #ffffff);
  background: color-mix(in srgb, var(--cat-suave) 60%, #ffffff);
  overflow: hidden;
  padding: 0;
  cursor: pointer;
  font: inherit;
  transition: border-color 0.2s, background 0.2s;
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
  gap: 3px;
  color: var(--ion-color-medium);
}
.placeholder-icone {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: var(--cat);
  color: #fff;
  font-size: 24px;
  margin-bottom: 8px;
  transition: background 0.2s;
}
.placeholder strong {
  color: var(--ion-text-color);
  font-size: 16px;
}
.placeholder span {
  font-size: 13px;
}
.trocar {
  position: absolute;
  right: 10px;
  bottom: 10px;
  background: rgba(30, 16, 54, 0.72);
  color: #fff;
  border-radius: 999px;
  padding: 7px 13px;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* tipo de evento */
.tipos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tipo {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 13px 9px 10px;
  border-radius: 999px;
  border: 1.5px solid var(--tipo-suave);
  background: var(--tipo-suave);
  color: var(--tipo-texto);
  font: 700 14px/1 var(--ef-fonte);
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.tipo ion-icon {
  font-size: 17px;
}
.tipo.ativo {
  background: var(--tipo);
  border-color: var(--tipo);
  color: var(--tipo-tinta);
  box-shadow: 0 6px 14px color-mix(in srgb, var(--tipo) 35%, transparent);
}
.tipo.novo {
  background: #fff;
  border: 1.5px dashed #cfc6df;
  color: var(--ef-tinta-2);
}
.tipo:focus-visible {
  outline: 3px solid var(--ef-noite);
  outline-offset: 2px;
}

/* campos */
.icone-campo {
  color: var(--cat);
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
  margin-bottom: -6px;
}
.link-novo {
  font-size: 13px;
  font-weight: 700;
  color: var(--ef-pitaya);
  text-decoration: none;
}
.preco-linha {
  display: flex;
  gap: 10px;
  align-items: stretch;
}
.preco-linha ion-input {
  flex: 1;
}
.gratuito-botao {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1.5px solid var(--ef-borda);
  background: #fff;
  color: var(--ef-tinta-2);
  font: 700 14px/1 var(--ef-fonte);
  cursor: pointer;
}
.gratuito-botao.ativo {
  border-color: var(--ef-rio);
  background: #dcf5f2;
  color: #0a7a6f;
}
.gratuito-botao ion-icon {
  font-size: 18px;
}

/* rodapé fixo */
.rodape {
  background: #fff;
  padding: 10px 16px calc(var(--ion-safe-area-bottom, 0px) + 10px);
  box-shadow: 0 -8px 24px rgba(30, 16, 54, 0.08);
}
.rodape ion-button {
  margin: 0;
}
</style>
