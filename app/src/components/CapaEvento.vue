<template>
  <div class="capa-evento">
    <img v-if="evento.imagem_url && !falhou" :src="evento.imagem_url" alt="" loading="lazy" @error="falhou = true" />
    <div v-else class="sem-foto" :style="{ '--c1': cor.cor, '--c2': cor.escura }">
      <ion-icon :icon="icone" :style="{ fontSize: tamanhoIcone }" />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { IonIcon } from '@ionic/vue'
import { corCategoria, iconeCategoria } from '@/services/cores'

const props = defineProps({
  evento: { type: Object, required: true },
  tamanhoIcone: { type: String, default: '32px' },
})
const falhou = ref(false)
watch(() => props.evento.imagem_url, () => (falhou.value = false))
const cor = computed(() => corCategoria(props.evento.categoria))
const icone = computed(() => iconeCategoria(props.evento.categoria))
</script>

<style scoped>
.capa-evento {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.sem-foto {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.28), transparent 45%),
    linear-gradient(145deg, var(--c1), var(--c2));
}
.sem-foto ion-icon {
  color: rgba(255, 255, 255, 0.92);
}
</style>
