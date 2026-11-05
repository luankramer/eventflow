<template>
  <ion-page>
    <ion-content>
      <ion-refresher slot="fixed" @ionRefresh="atualizar">
        <ion-refresher-content />
      </ion-refresher>

      <header class="hero">
        <span class="luz-ipe" />
        <p class="saudacao">Olá, {{ primeiroNome }}</p>
        <h1>Encontre seu próximo evento</h1>
      </header>

      <div class="busca">
        <ion-searchbar
          v-model="busca"
          placeholder="Buscar evento, categoria ou local"
          :debounce="350"
          @ionInput="carregar"
          @ionClear="carregar"
        />
      </div>

      <div v-if="categorias.length" class="filtros">
        <button type="button" :class="{ ativo: categoriaId === null }" @click="filtrar(null)">
          <ion-icon :icon="apps" /> Todas
        </button>
        <button
          v-for="c in categorias"
          :key="c.id"
          type="button"
          :class="{ ativo: categoriaId === c.id }"
          :style="{ '--cat': corCategoria(c).cor, '--cat-suave': corCategoria(c).suave, '--cat-texto': corCategoria(c).texto, '--cat-tinta': corCategoria(c).tinta }"
          @click="filtrar(c.id)"
        >
          <ion-icon :icon="iconeCategoria(c)" /> {{ c.nome }}
        </button>
      </div>

      <section v-if="destaques.length" class="secao-destaques">
        <h2 class="titulo-secao">Próximos eventos</h2>
        <div class="carrossel">
          <DestaqueCard v-for="e in destaques" :key="e.id" :evento="e" @abrir="abrir" />
        </div>
      </section>

      <section class="lista">
        <h2 v-if="eventos.length" class="titulo-secao">{{ tituloLista }}</h2>

        <template v-if="carregando && !eventos.length">
          <div v-for="n in 3" :key="n" class="esqueleto cartao">
            <ion-skeleton-text animated class="esq-canhoto" />
            <div class="esq-linhas">
              <ion-skeleton-text animated style="width: 40%" />
              <ion-skeleton-text animated style="width: 85%" />
              <ion-skeleton-text animated style="width: 55%" />
            </div>
          </div>
        </template>

        <EventoCard v-for="e in eventos" :key="e.id" :evento="e" @abrir="abrir" />

        <div v-if="!carregando && !eventos.length" class="vazio">
          <div class="vazio-icone"><ion-icon :icon="filtrando ? searchOutline : ticketOutline" /></div>
          <h3>{{ filtrando ? 'Nenhum evento encontrado' : 'Nenhum evento ainda' }}</h3>
          <p>{{ filtrando ? 'Tente buscar por outro nome, categoria ou local.' : 'Cadastre o primeiro evento no botão +.' }}</p>
        </div>
      </section>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end">
        <ion-fab-button router-link="/eventos/novo" aria-label="Cadastrar evento">
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
import { add, apps, searchOutline, ticketOutline } from 'ionicons/icons'
import EventoCard from '@/components/EventoCard.vue'
import DestaqueCard from '@/components/DestaqueCard.vue'
import { api } from '@/services/api'
import { sessao } from '@/services/sessao'
import { avisarErro } from '@/services/avisos'
import { corCategoria, iconeCategoria } from '@/services/cores'

const ionRouter = useIonRouter()
const eventos = ref([])
const categorias = ref([])
const busca = ref('')
const categoriaId = ref(null)
const carregando = ref(true)

const primeiroNome = computed(() => (sessao.usuario?.nome || '').split(' ')[0] || 'bem-vindo')
const filtrando = computed(() => Boolean(busca.value?.trim() || categoriaId.value))
// O carrossel aparece só na tela inicial, sem busca nem filtro.
const destaques = computed(() => (filtrando.value || eventos.value.length < 2 ? [] : eventos.value.slice(0, 5)))
const tituloLista = computed(() => {
  if (!filtrando.value) return 'Todos os eventos'
  const n = eventos.value.length
  return `${n} ${n === 1 ? 'resultado' : 'resultados'}`
})

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
.hero {
  padding-bottom: 54px;
}
.saudacao {
  font-weight: 600;
  margin-bottom: 6px !important;
}
.hero h1 {
  max-width: 260px;
}
.busca {
  margin: -28px 16px 0;
  position: relative;
  z-index: 2;
}
.filtros {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 16px 16px 2px;
  scrollbar-width: none;
}
.filtros::-webkit-scrollbar {
  display: none;
}
.filtros button {
  --cat: var(--ef-noite);
  --cat-suave: #ebe5f6;
  --cat-texto: var(--ef-noite);
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: #fff;
  color: var(--ef-tinta-2);
  border-radius: 999px;
  padding: 9px 14px 9px 11px;
  font: 700 13px/1 var(--ef-fonte);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(30, 16, 54, 0.06);
}
.filtros button ion-icon {
  font-size: 16px;
  color: var(--cat);
}
.filtros button.ativo {
  background: var(--cat);
  color: var(--cat-tinta, #fff);
  box-shadow: 0 6px 16px color-mix(in srgb, var(--cat) 40%, transparent);
}
.filtros button.ativo ion-icon {
  color: var(--cat-tinta, #fff);
}
.secao-destaques .titulo-secao,
.lista {
  padding: 0 16px;
}
.carrossel {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding: 0 16px 18px;
  scroll-snap-type: x mandatory;
  scroll-padding: 0 16px;
  scrollbar-width: none;
}
.carrossel::-webkit-scrollbar {
  display: none;
}
.secao-destaques + .lista .titulo-secao {
  margin-top: 8px;
}
.lista {
  padding-bottom: 96px;
}
.esqueleto {
  display: flex;
  gap: 14px;
  padding: 0;
  margin-bottom: 14px;
  overflow: hidden;
}
.esq-canhoto {
  width: 74px;
  height: 104px;
  margin: 0;
}
.esq-linhas {
  flex: 1;
  padding: 14px 12px 0 0;
}
</style>
