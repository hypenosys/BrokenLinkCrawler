<template>
  <div v-if="currentTask" class="relative overflow-hidden rounded-lg">
    <!-- Gradient animado de fondo -->
    <div class="absolute inset-0 bg-gradient-to-r" :class="statusGradient"></div>

    <div class="relative px-8 py-12 flex justify-between items-start">
      <div>
        <h2 class="text-4xl font-bold mb-2">{{ statusLabel }}</h2>
        <p class="text-lg text-slate-300 mb-8">{{ currentTask.url }}</p>

        <!-- KPIs -->
        <div class="grid grid-cols-3 gap-8">
          <div>
            <div class="text-5xl font-bold text-green-400">{{ currentTask.progress.links }}</div>
            <div class="text-sm text-slate-400">URLs Encontradas</div>
          </div>
          <div>
            <div class="text-5xl font-bold text-red-400">{{ currentTask.progress.broken }}</div>
            <div class="text-sm text-slate-400">Enlaces Rotos</div>
          </div>
          <div>
            <div class="text-5xl font-bold text-blue-400">{{ integrityPercent }}%</div>
            <div class="text-sm text-slate-400">Integridad</div>
          </div>
        </div>
      </div>

      <!-- Status Badge + Botones -->
      <div class="space-y-4">
        <div class="text-right">
          <span :class="['px-4 py-2 rounded-full text-sm font-semibold', statusBadgeClass]">
            {{ currentTask.status.toUpperCase() }}
          </span>
        </div>
        <button
          v-if="currentTask.status === 'completed'"
          @click="$emit('new-crawl')"
          class="block px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition"
        >
          Nuevo Crawl
        </button>
      </div>
    </div>
  </div>

  <!-- Sin tarea activa -->
  <div v-else class="text-center py-16">
    <h2 class="text-3xl font-bold mb-4">¿Comenzamos?</h2>
    <button
      @click="$emit('new-crawl')"
      class="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-lg font-semibold text-lg transition transform hover:scale-105"
    >
      + Nuevo Crawl
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentTask: Object
})

const statusLabel = computed(() => {
  const s = props.currentTask?.status
  return s === 'running' ? '🔄 Crawleando...'
       : s === 'completed' ? '✅ Completado'
       : s === 'failed' ? '❌ Error'
       : '⏸️ Pausado'
})

const statusGradient = computed(() => {
  const s = props.currentTask?.status
  return s === 'running' ? 'from-blue-600/30 to-purple-600/30'
       : s === 'completed' ? 'from-green-600/30 to-emerald-600/30'
       : 'from-red-600/30 to-orange-600/30'
})

const statusBadgeClass = computed(() => {
  const s = props.currentTask?.status
  return s === 'running' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/50'
       : s === 'completed' ? 'bg-green-500/20 text-green-300 border border-green-500/50'
       : 'bg-red-500/20 text-red-300 border border-red-500/50'
})

const integrityPercent = computed(() => {
  if (!props.currentTask?.progress) return 0
  const { links, broken } = props.currentTask.progress
  if (links === 0) return 100
  return Math.round(((links - broken) / links) * 100)
})
</script>