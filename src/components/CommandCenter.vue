<!--
Projeto: SOFIA Command Center
Versão: 3.2 (Layout Responsivo Corrigido)
Data: 06/10/2025
Arquivo: /home/mesh/sofia-command-center/src/components/CommandCenter.vue
-->
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// --- Configurações ---
const API_BASE_URL = 'https://sofia-ctl8.onrender.com';
const CONDENSER_ENDPOINT = '/api/v1/condenser/run';

// --- Lista de IAs e Estado de Navegação ---
const availableIAs = ref([
  { name: 'Simulador Local', url: '/fake-ia.html' },
  { name: 'ChatGPT', url: 'https://chat.openai.com/' },
  { name: 'Google Gemini', url: 'https://gemini.google.com/' },
  { name: 'Claude', url: 'https://claude.ai/' },
]  );
const currentIaUrl = ref(availableIAs.value[0].url);

// --- Estado da Interface ---
const originalPrompt = ref('');
const condensedPrompt = ref('');
const isLoading = ref(false);
const error = ref(null);
const condensationMode = ref('summary');
const iframeRef = ref(null);

// --- Estado para o Placar Consolidado ---
const totalWaterSaved = ref(0);
const totalCarbonSaved = ref(0);

// --- Métricas da Última Otimização ---
const lastReduction = ref({
  original: 0,
  condensed: 0,
  percentage: 0,
  water: 0,
  carbon: 0,
});

// --- Constantes de Cálculo ---
const WATER_SAVED_AT_100_PERCENT = 652;
const CARBON_SAVED_AT_100_PERCENT = 0.40;

// --- Funções ---

onMounted(() => {
  totalWaterSaved.value = parseFloat(localStorage.getItem('totalWaterSaved') || 0);
  totalCarbonSaved.value = parseFloat(localStorage.getItem('totalCarbonSaved') || 0);
});

async function handleCondense() {
  if (!originalPrompt.value.trim()) return;
  isLoading.value = true;
  error.value = null;
  condensedPrompt.value = '';

  try {
    const response = await axios.post(`${API_BASE_URL}${CONDENSER_ENDPOINT}`, {
      text: originalPrompt.value,
      mode: condensationMode.value
    });
    condensedPrompt.value = response.data.condensed_text;

    const originalLength = originalPrompt.value.length;
    const condensedLength = condensedPrompt.value.length;
    const reductionPercentage = ((1 - (condensedLength / originalLength)) * 100);
    const waterSaved = (WATER_SAVED_AT_100_PERCENT * (reductionPercentage / 100));
    const carbonSaved = (CARBON_SAVED_AT_100_PERCENT * (reductionPercentage / 100));

    lastReduction.value = {
      original: originalLength,
      condensed: condensedLength,
      percentage: reductionPercentage,
      water: waterSaved,
      carbon: carbonSaved,
    };

    totalWaterSaved.value += waterSaved;
    totalCarbonSaved.value += carbonSaved;

    localStorage.setItem('totalWaterSaved', totalWaterSaved.value);
    localStorage.setItem('totalCarbonSaved', totalCarbonSaved.value);

  } catch (err) {
    error.value = "Falha ao conectar ao Agente Condensador.";
  } finally {
    isLoading.value = false;
  }
}

function injectToIA() {
  if (!condensedPrompt.value || !iframeRef.value) return;
  
  try {
    const targetTextarea = iframeRef.value.contentWindow.document.getElementById('ia-prompt-textarea');
    if (targetTextarea) {
      targetTextarea.value = condensedPrompt.value;
      targetTextarea.focus();
    } else {
      console.warn("Não foi possível encontrar o campo de texto ('ia-prompt-textarea') no iframe. A injeção só funciona no simulador local.");
      alert("A injeção de texto automática só é compatível com o 'Simulador Local'. Para outras IAs, por favor, copie e cole o texto manualmente.");
    }
  } catch (e) {
    console.error("Erro de segurança ao tentar acessar o conteúdo do iframe. Isso é esperado ao carregar sites de terceiros (ex: ChatGPT).", e);
    alert("Não é possível interagir com o conteúdo de sites externos por motivos de segurança do navegador. Por favor, copie e cole o texto otimizado manualmente.");
  }
}
</script>

<template>
  <div class="command-center-layout">
    <!-- Coluna Esquerda: Área da IA -->
    <div class="ia-area">
      <header class="ia-header">
        <select v-model="currentIaUrl" class="ia-selector">
          <option v-for="ia in availableIAs" :key="ia.url" :value="ia.url">
            {{ ia.name }}
          </option>
        </select>
      </header>
      <iframe :src="currentIaUrl" ref="iframeRef" class="ia-iframe" sandbox="allow-forms allow-scripts allow-same-origin allow-popups"></iframe>
    </div>

    <!-- Coluna Divisória -->
    <div class="layout-divider"></div>

    <!-- Coluna Direita: SOFIA Sidecar -->
    <div class="sofia-sidecar">
      <header class="sidecar-header">
        <img src="/logo_meshwave.svg" alt="MeshWave Logo" />
        <h1>SOFIA Command Center</h1>
      </header>
      
      <section class="scoreboard">
        <h2>Monitor de Impacto Ambiental (MIA)</h2>
        <div class="scoreboard-metrics current-optimization">
          <div class="scoreboard-item">
            <span>💧 Água</span>
            <p>{{ lastReduction.water.toFixed(0) }} <span>ml</span></p>
            <span class="sublabel">DA OTIMIZAÇÃO</span>
          </div>
          <div class="scoreboard-item">
            <span>🍃 Carbono</span>
            <p>{{ lastReduction.carbon.toFixed(2) }} <span>gCO₂eq</span></p>
            <span class="sublabel">DA OTIMIZAÇÃO</span>
          </div>
        </div>
        <div class="scoreboard-metrics consolidated-session">
          <div class="scoreboard-item">
            <p>{{ totalWaterSaved.toFixed(0) }} <span>ml</span></p>
            <span class="sublabel">Consolidado da Sessão</span>
          </div>
          <div class="scoreboard-item">
            <p>{{ totalCarbonSaved.toFixed(2) }} <span>gCO₂eq</span></p>
            <span class="sublabel">Consolidado da Sessão</span>
          </div>
        </div>
      </section>

      <div class="sidecar-content">
        <div class="prompt-box original-box">
          <label for="original-prompt">1. Escreva seu prompt aqui:</label>
          <textarea id="original-prompt" v-model="originalPrompt"></textarea>
        </div>

        <div class="controls">
          <div class="mode-selector">
            <button @click="condensationMode = 'summary'" :class="{active: condensationMode === 'summary'}">Resumo</button>
            <button @click="condensationMode = 'llm_optimization'" :class="{active: condensationMode === 'llm_optimization'}">Otimização LLM</button>
          </div>
          <button @click="handleCondense" :disabled="isLoading" class="optimize-btn">
            {{ isLoading ? 'Otimizando...' : '2. Otimizar Texto' }}
          </button>
        </div>

        <div class="prompt-box condensed-box">
          <label for="condensed-prompt">3. Resultado Otimizado:</label>
          <textarea id="condensed-prompt" v-model="condensedPrompt" readonly></textarea>
        </div>

        <button @click="injectToIA" :disabled="!condensedPrompt" class="inject-btn">
          🚀 Injetar na IA
        </button>
      </div>
    </div>
  </div>
</template>

<style>
/* Estilos Globais */
html, body { margin: 0; padding: 0; height: 100%; font-family: 'Segoe UI', sans-serif; background-color: #1e1e1e; color: #e0e0e0; overflow: hidden; }

.command-center-layout { display: flex; height: 100vh; width: 100vw; }

/* Layout com Coluna Divisória */
.ia-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; 
}

.layout-divider {
  width: 10px;
  flex-shrink: 0;
  background-color: #1e1e1e;
}

.sofia-sidecar {
  width: 30%;
  flex-shrink: 0;
  /* [CORREÇÃO] Transforma o sidecar em um contêiner flex vertical */
  display: flex; 
  flex-direction: column;
  background-color: #2a2a2a;
  /* [CORREÇÃO] Garante que a altura não ultrapasse a da tela */
  height: 100vh;
}

.ia-header { padding: 8px 10px; background-color: #2a2a2a; border-bottom: 1px solid #444; }
.ia-selector {
  width: 100%;
  padding: 6px 8px;
  border-radius: 4px;
  border: 1px solid #555;
  background-color: #1e1e1e;
  color: #ccc;
  box-sizing: border-box;
  font-size: 0.8rem;
}

.ia-iframe { width: 100%; height: 100%; border: none; }

.sidecar-header { display: flex; align-items: center; gap: 1rem; padding: 8px 15px; border-bottom: 1px solid #444; flex-shrink: 0; }
.sidecar-header img { height: 24px; }
.sidecar-header h1 { font-size: 1rem; font-weight: 300; margin: 0; }
.scoreboard { padding: 15px; background-color: #333; text-align: center; border-bottom: 1px solid #444; flex-shrink: 0; }
.scoreboard h2 { margin: 0 0 0.8rem 0; font-size: 0.9rem; font-weight: 600; color: #00aaff; text-transform: uppercase; }
.scoreboard-metrics { display: flex; justify-content: space-around; align-items: baseline; }
.scoreboard-item { display: flex; flex-direction: column; }
.scoreboard-item span { font-size: 0.7rem; color: #aaa; }
.scoreboard-item p { margin: 0.1rem 0 0 0; }
.scoreboard-item p span { font-weight: normal; }
.sublabel { text-transform: uppercase; }
.current-optimization { margin-bottom: 1rem; }
.current-optimization .scoreboard-item p { font-size: 1.2rem; font-weight: bold; }
.current-optimization .scoreboard-item p span { font-size: 0.8rem; }
.current-optimization .sublabel { font-size: 0.6rem !important; color: #888 !important; margin-top: 2px; }
.consolidated-session .scoreboard-item p { font-size: 0.9rem; font-weight: normal; color: #ccc; }
.consolidated-session .scoreboard-item p span { font-size: 0.7rem; }
.consolidated-session .sublabel { font-size: 0.6rem !important; color: #777 !important; margin-top: 2px; }

.sidecar-content { 
  padding: 15px; 
  display: flex; 
  flex-direction: column; 
  gap: 10px; 
  /* [CORREÇÃO] Faz esta área crescer para ocupar o espaço vertical restante */
  flex-grow: 1; 
  min-height: 0; 
  /* [CORREÇÃO] Remove o overflow hidden que escondia o conteúdo */
}

.prompt-box { 
  display: flex; 
  flex-direction: column; 
  /* [CORREÇÃO] Define que as caixas de prompt devem crescer igualmente */
  flex-grow: 1;
  /* [CORREÇÃO] Necessário para que o flex-grow funcione corretamente em contêineres aninhados */
  min-height: 0;
}

/* [REMOVIDO] As regras abaixo não são mais necessárias, pois o flex-grow cuida disso */
/* .prompt-box.original-box { flex: 2; min-height: 0; } */
/* .prompt-box.condensed-box { flex: 2; min-height: 0; } */

.prompt-box label { display: block; margin-bottom: 0.4rem; font-weight: 600; font-size: 0.85rem; }

.prompt-box textarea { 
  width: 100%; 
  /* [CORREÇÃO] Faz o textarea preencher 100% da altura do seu pai (.prompt-box) */
  height: 100%; 
  background-color: #1e1e1e; 
  border: 1px solid #444; 
  border-radius: 4px; 
  color: #e0e0e0; 
  padding: 8px; 
  font-size: 0.9rem; 
  box-sizing: border-box; 
  /* [CORREÇÃO] Impede o redimensionamento manual que quebra o layout */
  resize: none; 
}

.controls { flex-shrink: 0; }
.inject-btn { flex-shrink: 0; }
.mode-selector { display: flex; }
.mode-selector button { flex: 1; padding: 5px 8px; border: 1px solid #444; background-color: #333; color: #ccc; cursor: pointer; font-size: 0.8rem; }
.mode-selector button:first-child { border-radius: 4px 0 0 4px; }
.mode-selector button:last-child { border-radius: 0 4px 4px 0; }
.mode-selector button.active { background-color: #007acc; color: white; border-color: #007acc; }
.optimize-btn, .inject-btn { width: 100%; padding: 6px 8px; font-size: 0.85rem; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; transition: background-color 0.2s; box-sizing: border-box; }
.optimize-btn { background-color: #007acc; color: white; }
.inject-btn { background-color: #28a745; color: white; }
.optimize-btn:disabled, .inject-btn:disabled { background-color: #555; cursor: not-allowed; }
</style>

