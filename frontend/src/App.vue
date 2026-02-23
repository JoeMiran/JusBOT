<script setup>
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const messages = ref([
  { 
    role: 'assistant', 
    text: 'Olá, colaborador(a). \nSou o Assistente de Políticas Internas.\nTenho acesso às diretrizes oficiais do banco Itaú, incluindo o Código de Ética, Política de Privacidade e normas de conduta. Como posso esclarecer nossas normativas hoje?',
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
      text: 'Houve uma falha técnica na conexão com o servidor corporativo.', 
      mode: 'error' 
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col h-screen bg-gray-50 selection:bg-itau-orange selection:text-white font-corporate">
    
    <header class="flex-none px-8 py-6 border-b border-gray-200 bg-white flex items-center justify-between shadow-sm z-10">
      <div class="flex items-center gap-4">
        <img src="/favicon.ico" alt="Logo Itaú" class="w-10 h-10 object-contain drop-shadow-sm" />
        <div>
          <h1 class="text-3xl text-itau-orange font-bold tracking-tight pb-1">
            ItaúAI
          </h1>
          <p class="text-[10px] text-itau-blue font-bold uppercase tracking-[0.2em]">
            Assistente de Políticas Internas
          </p>
        </div>
      </div>

      <div class="flex items-center gap-4 text-[10px] tracking-widest uppercase">
        <span class="font-bold" :class="!isRagEnabled ? 'text-itau-blue' : 'text-itau-blue/50'">Geral</span>
        
        <button 
          @click="isRagEnabled = !isRagEnabled"
          class="relative w-12 h-6 border rounded-full transition-all duration-300 focus:outline-none"
          :class="isRagEnabled ? 'bg-itau-orange border-itau-orange' : 'bg-gray-100 border-itau-blue'"
        >
          <div 
            class="absolute top-1 left-1 w-3.5 h-3.5 bg-white rounded-full shadow-sm transform transition-transform duration-300"
            :class="isRagEnabled ? 'translate-x-6' : 'translate-x-0'"
          ></div>
        </button>
        
        <span class="font-bold" :class="isRagEnabled ? 'text-itau-orange' : 'text-itau-blue/50'">Políticas Internas</span>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto p-8 space-y-8 scroll-smooth bg-gray-50">
      <div v-for="(msg, index) in messages" :key="index" class="max-w-5xl mx-auto group">
        
        <div v-if="msg.role === 'user'" class="flex justify-end">
          <div class="bg-white border-r-4 border-itau-orange shadow-sm pl-6 pr-6 py-4 max-w-[85%] rounded-l-lg rounded-br-sm">
            <p class="text-[10px] text-itau-blue uppercase tracking-widest mb-1 text-right font-bold">Colaborador</p>
            <p class="text-lg text-itau-blue leading-relaxed">{{ msg.text }}</p>
          </div>
        </div>

        <div v-else class="flex justify-start w-full">
          <div class="w-full bg-white border border-gray-100 rounded-r-xl rounded-bl-sm p-8 shadow-md relative">
            <div class="absolute top-0 left-0 w-1.5 h-full bg-itau-orange rounded-l-xl"></div>
            
            <div class="flex items-center gap-3 mb-4 border-b border-gray-100 pb-3">
              <span class="text-itau-orange text-xl font-bold">i</span>
              <p class="text-xs text-itau-orange font-bold tracking-widest">
                ItaúAI &bull; {{ msg.mode === 'rag' ? 'Consulta de Políticas Internas' : 'Conhecimento Aberto' }}
              </p>
            </div>
            
            <div class="text-lg text-itau-blue leading-8 text-justify">
              <span class="whitespace-pre-wrap">{{ msg.text }}</span>
            </div>
            
            <div v-if="msg.sources && msg.sources.length" class="mt-8 pt-4 border-t border-gray-100 bg-gray-50 p-5 rounded-lg">
              <p class="text-[10px] text-itau-blue font-bold uppercase tracking-widest mb-3">Normativa de Referência:</p>
              <ul class="space-y-2">
                <li v-for="(src, i) in msg.sources" :key="i" class="text-sm text-itau-blue pl-4 border-l-2 border-itau-orange/40">
                  {{ src }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-8">
        <span class="text-itau-orange font-medium text-sm border-b-2 border-itau-orange/30 pb-1 animate-pulse">
          Consultando normativas e manuais do banco...
        </span>
      </div>
    </main>

    <footer class="flex-none px-8 py-8 bg-white border-t border-gray-200 shadow-[0_-4px_10px_-2px_rgba(0,0,0,0.03)] z-10">
      <div class="max-w-5xl mx-auto flex border-2 border-itau-blue rounded-lg focus-within:border-itau-orange transition-colors duration-300 bg-white overflow-hidden shadow-sm">
        <input 
          v-model="question" 
          @keyup.enter="sendMessage"
          :disabled="loading"
          type="text" 
          placeholder="Descreva sua dúvida sobre normas internas ou processos..." 
          class="w-full bg-transparent text-itau-blue placeholder-itau-blue/50 px-6 py-4 focus:outline-none text-lg font-medium"
        >
        <button 
          @click="sendMessage"
          :disabled="loading"
          class="bg-itau-blue text-white hover:bg-itau-orange hover:text-white px-10 transition-all duration-300 disabled:opacity-50 disabled:hover:bg-itau-blue border-l border-itau-blue font-bold text-[11px] uppercase tracking-[0.2em]"
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