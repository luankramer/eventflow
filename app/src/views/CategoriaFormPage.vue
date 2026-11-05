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
        <div>
          <label class="rotulo" for="nome-cat">Nome *</label>
          <ion-input id="nome-cat" v-model="form.nome" fill="outline" placeholder="Ex.: Música" :maxlength="80" />
        </div>
        <div>
          <label class="rotulo" for="desc-cat">Descrição</label>
          <ion-textarea
            id="desc-cat"
            v-model="form.descricao"
            fill="outline"
            placeholder="Opcional"
            :auto-grow="true"
            :rows="3"
          />
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
import { trashOutline } from 'ionicons/icons'
import { api } from '@/services/api'
import { voltarPara } from '@/services/navegacao'
import { avisar, avisarErro, avisarSucesso, confirmar } from '@/services/avisos'

const route = useRoute()
const ionRouter = useIonRouter()
const id = route.params.id
const editando = computed(() => Boolean(id))
const form = reactive({ nome: '', descricao: '' })
const carregando = ref(Boolean(id))
const salvando = ref(false)

onMounted(async () => {
  if (!id) return
  try {
    const c = await api.categoria(id)
    form.nome = c.nome
    form.descricao = c.descricao || ''
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
    const dados = { nome: form.nome.trim(), descricao: form.descricao.trim() || null }
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
</style>
