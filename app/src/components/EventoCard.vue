<template>
  <!-- Card em formato de ingresso: canhoto com a data | informações | miniatura -->
  <div class="sombra">
  <button class="ingresso" type="button" :style="{ '--cat': cor.cor, '--cat-suave': cor.suave, '--cat-texto': cor.texto, '--cat-tinta': cor.tinta }" @click="$emit('abrir', evento.id)">
    <div class="canhoto">
      <span class="semana">{{ data.semana }}</span>
      <strong class="dia">{{ data.dia }}</strong>
      <span class="mes">{{ data.mes }}</span>
    </div>

    <div class="corpo">
      <span class="chip-cat">
        <ion-icon :icon="icone" />
        {{ evento.categoria.nome }}
      </span>
      <h3>{{ evento.nome }}</h3>
      <p class="linha"><ion-icon :icon="timeOutline" /> {{ formatarHora(evento.hora) }}</p>
      <p class="linha"><ion-icon :icon="locationOutline" /> {{ evento.local.nome }}</p>
      <span class="preco" :class="{ gratuito: !Number(evento.preco) }">{{ formatarPreco(evento.preco) }}</span>
    </div>

    <div class="miniatura">
      <CapaEvento :evento="evento" tamanho-icone="28px" />
    </div>
  </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { IonIcon } from '@ionic/vue'
import { locationOutline, timeOutline } from 'ionicons/icons'
import CapaEvento from './CapaEvento.vue'
import { formatarHora, formatarPreco, partesData } from '@/services/formato'
import { corCategoria, iconeCategoria } from '@/services/cores'

const props = defineProps({ evento: { type: Object, required: true } })
defineEmits(['abrir'])
const data = computed(() => partesData(props.evento.data))
const cor = computed(() => corCategoria(props.evento.categoria))
const icone = computed(() => iconeCategoria(props.evento.categoria))
</script>

<style scoped>
.sombra {
  margin-bottom: 14px;
  filter: drop-shadow(0 6px 14px rgba(30, 16, 54, 0.09));
}
.ingresso {
  --recorte: 9px;
  position: relative;
  width: 100%;
  display: flex;
  align-items: stretch;
  text-align: left;
  font: inherit;
  color: inherit;
  cursor: pointer;
  padding: 0;
  border: 0;
  background: #fff;
  border-radius: 18px;
  transition: transform 0.12s ease;
  /* recortes semicirculares em cima e embaixo, na linha do picote */
  -webkit-mask:
    radial-gradient(circle at 74px 0, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) top / 100% 51% no-repeat,
    radial-gradient(circle at 74px 100%, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) bottom / 100% 51% no-repeat;
  mask:
    radial-gradient(circle at 74px 0, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) top / 100% 51% no-repeat,
    radial-gradient(circle at 74px 100%, transparent var(--recorte), #000 calc(var(--recorte) + 0.5px)) bottom / 100% 51% no-repeat;
}
.ingresso:active {
  transform: scale(0.98);
}
.canhoto {
  width: 74px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--cat);
  color: var(--cat-tinta);
  border-right: 2px dashed rgba(255, 255, 255, 0.6);
  padding: 12px 0;
}
.semana,
.mes {
  font-size: 12px;
  font-weight: 700;
  opacity: 0.9;
}
.dia {
  font-family: var(--ef-fonte-titulo);
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
  margin: 2px 0;
  letter-spacing: -1px;
}
.corpo {
  flex: 1;
  min-width: 0;
  padding: 12px 10px 12px 14px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
}
.chip-cat {
  background: var(--cat-suave);
  color: var(--cat-texto);
  margin-bottom: 3px;
}
h3 {
  margin: 0 0 3px;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.2px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.linha {
  margin: 0;
  color: var(--ion-color-medium);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.linha ion-icon {
  flex-shrink: 0;
  color: var(--cat);
}
.preco {
  margin-top: 4px;
  font-size: 17px;
}
.miniatura {
  width: 82px;
  flex-shrink: 0;
  padding: 10px 10px 10px 0;
}
.miniatura :deep(.capa-evento) {
  border-radius: 14px;
}
</style>
