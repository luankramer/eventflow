import { createRouter, createWebHistory } from '@ionic/vue-router'
import { carregarSessao, estaLogado } from '@/services/sessao'
import TabsPage from '@/views/TabsPage.vue'

const routes = [
  { path: '/', redirect: '/tabs/eventos', meta: { publica: true } },
  { path: '/login', component: () => import('@/views/LoginPage.vue'), meta: { publica: true } },
  {
    path: '/tabs/',
    component: TabsPage,
    children: [
      { path: '', redirect: '/tabs/eventos' },
      { path: 'eventos', component: () => import('@/views/EventosPage.vue'), meta: { publica: true } },
      { path: 'mapa', component: () => import('@/views/MapaPage.vue'), meta: { publica: true } },
      { path: 'cadastros', component: () => import('@/views/CadastrosPage.vue') },
      { path: 'perfil', component: () => import('@/views/PerfilPage.vue'), meta: { publica: true } },
    ],
  },
  { path: '/eventos/novo', component: () => import('@/views/EventoFormPage.vue') },
  { path: '/eventos/:id', component: () => import('@/views/EventoDetalhePage.vue'), meta: { publica: true } },
  { path: '/eventos/:id/editar', component: () => import('@/views/EventoFormPage.vue') },
  { path: '/categorias', component: () => import('@/views/CategoriasPage.vue') },
  { path: '/categorias/nova', component: () => import('@/views/CategoriaFormPage.vue') },
  { path: '/categorias/:id/editar', component: () => import('@/views/CategoriaFormPage.vue') },
  { path: '/locais', component: () => import('@/views/LocaisPage.vue') },
  { path: '/locais/novo', component: () => import('@/views/LocalFormPage.vue') },
  { path: '/locais/:id/editar', component: () => import('@/views/LocalFormPage.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/tabs/eventos', meta: { publica: true } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Ver eventos, mapa e detalhes é livre. Cadastrar e editar pede login:
// sem sessão vai para o login e, depois de entrar, volta para onde ia.
router.beforeEach(async (to) => {
  await carregarSessao()
  if (!to.meta.publica && !estaLogado()) return { path: '/login', query: { voltar: to.fullPath } }
  if (to.path === '/login' && estaLogado()) return '/tabs/eventos'
  return true
})

export default router
