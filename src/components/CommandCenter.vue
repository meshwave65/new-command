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

      originalText: "Importante: O brilho sutil na cor de destaque atrai o olhar. A Economia de Água é apresentada como uma métrica clara e direta, com um ícone discreto, mas elegante. A lógica aqui é mostrar, não apenas dizer. O usuário vê o benefício ambiental que ele gerou com aquela única otimização.",

      optimizedText: "O resultado da otimização aparecerá aqui...",

      condensedChars: 0,
      reductionPercentage: 0.0,
      h2oSaved: 0,
      energySaved: 0,
      co2Avoided: 0,

      // 🔥 BASE URL CENTRALIZADA (IMPORTANTE)
      apiBaseUrl: 'https://api.meshwave.com.br'
    };
  },

  computed: {
    buttonText() {
      return this.isOptimizing ? 'Otimizando...' : 'OTIMIZAR';
    },

    originalTextLength() {
      return this.originalText.length;
    }
  },

  watch: {
    shareLocationData(newValue) {
      localStorage.setItem('meshwalker_consent', JSON.stringify(newValue));
    },

    originalText(newText) {
      if (!this.isOptimizing && this.optimizedText.startsWith('O resultado')) {
        this.calculateImpact(newText.length, 0);
      }
    }
  },

  created() {
    this.initializeUserId();
    this.loadConsentPreference();
    this.calculateImpact(this.originalText.length, 0);
  },

  methods: {

    // ==============================
    // USER ID
    // ==============================
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
      if (consent !== null) {
        this.shareLocationData = JSON.parse(consent);
      }
    },

    // ==============================
    // 🔥 API CALL CORRIGIDA
    // ==============================
    async optimizeText() {
      if (this.isOptimizing || !this.originalText.trim()) return;

      this.isOptimizing = true;
      this.optimizedText = "Processando...";

      if (this.isFirstOptimization) {
        this.showLatencyWarning = true;
      }

      try {
        const url = `${this.apiBaseUrl}/api/v1/condenser/run`;

        const response = await axios.post(
          url,
          {
            text: this.originalText,
            mode: this.optimizationMode,
            user_id: this.userId
          },
          {
            timeout: 300000,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );

        this.optimizedText =
          response?.data?.condensed_text ??
          "Erro: resposta inválida da API.";

        this.calculateImpact(
          this.originalText.length,
          this.optimizedText.length || 0
        );

      } catch (error) {
        console.error("Erro na chamada da API:", error);

        this.optimizedText =
          "Erro ao conectar com o servidor. Verifique API / CORS / rede.";

        this.calculateImpact(this.originalText.length, 0);

      } finally {
        this.isOptimizing = false;

        if (this.isFirstOptimization) {
          this.isFirstOptimization = false;

          setTimeout(() => {
            this.showLatencyWarning = false;
          }, 10000);
        }
      }
    },

    // ==============================
    // IMPACTO AMBIENTAL
    // ==============================
    calculateImpact(originalLength, condensedLength) {
      const BASE_COST_H2O_ML = 562;
      const BASE_COST_ENERGY_KWH = 0.08;
      const BASE_COST_CO2_G = 0.5;

      this.condensedChars = condensedLength;

      const reductionPercentage =
        originalLength > 0
          ? (1 - (condensedLength / originalLength)) * 100
          : 0;

      this.reductionPercentage = reductionPercentage;

      this.h2oSaved = BASE_COST_H2O_ML * (reductionPercentage / 100);
      this.energySaved = BASE_COST_ENERGY_KWH * (reductionPercentage / 100);
      this.co2Avoided = BASE_COST_CO2_G * (reductionPercentage / 100);
    },

    // ==============================
    // MODOS
    // ==============================
    setOptimizationMode(mode) {
      this.optimizationMode = mode;
    },

    clearInputText() {
      this.originalText = '';
      this.optimizedText = 'O resultado da otimização aparecerá aqui...';
      this.calculateImpact(0, 0);
    },

    // ==============================
    // COPY
    // ==============================
    copyOutputText() {
      if (
        !this.optimizedText ||
        this.optimizedText.startsWith("Erro") ||
        this.optimizedText.startsWith("O resultado")
      ) return;

      navigator.clipboard.writeText(this.optimizedText)
        .then(() => alert("Texto copiado!"))
        .catch(err => console.error('Erro ao copiar:', err));
    },

    // ==============================
    // COOKIES
    // ==============================
    setCookie(name, value, days) {
      let expires = "";

      if (days) {
        const date = new Date();
        date.setTime(date.getTime() + days * 86400000);
        expires = "; expires=" + date.toUTCString();
      }

      document.cookie = `${name}=${value || ""}${expires}; path=/`;
    },

    getCookie(name) {
      const nameEQ = name + "=";
      const ca = document.cookie.split(';');

      for (let c of ca) {
        while (c.charAt(0) === ' ') c = c.substring(1);
        if (c.indexOf(nameEQ) === 0) {
          return c.substring(nameEQ.length);
        }
      }

      return null;
    }
  }
};
</script>
