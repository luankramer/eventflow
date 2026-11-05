<template>
  <ion-page>
    <ion-content class="ion-padding">
      <header class="topo respeita-status">
        <h1 class="titulo-pagina">Cadastros</h1>
        <p class="subtitulo-pagina">Gerencie as categorias e os locais usados nos eventos.</p>
      </header>

      <router-link to="/categorias" class="atalho cartao">
        <div class="icone"><ion-icon :icon="pricetagsOutline" /></div>
        <div class="texto">
          <strong>Categorias</strong>
          <span>{{ rotulo(totais.categorias, 'categoria', 'categorias') }}</span>
        </div>
        <ion-icon :icon="chevronForward" class="seta" />
      </router-link>

      <router-link to="/locais" class="atalho cartao">
        <div class="icone verde"><ion-icon :icon="locationOutline" /></div>
        <div class="texto">
          <strong>Locais</strong>
          <span>{{ rotulo(totais.locais, 'local', 'locais') }} com coordenadas</span>
        </div>
        <ion-icon :icon="chevronForward" class="seta" />
      </router-link>

      <router-link to="/eventos/novo" class="atalho cartao">
        <div class="icone laranja"><ion-icon :icon="addCircleOutline" /></div>
        <div class="texto">
          <strong>Novo evento</strong>
          <span>{{ rotulo(totais.eventos, 'evento cadastrado', 'eventos cadastrados') }}</span>
        </div>
        <ion-icon :icon="chevronForward" class="seta" />
      </router-link>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { reactive } from 'vue'
import { IonContent, IonIcon, IonPage, onIonViewWillEnter } from '@ionic/vue'
import { addCircleOutline, chevronForward, locationOutline, pricetagsOutline } from 'ionicons/icons'
import { api } from '@/services/api'

const totais = reactive({ categorias: null, locais: null, eventos: null })

function rotulo(n, singular, plural) {
  if (n === null) return 'Carregando…'
  return `${n} ${n === 1 ? singular : plural}`
}

onIonViewWillEnter(async () => {
  try {
    const [c, l, e] = await Promise.all([api.categorias(), api.locais(), api.eventos()])
    Object.assign(totais, { categorias: c.length, locais: l.length, eventos: e.length })
  } catch {
    /* mantém "Carregando…"; as telas internas mostram o erro */
  }
})
</script>

<style scoped>
.topo {
  padding-top: 8px;
  margin-bottom: 8px;
}
.atalho {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  margin-bottom: 12px;
  text-decoration: none;
  color: inherit;
}
.icone {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--ef-suave);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.icone ion-icon {
  font-size: 24px;
  color: var(--ion-color-primary);
}
.icone.verde {
  background: #e7f6ec;
}
.icone.verde ion-icon {
  color: #16a34a;
}
.icone.laranja {
  background: #fff1e6;
}
.icone.laranja ion-icon {
  color: #ea580c;
}
.texto {
  flex: 1;
}
.texto strong {
  display: block;
  font-size: 16px;
}
.texto span {
  font-size: 13px;
  color: var(--ion-color-medium);
}
.seta {
  color: #b6b9c8;
  font-size: 20px;
}
</style>
