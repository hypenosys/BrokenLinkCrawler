<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
    <!-- Header -->
    <header class="border-b border-slate-700/50 bg-slate-950/50 backdrop-blur">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          🕷️ Broken Link Crawler
        </h1>
        <div class="text-sm text-slate-400">
          Diputació de Tarragona
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-6 py-8">
      <!-- Hero Dashboard -->
      <div class="mb-8">
        <DashboardHero
          :current-task="currentTask"
          @new-crawl="showNewCrawlModal = true"
        />
      </div>

      <!-- Grid de Tareas -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <CrawlerCard
          v-for="task in history"
          :key="task.id"
          :task="task"
          :is-active="currentTask?.id === task.id"
        />
      </div>

      <!-- Live Log -->
      <LiveLog v-if="currentTask?.status === 'running'" :task-id="currentTask.id" />

      <!-- Results Viewer -->
      <ResultsViewer v-if="currentTask?.status === 'completed'" :results="currentTask.results" />
    </main>

    <!-- Modal Nuevo Crawl -->
    <Teleport to="body" v-if="showNewCrawlModal">
      <NewCrawlModal
        @submit="startCrawl"
        @close="showNewCrawlModal = false"
      />
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCrawlerStore } from './stores/crawler'
import DashboardHero from './components/DashboardHero.vue'
import CrawlerCard from './components/CrawlerCard.vue'
import LiveLog from './components/LiveLog.vue'
import ResultsViewer from './components/ResultsViewer.vue'
import NewCrawlModal from './components/NewCrawlModal.vue'

const store = useCrawlerStore()
const showNewCrawlModal = ref(false)

const currentTask = computed(() => store.currentTask)
const history = computed(() => store.history)

onMounted(async () => {
  await store.fetchHistory()
  // Poll cada 2s si hay tarea activa
  setInterval(() => {
    if (currentTask.value?.status === 'running') {
      store.fetchCurrentTask()
    }
  }, 2000)
})

const startCrawl = async (config) => {
  await store.startCrawl(config)
  showNewCrawlModal.value = false
}
</script>