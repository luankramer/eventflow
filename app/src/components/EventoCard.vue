<template>
  <button class="evento cartao" type="button" @click="$emit('abrir', evento.id)">
    <div class="miniatura">
      <img v-if="evento.imagem_url && !falhou" :src="evento.imagem_url" alt="" loading="lazy" @error="falhou = true" />
      <div v-else class="sem-imagem">
        <strong>{{ data.dia }}</strong>
        <span>{{ data.mes }}</span>
      </div>
    </div>
    <div class="info">
      <h3>{{ evento.nome }}</h3>
      <p class="quando">
        <ion-icon :icon="timeOutline" />
        {{ formatarData(evento.data) }} · {{ formatarHora(evento.hora) }}
      </p>
      <div class="rodape">
        <span class="chip-cat">{{ evento.categoria.nome }}</span>
        <span class="preco" :class="{ gratuito: !Number(evento.preco) }">{{ formatarPreco(evento.preco) }}</span>
      </div>
    </div>
  </button>
</template>

<script setup>
import { computed, ref } from 'vue'
import { IonIcon } from '@ionic/vue'
import { timeOutline } from 'ionicons/icons'
import { formatarData, formatarHora, formatarPreco, partesData } from '@/services/formato'

const props = defineProps({ evento: { type: Object, required: true } })
defineEmits(['abrir'])
const falhou = ref(false)
const data = computed(() => partesData(props.evento.data))
</script>

<style scoped>
.evento {
  width: 100%;
  display: flex;
  gap: 14px;
  padding: 12px;
  text-align: left;
  font: inherit;
  color: inherit;
  cursor: pointer;
  margin-bottom: 12px;
  transition: transform 0.1s;
}
.evento:active {
  transform: scale(0.985);
}
.miniatura {
  width: 84px;
  height: 84px;
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
  background: var(--ef-suave);
}
.miniatura img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.sem-imagem {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
}
.sem-imagem strong {
  font-size: 26px;
  line-height: 1;
}
.sem-imagem span {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.85;
}
.info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
h3 {
  margin: 2px 0 4px;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.25;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.quando {
  margin: 0;
  color: var(--ion-color-medium);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.rodape {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 6px;
}
</style>
