<template>
  <ion-page>
    <ion-content>
      <header class="hero">
        <span class="luz-ipe" />
        <h1>Cadastros</h1>
        <p>Categorias e locais usados nos seus eventos.</p>
      </header>

      <div class="blocos">
        <router-link to="/categorias" class="bloco pitaya">
          <ion-icon :icon="pricetags" class="icone" />
          <strong>{{ valor(totais.categorias) }}</strong>
          <span>{{ totais.categorias === 1 ? 'Categoria' : 'Categorias' }}</span>
          <ion-icon :icon="arrowForward" class="seta" />
        </router-link>

        <router-link to="/locais" class="bloco rio">
          <ion-icon :icon="location" class="icone" />
          <strong>{{ valor(totais.locais) }}</strong>
          <span>{{ totais.locais === 1 ? 'Local no mapa' : 'Locais no mapa' }}</span>
          <ion-icon :icon="arrowForward" class="seta" />
        </router-link>

        <router-link to="/eventos/novo" class="bloco ipe largo">
          <div class="largo-texto">
            <strong class="pequeno">Cadastrar evento</strong>
            <span>{{ totais.eventos === null ? 'Carregando…' : `${totais.eventos} ${totais.eventos === 1 ? 'evento cadastrado' : 'eventos cadastrados'}` }}</span>
          </div>
          <div class="mais"><ion-icon :icon="add" /></div>
        </router-link>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { reactive } from 'vue'
import { IonContent, IonIcon, IonPage, onIonViewWillEnter } from '@ionic/vue'
import { add, arrowForward, location, pricetags } from 'ionicons/icons'
import { api } from '@/services/api'

const totais = reactive({ categorias: null, locais: null, eventos: null })
const valor = (n) => (n === null ? '–' : n)

onIonViewWillEnter(async () => {
  try {
    const [c, l, e] = await Promise.all([api.categorias(), api.locais(), api.eventos()])
    Object.assign(totais, { categorias: c.length, locais: l.length, eventos: e.length })
  } catch {
    /* as telas internas mostram o erro */
  }
})
</script>

<style scoped>
.hero p {
  margin-top: 6px;
}
.blocos {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 18px 16px 32px;
}
.bloco {
  position: relative;
  overflow: hidden;
  min-height: 168px;
  border-radius: 24px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  text-decoration: none;
  color: #fff;
  isolation: isolate;
  transition: transform 0.12s ease;
}
.bloco:active {
  transform: scale(0.97);
}
.bloco.pitaya {
  background: linear-gradient(150deg, #ff3d7f, var(--ef-pitaya) 60%, #b30f4a);
  box-shadow: 0 14px 28px rgba(232, 23, 93, 0.3);
}
.bloco.rio {
  background: linear-gradient(150deg, #2fd4c2, var(--ef-rio) 60%, #0a7a6f);
  box-shadow: 0 14px 28px rgba(18, 181, 165, 0.3);
}
.bloco.ipe {
  background: var(--ef-ipe);
  color: var(--ef-noite);
  box-shadow: 0 14px 28px rgba(255, 184, 0, 0.32);
}
.icone {
  position: absolute;
  z-index: -1;
  top: -10px;
  right: -14px;
  font-size: 104px;
  opacity: 0.22;
  transform: rotate(-12deg);
}
.bloco strong {
  font-family: var(--ef-fonte-titulo);
  font-size: 46px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -1.5px;
}
.bloco span {
  font-size: 14px;
  font-weight: 700;
  margin-top: 4px;
}
.seta {
  position: absolute;
  top: 16px;
  left: 16px;
  font-size: 20px;
  background: rgba(255, 255, 255, 0.22);
  border-radius: 50%;
  padding: 6px;
}
.largo {
  grid-column: 1 / -1;
  min-height: 0;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 20px 18px 20px 20px;
}
.largo-texto {
  display: flex;
  flex-direction: column;
}
.bloco strong.pequeno {
  font-size: 22px;
  letter-spacing: -0.4px;
}
.largo span {
  font-weight: 600;
  opacity: 0.8;
}
.mais {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: var(--ef-noite);
  color: var(--ef-ipe);
  font-size: 26px;
}
</style>
