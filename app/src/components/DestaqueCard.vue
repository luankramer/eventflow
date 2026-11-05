<template>
  <button class="destaque" type="button" @click="$emit('abrir', evento.id)">
    <CapaEvento :evento="evento" tamanho-icone="64px" class="fundo" />
    <div class="veu" />

    <div class="selo-data">
      <strong>{{ data.dia }}</strong>
      <span>{{ data.mes }}</span>
    </div>
    <span class="selo-preco" :class="{ gratuito: !Number(evento.preco) }">{{ formatarPreco(evento.preco) }}</span>

    <div class="texto">
      <span class="chip-cat" :style="{ background: cor.cor, color: cor.tinta }">
        <ion-icon :icon="icone" /> {{ evento.categoria.nome }}
      </span>
      <h3>{{ evento.nome }}</h3>
      <p><ion-icon :icon="locationOutline" /> {{ evento.local.nome }}</p>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { IonIcon } from '@ionic/vue'
import { locationOutline } from 'ionicons/icons'
import CapaEvento from './CapaEvento.vue'
import { formatarPreco, partesData } from '@/services/formato'
import { corCategoria, iconeCategoria } from '@/services/cores'

const props = defineProps({ evento: { type: Object, required: true } })
defineEmits(['abrir'])
const data = computed(() => partesData(props.evento.data))
const cor = computed(() => corCategoria(props.evento.categoria))
const icone = computed(() => iconeCategoria(props.evento.categoria))
</script>

<style scoped>
.destaque {
  position: relative;
  flex-shrink: 0;
  width: 250px;
  height: 300px;
  border: 0;
  padding: 0;
  border-radius: 24px;
  overflow: hidden;
  text-align: left;
  font: inherit;
  color: #fff;
  cursor: pointer;
  scroll-snap-align: start;
  box-shadow: 0 14px 30px rgba(30, 16, 54, 0.22);
  transition: transform 0.12s ease;
}
.destaque:active {
  transform: scale(0.98);
}
.fundo {
  position: absolute;
  inset: 0;
}
.veu {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(30, 16, 54, 0) 35%, rgba(30, 16, 54, 0.92) 100%);
}
.selo-data {
  position: absolute;
  top: 14px;
  left: 14px;
  width: 54px;
  padding: 7px 0 6px;
  border-radius: 16px;
  background: #fff;
  color: var(--ef-noite);
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1;
}
.selo-data strong {
  font-family: var(--ef-fonte-titulo);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.selo-data span {
  font-size: 12px;
  font-weight: 700;
  color: var(--ef-pitaya);
  margin-top: 2px;
}
.selo-preco {
  position: absolute;
  top: 14px;
  right: 14px;
  padding: 7px 12px;
  border-radius: 999px;
  background: var(--ef-ipe);
  color: var(--ef-noite);
  font-family: var(--ef-fonte-titulo);
  font-weight: 800;
  font-size: 14px;
}
.texto {
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: 16px;
}

h3 {
  margin: 8px 0 6px;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.5px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
p {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.82);
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>
