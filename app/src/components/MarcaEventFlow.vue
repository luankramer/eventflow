<template>
  <span class="marca-ef" :class="{ clara }" role="img" aria-label="EventFlow">
    <svg viewBox="0 0 120 120" :width="tamanho" :height="tamanho" aria-hidden="true">
      <defs>
        <linearGradient :id="idGradiente" x1="0.15" y1="0" x2="0.85" y2="1">
          <stop offset="0" stop-color="#FF4F8B" />
          <stop offset="0.55" stop-color="#E8175D" />
          <stop offset="1" stop-color="#B80F4C" />
        </linearGradient>
      </defs>
      <path d="M12 104 C 26 104, 30 86, 44 86 S 58 94, 66 93" fill="none" stroke="#FFB800" stroke-width="6.5" stroke-linecap="round" stroke-dasharray="0.1 12.5" />
      <path d="M76 92 C 76 92 50 66 50 46 A 26 26 0 1 1 102 46 C 102 66 76 92 76 92 Z" :fill="`url(#${idGradiente})`" />
      <path d="M63 35 h26 a3 3 0 0 1 3 3 v4.2 a4.3 4.3 0 0 0 0 8.6 V55 a3 3 0 0 1 -3 3 h-26 a3 3 0 0 1 -3 -3 v-4.2 a4.3 4.3 0 0 0 0 -8.6 V38 a3 3 0 0 1 3 -3 Z" fill="#FFFFFF" />
      <path d="M72 38.5 v16.5" stroke="#E8175D" stroke-width="2" stroke-dasharray="2.4 2.4" stroke-linecap="round" />
    </svg>
    <span v-if="comNome" class="nome" :style="{ fontSize: `${tamanho * 0.5}px` }">EventFlow</span>
  </span>
</template>

<script setup>
// Logo oficial do EventFlow: pino de localização com um ingresso e o trajeto até o evento.
defineProps({
  tamanho: { type: Number, default: 48 },
  comNome: { type: Boolean, default: true },
  clara: { type: Boolean, default: false }, // nome em branco, para fundos escuros
})
const idGradiente = `ef-pino-${Math.random().toString(36).slice(2, 8)}`
</script>

<style scoped>
.marca-ef {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.marca-ef svg {
  flex-shrink: 0;
  display: block;
}
.nome {
  font-family: var(--ef-fonte-titulo);
  font-weight: 800;
  letter-spacing: -0.04em;
  font-variation-settings: 'wdth' 90;
  color: var(--ef-noite, #1e1036);
  line-height: 1;
}
.clara .nome {
  color: #fff;
}
</style>
