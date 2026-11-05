<template>
  <ion-page>
    <ion-content class="ion-padding">
      <ion-refresher slot="fixed" @ionRefresh="atualizar">
        <ion-refresher-content />
      </ion-refresher>

      <header class="topo respeita-status">
        <p class="subtitulo-pagina">Olá, {{ primeiroNome }} 👋</p>
        <h1 class="titulo-pagina">Eventos</h1>
      </header>

      <ion-searchbar
        v-model="busca"
        placeholder="Buscar por nome, categoria ou local"
        :debounce="350"
        @ionInput="carregar"
        @ionClear="carregar"
      />

      <div v-if="categorias.length" class="filtros">
        <button type="button" :class="{ ativo: categoriaId === null }" @click="filtrar(null)">Todas</button>
        <button
          v-for="c in categorias"
          :key="c.id"
          type="button"
          :class="{ ativo: categoriaId === c.id }"
          @click="filtrar(c.id)"
        >
          {{ c.nome }}
        </button>
      </div>

      <div class="lista">
        <template v-if="carregando && !eventos.length">
          <div v-for="n in 4" :key="n" class="cartao esqueleto">
            <ion-skeleton-text animated class="esq-img" />
            <div class="esq-linhas">
              <ion-skeleton-text animated style="width: 80%" />
              <ion-skeleton-text animated style="width: 50%" />
              <ion-skeleton-text animated style="width: 35%" />
            </div>
          </div>
        </template>

        <EventoCard v-for="e in eventos" :key="e.id" :evento="e" @abrir="abrir" />

        <div v-if="!carregando && !eventos.length" class="vazio">
          <ion-icon :icon="busca || categoriaId ? searchOutline : calendarClearOutline" />
          <h3>{{ busca || categoriaId ? 'Nenhum evento encontrado' : 'Nenhum evento cadastrado' }}</h3>
          <p>{{ busca || categoriaId ? 'Tente outro termo de busca.' : 'Toque no + para criar o primeiro.' }}</p>
        </div>
      </div>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end">
        <ion-fab-button router-link="/eventos/novo" aria-label="Novo evento">
          <ion-icon :icon="add" />
        </ion-fab-button>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  IonContent, IonFab, IonFabButton, IonIcon, IonPage, IonRefresher, IonRefresherContent,
  IonSearchbar, IonSkeletonText, onIonViewWillEnter, useIonRouter,
} from '@ionic/vue'
import { add, calendarClearOutline, searchOutline } from 'ionicons/icons'
import EventoCard from '@/components/EventoCard.vue'
import { api } from '@/services/api'
import { sessao } from '@/services/sessao'
import { avisarErro } from '@/services/avisos'

const ionRouter = useIonRouter()
const eventos = ref([])
const categorias = ref([])
const busca = ref('')
const categoriaId = ref(null)
const carregando = ref(true)

const primeiroNome = computed(() => (sessao.usuario?.nome || '').split(' ')[0] || 'bem-vindo')

async function carregar() {
  carregando.value = true
  try {
    eventos.value = await api.eventos({ busca: busca.value?.trim(), categoria_id: categoriaId.value })
  } catch (erro) {
    avisarErro(erro)
  } finally {
    carregando.value = false
  }
}

async function carregarCategorias() {
  try {
    categorias.value = await api.categorias()
    if (categoriaId.value && !categorias.value.some((c) => c.id === categoriaId.value)) categoriaId.value = null
  } catch {
    /* o erro já aparece ao carregar os eventos */
  }
}

function filtrar(id) {
  categoriaId.value = id
  carregar()
}

async function atualizar(ev) {
  await Promise.all([carregar(), carregarCategorias()])
  ev.target.complete()
}

const abrir = (id) => ionRouter.push(`/eventos/${id}`)

// Recarrega toda vez que a tela aparece (ex.: depois de criar/editar um evento).
onIonViewWillEnter(() => {
  carregarCategorias()
  carregar()
})
</script>

<style scoped>
.topo {
  padding-top: 8px;
}
.subtitulo-pagina {
  margin-bottom: 0;
}
ion-searchbar {
  margin: 14px 0 12px;
}
.filtros {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  margin: 0 -16px 16px;
  padding: 0 16px 2px;
  scrollbar-width: none;
}
.filtros::-webkit-scrollbar {
  display: none;
}
.filtros button {
  flex-shrink: 0;
  border: 1px solid var(--ef-borda);
  background: #fff;
  color: #4a4f61;
  border-radius: 999px;
  padding: 7px 14px;
  font: 600 13px/1 inherit;
  font-family: inherit;
  cursor: pointer;
}
.filtros button.ativo {
  background: var(--ion-color-primary);
  border-color: var(--ion-color-primary);
  color: #fff;
}
.lista {
  padding-bottom: 80px;
}
.esqueleto {
  display: flex;
  gap: 14px;
  padding: 12px;
  margin-bottom: 12px;
}
.esq-img {
  width: 84px;
  height: 84px;
  border-radius: 12px;
  margin: 0;
}
.esq-linhas {
  flex: 1;
}
</style>
