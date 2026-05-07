<script>
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

export default {
  data() {
    return {
      isOptimizing: false,
      isFirstOptimization: true,
      showLatencyWarning: false,

      optimizationMode: 'human',

      userId: null,
      shareLocationData: true,

      apiUrl: 'https://api.meshwave.com.br/api/v1/condenser/run',

      originalText:
        "Importante: O brilho sutil na cor de destaque atrai o olhar. A Economia de Água é apresentada como métrica clara e direta.",

      optimizedText: "O resultado da otimização aparecerá aqui...",

      condensedChars: 0,
      reductionPercentage: 0,
      h2oSaved: 0,
      energySaved: 0,
      co2Avoided: 0,
    };
  },

  computed: {
    buttonText() {
      return this.isOptimizing ? 'Otimizando...' : 'OTIMIZAR';
    },

    originalTextLength() {
      return this.originalText ? this.originalText.length : 0;
    }
  },

  watch: {
    shareLocationData(val) {
      try {
        localStorage.setItem('meshwalker_consent', JSON.stringify(val));
      } catch (e) {
        console.warn("localStorage error:", e);
      }
    }
  },

  created() {
    this.initSafe();
  },

  methods: {

    // =========================
    // INIT SEGURO (evita tela branca)
    // =========================
    initSafe() {
      try {
        let userId = this.getCookie('meshwalker_user_id');

        if (!userId) {
          userId = uuidv4();
          this.setCookie('meshwalker_user_id', userId, 365);
        }

        this.userId = userId;

      } catch (e) {
        console.warn("user init error:", e);
        this.userId = uuidv4();
      }

      this.calculateImpact(this.originalText.length, 0);
    },

    // =========================
    // API CALL (CORRIGIDO 100%)
    // =========================
    async optimizeText() {
      if (this.isOptimizing || !this.originalText?.trim()) return;

      this.isOptimizing = true;
      this.optimizedText = "Processando...";

      if (this.isFirstOptimization) {
        this.showLatencyWarning = true;
      }

      try {
        const response = await axios.post(
          this.apiUrl,
          {
            text: this.originalText,
            mode: this.optimizationMode
          },
          {
            timeout: 300000,
            headers: {
              "Content-Type": "application/json"
            }
          }
        );

        this.optimizedText =
          response?.data?.condensed_text ||
          "Resposta vazia da API";

        this.calculateImpact(
          this.originalText.length,
          this.optimizedText.length || 0
        );

      } catch (error) {
        console.error("API error:", error);

        this.optimizedText =
          "Erro ao conectar com API MeshWave";

        this.calculateImpact(this.originalText.length, 0);

      } finally {
        this.isOptimizing = false;

        if (this.isFirstOptimization) {
          this.isFirstOptimization = false;

          setTimeout(() => {
            this.showLatencyWarning = false;
          }, 8000);
        }
      }
    },

    // =========================
    // IMPACTO
    // =========================
    calculateImpact(originalLength, condensedLength) {
      const BASE_H2O = 562;
      const BASE_ENERGY = 0.08;
      const BASE_CO2 = 0.5;

      this.condensedChars = condensedLength;

      const reduction =
        originalLength > 0
          ? (1 - condensedLength / originalLength) * 100
          : 0;

      this.reductionPercentage = reduction;

      this.h2oSaved = BASE_H2O * (reduction / 100);
      this.energySaved = BASE_ENERGY * (reduction / 100);
      this.co2Avoided = BASE_CO2 * (reduction / 100);
    },

    // =========================
    // MODOS
    // =========================
    setOptimizationMode(mode) {
      this.optimizationMode = mode;
    },

    clearInputText() {
      this.originalText = '';
      this.optimizedText = 'O resultado da otimização aparecerá aqui...';
      this.calculateImpact(0, 0);
    },

    // =========================
    // COPY
    // =========================
    copyOutputText() {
      if (!this.optimizedText || this.optimizedText.startsWith("Erro")) return;

      navigator.clipboard.writeText(this.optimizedText)
        .then(() => alert("Texto copiado!"))
        .catch(err => console.warn(err));
    },

    // =========================
    // COOKIE SAFE
    // =========================
    setCookie(name, value, days) {
      try {
        const date = new Date();
        date.setTime(date.getTime() + days * 86400000);

        document.cookie =
          `${name}=${value}; expires=${date.toUTCString()}; path=/`;

      } catch (e) {
        console.warn("cookie error:", e);
      }
    },

    getCookie(name) {
      try {
        const cookies = document.cookie.split(';');

        for (let c of cookies) {
          c = c.trim();

          if (c.startsWith(name + "=")) {
            return c.substring(name.length + 1);
          }
        }

        return null;

      } catch (e) {
        return null;
      }
    }
  }
};
</script>

<template>
  <div id="app-container">
    <textarea v-model="originalText"></textarea>

    <button @click="optimizeText" :disabled="isOptimizing">
      {{ buttonText }}
    </button>

    <div>
      {{ optimizedText }}
    </div>
  </div>
</template>
