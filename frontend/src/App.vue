<script setup>
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const messages = ref([
  { 
    role: 'assistant', 
    text: 'Prezado(a). Sou o JusAI.\nPossuo acesso à Constituição, CDC, CPC e LGPD. Como posso auxiliá-lo juridicamente hoje?',
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
      text: 'Houve uma falha técnica na conexão com o servidor jurídico.', 
      mode: 'error' 
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col h-screen bg-jus-black selection:bg-jus-gold selection:text-black">
    
    <header class="flex-none px-8 py-6 border-b border-jus-gold-dim/30 bg-jus-black flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="text-4xl">⚖️</div>
        <div>
          <h1 class="text-3xl text-jus-gold font-bold tracking-wide border-b border-jus-gold/20 pb-1 uppercase">
            JusAI
          </h1>
          <p class="text-[10px] text-gray-500 font-ui uppercase tracking-[0.3em] mt-1">
            Inteligência Jurídica UFPA
          </p>
        </div>
      </div>

      <div class="flex items-center gap-4 text-[10px] font-ui tracking-widest uppercase">
        <span :class="!isRagEnabled ? 'text-gray-300 font-bold' : 'text-gray-600'">Geral</span>
        <button 
          @click="isRagEnabled = !isRagEnabled"
          class="relative w-12 h-6 border border-jus-gold/50 rounded-full transition-all duration-300 focus:outline-none hover:border-jus-gold"
          :class="isRagEnabled ? 'bg-jus-gold/10' : 'bg-transparent'"
        >
          <div 
            class="absolute top-1 left-1 w-3.5 h-3.5 bg-jus-gold rounded-full shadow-sm transform transition-transform duration-300"
            :class="isRagEnabled ? 'translate-x-6' : 'translate-x-0'"
          ></div>
        </button>
        <span :class="isRagEnabled ? 'text-jus-gold font-bold' : 'text-gray-600'">Acervo Jurídico</span>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto p-8 space-y-10 scroll-smooth bg-jus-black">
      <div v-for="(msg, index) in messages" :key="index" class="max-w-5xl mx-auto group">
        
        <div v-if="msg.role === 'user'" class="flex justify-end">
          <div class="bg-jus-gray-light border-l-2 border-gray-600 pl-6 pr-6 py-4 max-w-[85%]">
            <p class="text-[10px] text-gray-500 font-ui uppercase tracking-widest mb-2 text-right">Consulente</p>
            <p class="text-lg text-gray-300 leading-relaxed font-light">{{ msg.text }}</p>
          </div>
        </div>

        <div v-else class="flex justify-start w-full">
          <div class="w-full bg-jus-gray-dark border border-jus-gold-dim/30 p-8 shadow-sm relative">
            <div class="absolute top-0 left-0 w-24 h-[1px] bg-jus-gold"></div>
            <div class="flex items-center gap-3 mb-4 border-b border-gray-800 pb-2">
              <span class="text-jus-gold text-lg">§</span>
              <p class="text-xs text-jus-gold font-ui uppercase tracking-widest">
                JusAI &bull; {{ msg.mode === 'rag' ? 'Consulta Processual' : 'Conhecimento Aberto' }}
              </p>
            </div>
            <div class="text-lg text-gray-300 leading-8 text-justify font-serif">
              <span class="whitespace-pre-wrap">{{ msg.text }}</span>
            </div>
            
            <div v-if="msg.sources && msg.sources.length" class="mt-8 pt-4 border-t border-gray-800">
              <p class="text-[9px] text-gray-500 font-ui uppercase tracking-widest mb-2">Fundamentação Legal:</p>
              <ul class="space-y-2">
                <li v-for="(src, i) in msg.sources" :key="i" class="text-sm text-gray-500 italic pl-4 border-l border-jus-gold/20 font-serif">
                  "{{ src }}"
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-8">
        <span class="text-jus-gold font-serif italic text-sm border-b border-jus-gold/30 pb-1 animate-pulse">
          Analisando doutrina e legislação...
        </span>
      </div>
    </main>

    <footer class="flex-none px-8 py-8 bg-jus-black border-t border-jus-gold-dim/20">
      <div class="max-w-5xl mx-auto flex border border-gray-700 focus-within:border-jus-gold transition-colors duration-300 bg-jus-black">
        <input 
          v-model="question" 
          @keyup.enter="sendMessage"
          :disabled="loading"
          type="text" 
          placeholder="Digite a consulta jurídica..." 
          class="w-full bg-transparent text-gray-200 placeholder-gray-700 px-6 py-4 focus:outline-none font-serif text-lg"
        >
        <button 
          @click="sendMessage"
          :disabled="loading"
          class="bg-jus-gray-light hover:bg-jus-gold hover:text-black text-gray-400 px-10 transition-all duration-300 disabled:opacity-30 border-l border-gray-700 font-ui text-[10px] uppercase tracking-[0.2em] font-bold"
        >
          Enviar
        </button>
      </div>
    </footer>
  </div>
</template>