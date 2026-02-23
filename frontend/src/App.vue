<script setup>
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const messages = ref([
  { 
    role: 'assistant', 
    text: 'Olá, colaborador(a). Sou o Assistente de Governança do Itaú.\nTenho acesso ao nosso Código de Ética, Políticas de Privacidade e Diretrizes de Conduta. Como posso ajudar você a entender nossas normas hoje?',
    mode: 'rag'
  }
])
const loading = ref(false)
const isRagEnabled = ref(true)

const sendMessage = async () => {
  if (!question.value.trim()) return

  const currentMode = isRagEnabled.value ? 'rag' : 'pure'
  const userText = question.value

  messages.value.push({ role: 'user', text: userText, mode: currentMode })
  question.value = ''
  loading.value = true

  try {
    const response = await axios.post('http://127.0.0.1:8000/ask', {
      question: userText,
      use_rag: isRagEnabled.value 
    })

    messages.value.push({ 
      role: 'assistant', 
      text: response.data.answer,
      sources: response.data.sources,
      mode: currentMode 
    })
  } catch (error) {
    console.error(error)
    messages.value.push({ 
      role: 'assistant', 
      text: 'Desculpe, ocorreu uma instabilidade na conexão com o servidor de Governança.', 
      mode: 'error' 
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col h-screen bg-itau-gray selection:bg-itau-blue selection:text-white">
    
    <header class="flex-none px-8 py-4 bg-white border-b border-gray-200 flex items-center justify-between shadow-sm">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-itau-blue rounded-lg flex items-center justify-center shadow-md">
          <span class="text-white font-bold text-xs" style="color: yellow">Itaú</span>
        </div>
        <div>
          <h1 class="text-xl text-itau-orange font-bold tracking-tight">
            Compliance Bot
          </h1>
          <p class="text-[10px] text-gray-400 uppercase tracking-widest font-bold">
            Governança e Cultura Corporativa
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider">
        <span :class="!isRagEnabled ? 'text-itau-blue' : 'text-gray-400'">Assistente Geral</span>
        <button 
          @click="isRagEnabled = !isRagEnabled"
          class="relative w-12 h-6 bg-gray-200 rounded-full transition-all duration-300 focus:outline-none"
          :class="{ 'bg-itau-blue': isRagEnabled }"
        >
          <div 
            class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-300"
            :class="isRagEnabled ? 'translate-x-6' : 'translate-x-0'"
          ></div>
        </button>
        <span :class="isRagEnabled ? 'text-itau-orange' : 'text-gray-400'">Base de Políticas</span>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth">
      <div v-for="(msg, index) in messages" :key="index" class="max-w-4xl mx-auto">
        
        <div v-if="msg.role === 'user'" class="flex justify-end">
          <div class="bg-itau-blue text-white p-4 rounded-2xl rounded-tr-none max-w-[80%] shadow-md">
            <p class="text-[9px] uppercase font-bold opacity-70 mb-1">Você</p>
            <p class="text-md leading-relaxed">{{ msg.text }}</p>
          </div>
        </div>

        <div v-else class="flex justify-start">
          <div class="bg-white border-l-4 border-itau-orange p-6 rounded-r-2xl max-w-[90%] shadow-sm">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-itau-orange font-bold text-lg">●</span>
              <p class="text-xs text-itau-blue font-bold uppercase tracking-widest">
                Itaú Bot &bull; {{ msg.mode === 'rag' ? 'Política Interna' : 'Conhecimento Geral' }}
              </p>
            </div>
            
            <div class="text-itau-text leading-relaxed text-justify">
              <span class="whitespace-pre-wrap">{{ msg.text }}</span>
            </div>

            <div v-if="msg.sources && msg.sources.length" class="mt-6 pt-4 border-t border-gray-100">
              <p class="text-[9px] text-gray-400 font-bold uppercase mb-2">Documentos de Referência:</p>
              <div class="flex flex-wrap gap-2">
                <span v-for="(src, i) in msg.sources" :key="i" class="text-[10px] bg-gray-50 text-itau-blue border border-gray-200 px-2 py-1 rounded">
                  {{ src }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-4">
        <div class="flex gap-1">
          <div class="w-2 h-2 bg-itau-orange rounded-full animate-bounce"></div>
          <div class="w-2 h-2 bg-itau-orange rounded-full animate-bounce [animation-delay:-0.15s]"></div>
          <div class="w-2 h-2 bg-itau-orange rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        </div>
      </div>
    </main>

    <footer class="flex-none p-6 bg-white border-t border-gray-200">
      <div class="max-w-4xl mx-auto flex gap-3">
        <div class="relative flex-1">
          <input 
            v-model="question" 
            @keyup.enter="sendMessage"
            :disabled="loading"
            type="text" 
            placeholder="Dúvida sobre conduta, ética ou deveres..." 
            class="w-full bg-gray-50 text-itau-text border border-gray-300 rounded-xl px-6 py-4 focus:outline-none focus:border-itau-orange transition-colors disabled:opacity-50"
          >
        </div>
        <button 
          @click="sendMessage"
          :disabled="loading"
          class="bg-itau-orange hover:bg-[#D66500] text-white font-bold px-8 rounded-xl transition-all shadow-md disabled:opacity-50"
        >
          Perguntar
        </button>
      </div>
      <p class="text-center text-gray-400 text-[9px] mt-4 font-bold uppercase tracking-widest">
        Uso Exclusivo Interno &bull; Banco Itaú S.A.
      </p>
    </footer>
  </div>
</template>