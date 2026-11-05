<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/categorias" text="" />
        </ion-buttons>
        <ion-title>{{ editando ? 'Editar categoria' : 'Nova categoria' }}</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div v-if="carregando" class="centro"><ion-spinner name="crescent" /></div>

      <form v-else class="formulario" @submit.prevent="salvar">
        <!-- Prévia: como os eventos desta categoria vão aparecer -->
        <section class="previa" :style="estiloCor">
          <div class="previa-ingresso">
            <div class="previa-canhoto">
              <span>sáb</span>
              <strong>14</strong>
              <span>dez</span>
            </div>
            <div class="previa-corpo">
              <span class="chip-cat"><ion-icon :icon="iconeAtual" /> {{ form.nome.trim() || 'Nome da categoria' }}</span>
              <strong>Seu evento aparece assim</strong>
              <small>Cor e ícone de todos os eventos deste tipo</small>
            </div>
            <div class="previa-pino"><span /></div>
          </div>
        </section>

        <div>
          <label class="rotulo" for="nome-cat">Nome *</label>
          <ion-input
            id="nome-cat"
            v-model="form.nome"
            fill="outline"
            placeholder="Ex.: Música, Feira, Palestra"
            :maxlength="80"
            @ionInput="aoDigitarNome"
          />
        </div>

        <div>
          <span class="rotulo">Cor</span>
          <div class="cores" role="radiogroup" aria-label="Cor da categoria">
            <button
              v-for="c in CORES"
              :key="c.hex"
              type="button"
              role="radio"
              class="cor"
              :class="{ ativa: form.cor === c.hex }"
              :style="{ background: c.hex }"
              :aria-checked="form.cor === c.hex"
              :aria-label="c.nome"
              :title="c.nome"
              @click="form.cor = c.hex"
            >
              <ion-icon v-if="form.cor === c.hex" :icon="checkmark" :style="{ color: tons(c.hex).tinta }" />
            </button>
          </div>
        </div>

        <div>
          <span class="rotulo">Ícone</span>
          <div class="icones" role="radiogroup" aria-label="Ícone da categoria" :style="estiloCor">
            <button
              v-for="(item, chave) in ICONES"
              :key="chave"
              type="button"
              role="radio"
              class="icone-opcao"
              :class="{ ativo: form.icone === chave }"
              :aria-checked="form.icone === chave"
              @click="escolherIcone(chave)"
            >
              <span class="icone-caixa"><ion-icon :icon="item.icone" /></span>
              <span class="icone-rotulo">{{ item.rotulo }}</span>
            </button>
          </div>
        </div>

        <div>
          <label class="rotulo" for="desc-cat">Descrição</label>
          <ion-textarea id="desc-cat" v-model="form.descricao" fill="outline" placeholder="Opcional" :auto-grow="true" :rows="2" />
        </div>

        <ion-button type="submit" expand="block" class="botao-grande" :disabled="salvando">
          <ion-spinner v-if="salvando" name="crescent" />
          <span v-else>{{ editando ? 'Salvar alterações' : 'Cadastrar categoria' }}</span>
        </ion-button>
        <ion-button v-if="editando" expand="block" fill="clear" color="danger" @click="excluir">
          <ion-icon slot="start" :icon="trashOutline" /> Excluir categoria
        </ion-button>
      </form>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  IonBackButton, IonButton, IonButtons, IonContent, IonHeader, IonIcon, IonInput, IonPage, IonSpinner,
  IonTextarea, IonTitle, IonToolbar, useIonRouter,
} from '@ionic/vue'
import { checkmark, trashOutline } from 'ionicons/icons'
import { api } from '@/services/api'
import { voltarPara } from '@/services/navegacao'
import { avisar, avisarErro, avisarSucesso, confirmar } from '@/services/avisos'
import { CORES, ICONES, corCategoria, sugerirCor, sugerirIcone, tons } from '@/services/cores'

const route = useRoute()
const ionRouter = useIonRouter()
const id = route.params.id
const editando = computed(() => Boolean(id))
const form = reactive({ nome: '', descricao: '', cor: CORES[0].hex, icone: 'ingresso' })
const carregando = ref(true)
const salvando = ref(false)
let iconeEscolhidoAMao = false

const t = computed(() => tons(form.cor))
const iconeAtual = computed(() => ICONES[form.icone]?.icone ?? ICONES.ingresso.icone)
const estiloCor = computed(() => ({
  '--cat': t.value.cor,
  '--cat-suave': t.value.suave,
  '--cat-texto': t.value.texto,
  '--cat-tinta': t.value.tinta,
}))

// Enquanto o usuário não escolhe um ícone, sugerimos um pelo nome ("Show" → nota musical).
function aoDigitarNome() {
  if (!iconeEscolhidoAMao) form.icone = sugerirIcone(form.nome)
}
function escolherIcone(chave) {
  form.icone = chave
  iconeEscolhidoAMao = true
}

onMounted(async () => {
  try {
    if (id) {
      const c = await api.categoria(id)
      form.nome = c.nome
      form.descricao = c.descricao || ''
      form.cor = corCategoria(c).cor
      form.icone = c.icone && ICONES[c.icone] ? c.icone : sugerirIcone(c.nome)
      iconeEscolhidoAMao = true
    } else {
      form.cor = sugerirCor(await api.categorias()) // próxima cor ainda não usada
    }
  } catch (erro) {
    avisarErro(erro)
  } finally {
    carregando.value = false
  }
})

async function salvar() {
  if (form.nome.trim().length < 2) return avisar('Informe o nome da categoria.')
  salvando.value = true
  try {
    const dados = {
      nome: form.nome.trim(),
      descricao: form.descricao.trim() || null,
      cor: form.cor,
      icone: form.icone,
    }
    if (editando.value) await api.editarCategoria(id, dados)
    else await api.criarCategoria(dados)
    avisarSucesso(editando.value ? 'Categoria atualizada.' : 'Categoria cadastrada.')
    voltarPara(ionRouter, '/categorias')
  } catch (erro) {
    avisarErro(erro)
  } finally {
    salvando.value = false
  }
}

async function excluir() {
  if (!(await confirmar('Excluir categoria', `Excluir "${form.nome}"?`, 'Excluir'))) return
  try {
    await api.excluirCategoria(id)
    avisarSucesso('Categoria excluída.')
    voltarPara(ionRouter, '/categorias')
  } catch (erro) {
    avisarErro(erro)
  }
}
</script>

<style scoped>
.centro {
  display: grid;
  place-items: center;
  padding: 40px;
}

/* prévia */
.previa {
  padding: 18px;
  border-radius: 22px;
  background: var(--ef-noite);
  background-image: radial-gradient(circle at 90% 0%, color-mix(in srgb, var(--cat) 55%, transparent), transparent 60%);
  transition: background-image 0.2s;
}
.previa-ingresso {
  display: flex;
  align-items: stretch;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}
.previa-canhoto {
  width: 64px;
  flex-shrink: 0;
  background: var(--cat);
  color: var(--cat-tinta);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 2px dashed rgba(255, 255, 255, 0.6);
  padding: 10px 0;
  transition: background 0.2s;
}
.previa-canhoto span {
  font-size: 11px;
  font-weight: 700;
  opacity: 0.9;
}
.previa-canhoto strong {
  font-family: var(--ef-fonte-titulo);
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}
.previa-corpo {
  flex: 1;
  min-width: 0;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
}
.previa-corpo .chip-cat {
  background: var(--cat-suave);
  color: var(--cat-texto);
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
.previa-corpo strong {
  font-family: var(--ef-fonte-titulo);
  font-size: 16px;
  margin-top: 3px;
}
.previa-corpo small {
  color: var(--ion-color-medium);
  font-size: 12px;
}
.previa-pino {
  width: 54px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
}
.previa-pino span {
  width: 26px;
  height: 26px;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  background: var(--cat);
  border: 3px solid #fff;
  box-shadow: 0 4px 10px rgba(30, 16, 54, 0.3);
}

/* cores */
.cores {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}
.cor {
  aspect-ratio: 1;
  border-radius: 50%;
  border: 0;
  cursor: pointer;
  display: grid;
  place-items: center;
  font-size: 20px;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.06);
  transition: transform 0.12s;
}
.cor.ativa {
  box-shadow: 0 0 0 3px var(--ion-background-color), 0 0 0 5px var(--ef-noite);
  transform: scale(0.92);
}
.cor:focus-visible {
  outline: 3px solid var(--ef-noite);
  outline-offset: 3px;
}

/* ícones */
.icones {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.icone-opcao {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 10px 2px 8px;
  border: 1.5px solid transparent;
  border-radius: 14px;
  background: #fff;
  font: inherit;
  color: var(--ef-tinta-2);
  cursor: pointer;
}
.icone-caixa {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--ef-nevoa);
  font-size: 19px;
  color: var(--ef-tinta-2);
}
.icone-rotulo {
  font-size: 11px;
  font-weight: 600;
  text-align: center;
  line-height: 1.15;
}
.icone-opcao.ativo {
  border-color: var(--cat);
  color: var(--ion-text-color);
}
.icone-opcao.ativo .icone-caixa {
  background: var(--cat);
  color: var(--cat-tinta);
}
.icone-opcao:focus-visible {
  outline: 3px solid var(--ef-noite);
  outline-offset: 2px;
}
</style>
