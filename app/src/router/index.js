import { createRouter, createWebHistory } from '@ionic/vue-router'
import { carregarSessao, estaLogado } from '@/services/sessao'
import TabsPage from '@/views/TabsPage.vue'

const routes = [
  { path: '/', redirect: '/tabs/eventos' },
  { path: '/login', component: () => import('@/views/LoginPage.vue'), meta: { publica: true } },
  {
    path: '/tabs/',
    component: TabsPage,
    children: [
      { path: '', redirect: '/tabs/eventos' },
      { path: 'eventos', component: () => import('@/views/EventosPage.vue') },
      { path: 'mapa', component: () => import('@/views/MapaPage.vue') },
      { path: 'cadastros', component: () => import('@/views/CadastrosPage.vue') },
      { path: 'perfil', component: () => import('@/views/PerfilPage.vue') },
    ],
  },
  { path: '/eventos/novo', component: () => import('@/views/EventoFormPage.vue') },
  { path: '/eventos/:id', component: () => import('@/views/EventoDetalhePage.vue') },
  { path: '/eventos/:id/editar', component: () => import('@/views/EventoFormPage.vue') },
  { path: '/categorias', component: () => import('@/views/CategoriasPage.vue') },
  { path: '/categorias/nova', component: () => import('@/views/CategoriaFormPage.vue') },
  { path: '/categorias/:id/editar', component: () => import('@/views/CategoriaFormPage.vue') },
  { path: '/locais', component: () => import('@/views/LocaisPage.vue') },
  { path: '/locais/novo', component: () => import('@/views/LocalFormPage.vue') },
  { path: '/locais/:id/editar', component: () => import('@/views/LocalFormPage.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/tabs/eventos' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Guarda de rotas: sem sessão vai para o login; logado não volta para o login.
router.beforeEach(async (to) => {
  await carregarSessao()
  if (!to.meta.publica && !estaLogado()) return '/login'
  if (to.path === '/login' && estaLogado()) return '/tabs/eventos'
  return true
})

export default router
