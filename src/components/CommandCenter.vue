<script>
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

export default {
  data() {
    return {
      // --- Estado da Aplicação ---
      isOptimizing: false,
      isFirstOptimization: true,
      showLatencyWarning: false,
      optimizationMode: 'human', // 'human' ou 'llm'
      
      // --- Dados do Usuário e Consentimento ---
      userId: null,
      shareLocationData: true,

      // --- Textos ---
      originalText: "Importante: O brilho sutil na cor de destaque atrai o olhar. A Economia de Água é apresentada como uma métrica clara e direta, com um ícone discreto, mas elegante. A lógica aqui é mostrar, não apenas dizer. O usuário vê o benefício ambiental que ele gerou com aquela única otimização.",
      optimizedText: "O resultado da otimização aparecerá aqui...",

      // --- Métricas ---
      originalChars: 0,
      condensedChars: 0,
      reductionPercentage: 0.0,
      h2oSaved: 0,
      energySaved: 0,
      co2Avoided: 0,

      // --- Configuração ---
      apiUrl: ''  // Vazio para paths relativos com proxy Vite. Se CORS configurado no backend, mude para 'http://localhost:8000'
    };
  },
  computed: {
    buttonText() {
      if (this.isOptimizing && this.isFirstOptimization) return 'Ativando Servidores...';
      if (this.isOptimizing) return 'Otimizando...';
      return 'OTIMIZAR';
    }
  },
  watch: {
    shareLocationData(newValue) {
      localStorage.setItem('meshwalker_consent', newValue);
    },
    originalText(newValue) {
      this.originalChars = newValue.length;
      this.calculateImpact(this.originalChars, this.condensedChars);
    }
  },
  created() {
    this.initializeUserId();
    this.loadConsentPreference();
    this.originalChars = this.originalText.length;
    this.calculateImpact(this.originalChars, 0);
  },
  methods: {
    // --- Inicialização ---
    initializeUserId() {
      let userId = this.getCookie('meshwalker_user_id');
      if (!userId) {
        userId = uuidv4();
        this.setCookie('meshwalker_user_id', userId, 365);
      }
      this.userId = userId;
    },
    loadConsentPreference() {
      const consent = localStorage.getItem('meshwalker_consent');
      if (consent !== null) this.shareLocationData = JSON.parse(consent);
    },

    // --- Lógica Principal (AJUSTADA: Removida chamada para logInteraction) ---
    async optimizeText() {
      if (this.isOptimizing || !this.originalText.trim()) return;
      this.isOptimizing = true;
      this.optimizedText = "";
      this.showLatencyWarning = this.isFirstOptimization;

      const prompt = `Modo: ${this.optimizationMode}. Texto: ${this.originalText}`;

      try {
        console.log('Enviando requisição para otimizar:', `${this.apiUrl}/api/v1/condenser/run`);
        const response = await axios.post(`${this.apiUrl}/api/v1/condenser/run`, 
          { text: prompt },
          { timeout: 120000 }
        );
        
        console.log('Resposta recebida:', response.data);
        this.optimizedText = response.data.condensed_text || 'Erro: condensed_text não encontrado na resposta.';

        this.calculateImpact(this.originalText.length, this.optimizedText.length);
        // REMOVIDO: await this.logInteraction(); // Endpoint não existe no backend atual

      } catch (error) {
        console.error("Erro ao otimizar:", error);
        if (error.message.includes('Network Error') || error.code === 'ERR_NETWORK') {
          this.optimizedText = "Erro de rede (possivelmente CORS ou backend offline). Verifique se SOFIA está rodando em http://localhost:8000 e configure CORS ou proxy.";
        } else {
          this.optimizedText = `Ocorreu um erro ao conectar com SOFIA: ${error.message}. Verifique o console.`;
        }
        this.calculateImpact(this.originalText.length, 0);
      } finally {
        this.isOptimizing = false;
        this.isFirstOptimization = false;
        this.showLatencyWarning = false;
      }
    },

    // --- Lógica de Cálculo de Impacto ---
    calculateImpact(originalLength, condensedLength) {
      const BASE_COST_H2O_ML = 562; 
      const BASE_COST_ENERGY_KWH = 0.08;
      const BASE_COST_CO2_G = 0.5;

      this.originalChars = originalLength;
      this.condensedChars = condensedLength;

      const reductionPercentage = originalLength > 0 ? (1 - (condensedLength / originalLength)) * 100 : 0;
      this.reductionPercentage = reductionPercentage;

      this.h2oSaved = BASE_COST_H2O_ML * (reductionPercentage / 100);
      this.energySaved = BASE_COST_ENERGY_KWH * (reductionPercentage / 100);
      this.co2Avoided = BASE_COST_CO2_G * (reductionPercentage / 100);
    },

    // --- Log de Interação (MANTER COMENTADO: Endpoint não existe no backend atual) ---
    async logInteraction() {
      const payload = {
        sponsor: 'Carbon Zero',
        user_id: this.userId,
        reduction_percentage: parseFloat(this.reductionPercentage.toFixed(2)),
        h2o_saved_ml: parseFloat(this.h2oSaved.toFixed(2)),
        energy_saved_kwh: parseFloat(this.energySaved.toFixed(5)),
        co2_avoided_g: parseFloat(this.co2Avoided.toFixed(5)),
        collect_location: this.shareLocationData
      };
      try {
        console.log('Enviando log de interação (se endpoint existir):', `${this.apiUrl}/api/v1/interactions/log`);
        await axios.post(`${this.apiUrl}/api/v1/interactions/log`, payload);
        console.log('Interação logada com sucesso.');
      } catch (error) {
        console.warn("Falha ao registrar interação (endpoint /api/v1/interactions/log não existe no backend).", error);
      }
    },

    // --- Métodos de Utilidade ---
    setOptimizationMode(mode) {
      this.optimizationMode = mode;
    },
    clearInputText() {
      this.originalText = '';
      this.optimizedText = 'O resultado da otimização aparecerá aqui...';
      this.calculateImpact(0, 0);
    },
    copyOutputText() {
      if (!this.optimizedText || this.optimizedText.startsWith("Ocorreu um erro")) return;
      navigator.clipboard.writeText(this.optimizedText).then(() => {
        alert("Texto copiado para a área de transferência!");
      }).catch(err => console.error('Erro ao copiar texto: ', err));
    },

    // --- Funções Auxiliares de Cookie ---
    setCookie(name, value, days) {
      let expires = "";
      if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
      }
      document.cookie = name + "=" + (value || "") + expires + "; path=/";
    },
    getCookie(name) {
      const nameEQ = name + "=";
      const ca = document.cookie.split(';');
      for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
      }
      return null;
    }
  }
};
</script>

<!-- O <template> permanece o mesmo, sem alterações -->
<template>
  <div id="app-container">
    <header class="header">
      <div class="logo">
        <img src="/public/logo_meshwave.svg" alt="MeshWave Logo" style="width: 100%; height: auto;">
      </div>
      <h1 class="title">Command Center</h1>
    </header>

    <div class="main-grid">
      <!-- Coluna da Esquerda com Distribuição Vertical -->
      <div class="left-column">
        
        <div class="card input-card">
          <div class="card-header">
            <div class="card-title">Texto a ser Otimizado</div>
            <button @click="clearInputText" class="utility-btn" title="Limpar texto">Limpar</button>
          </div>
          <textarea v-model="originalText" placeholder="Insira o texto que deseja condensar..."></textarea>
        </div>

        <div class="card actions-card">
          <div class="actions-container">
            <button @click="setOptimizationMode('human')" class="action-btn" :class="{ active: optimizationMode === 'human' }">
              Resumo para Humanos
            </button>
            <button @click="setOptimizationMode('llm')" class="action-btn" :class="{ active: optimizationMode === 'llm' }">
              Otimização para AI/LLM
            </button>
            <button @click="optimizeText" class="optimize-btn-main" :disabled="isOptimizing">
              {{ buttonText }}
            </button>
          </div>
          <div v-if="showLatencyWarning" class="latency-notification">
            <p><strong>Poupar recursos naturais e energia está no DNA de nossa organização.</strong> Por isso, nossos servidores hibernam para minimizar o consumo. Sua primeira interação pode levar até 90 segundos. As seguintes serão instantâneas.</p>
          </div>
        </div>

        <div class="card output-card">
          <div class="card-header">
            <div class="card-title">Resultado Otimizado</div>
            <button @click="copyOutputText" class="utility-btn" title="Copiar resultado">Copiar</button>
          </div>
          <textarea :value="optimizedText" readonly placeholder="O resultado da otimização aparecerá aqui..."></textarea>
        </div>

      </div>

      <!-- Coluna da Direita (Métricas) -->
      <div class="right-column">
        <div class="card">
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">ORIGINAL</div>
              <div class="metric-value">{{ Math.round(originalChars) }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">CONDENSADO</div>
              <div class="metric-value">{{ Math.round(condensedChars) }}</div>
            </div>
            <div class="metric-card reduction">
              <div class="metric-label">REDUÇÃO</div>
              <div class="metric-value">{{ reductionPercentage.toFixed(1) }}%</div>
            </div>
          </div>

          <div class="impact-section">
            <div class="impact-title-main">MIA-D</div>
            <div class="impact-title-sub">Monitor de Impacto Ambiental Digital</div>
            
            <div class="impact-metrics-grid">
              <div class="impact-item">
                <div class="impact-icon">💧</div>
                <div>
                  <div class="impact-metric-label">Economia de Água</div>
                  <div class="impact-metric-value">{{ h2oSaved.toFixed(0) }} <span>ml</span></div>
                </div>
              </div>
              <div class="impact-item">
                <div class="impact-icon">⚡</div>
                <div>
                  <div class="impact-metric-label">Economia de Energia</div>
                  <div class="impact-metric-value">{{ energySaved.toFixed(3) }} <span>kWh</span></div>
                </div>
              </div>
              <div class="impact-item">
                <div class="impact-icon">🌱</div>
                <div>
                  <div class="impact-metric-label">Carbono Evitado</div>
                  <div class="impact-metric-value">{{ co2Avoided.toFixed(2) }} <span>gCO₂eq</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="sponsor-section">
            <div class="sponsor-logo">
              <img src="/public/logo_carbonzero.jpg" alt="Logo Carbon Zero" style="background: white; padding: 5px; border-radius: 8px;">
            </div>
            <div class="sponsor-label">Patrocinador Oficial</div>
          </div>

          <div class="privacy-consent">
            <input type="checkbox" id="consent-checkbox" v-model="shareLocationData">
            <label for="consent-checkbox">
              Concordo com a coleta do meu IP. <strong>Finalidade exclusiva:</strong> gerar dados geográficos agregados sobre o impacto ambiental.
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
