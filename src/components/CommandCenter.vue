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

      apiBaseUrl: 'https://api.meshwave.com.br',

      originalText:
        "Importante: O brilho sutil na cor de destaque atrai o olhar. A Economia de Água é apresentada como uma métrica clara e direta.",

      optimizedText: "O resultado da otimização aparecerá aqui...",

      condensedChars: 0,
      reductionPercentage: 0.0,
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
    shareLocationData(newValue) {
      try {
        localStorage.setItem('meshwalker_consent', JSON.stringify(newValue));
      } catch (e) {
        console.warn("LocalStorage error:", e);
      }
    },

    originalText(newText) {
      if (
        !this.isOptimizing &&
        this.optimizedText &&
        this.optimizedText.startsWith('O resultado')
      ) {
        this.calculateImpact(newText?.length || 0, 0);
      }
    }
  },

  created() {
    this.safeInit();
  },

  methods: {

    // ==========================
    // SAFE INIT (evita crash total)
    // ==========================
    safeInit() {
      try {
        this.initializeUserId();
      } catch (e) {
        console.error("init userId error:", e);
        this.userId = uuidv4();
      }

      try {
        this.loadConsentPreference();
      } catch (e) {
        console.error("consent error:", e);
        this.shareLocationData = true;
      }

      try {
        this.calculateImpact(this.originalText.length, 0);
      } catch (e) {
        console.error("impact error:", e);
      }
    },

    // ==========================
    // USER ID
    // ==========================
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

    // ==========================
    // API CALL (ROBUSTA)
    // ==========================
    async optimizeText() {
      if (this.isOptimizing || !this.originalText?.trim()) return;

      this.isOptimizing = true;
      this.optimizedText = "Processando...";

      if (this.isFirstOptimization) {
        this.showLatencyWarning = true;
      }

      try {
        const url =
          `${this.apiBaseUrl}/api/v1/condenser/run`;

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
          response?.data?.condensed_text ||
          "Resposta inválida da API";

        this.calculateImpact(
          this.originalText.length,
          this.optimizedText.length || 0
        );

      } catch (error) {
        console.error("API error:", error);

        this.optimizedText =
          "Erro ao conectar com servidor MeshWave";

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

    // ==========================
    // IMPACTO
    // ==========================
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

    // ==========================
    // MODOS
    // ==========================
    setOptimizationMode(mode) {
      this.optimizationMode = mode;
    },

    clearInputText() {
      this.originalText = '';
      this.optimizedText = 'O resultado da otimização aparecerá aqui...';
      this.calculateImpact(0, 0);
    },

    // ==========================
    // COPY SAFE
    // ==========================
    copyOutputText() {
      if (
        !this.optimizedText ||
        this.optimizedText.startsWith("Erro") ||
        this.optimizedText.startsWith("O resultado")
      ) return;

      navigator.clipboard.writeText(this.optimizedText)
        .then(() => alert("Copiado!"))
        .catch(err => console.warn("copy error:", err));
    },

    // ==========================
    // COOKIE SAFE
    // ==========================
    setCookie(name, value, days) {
      try {
        let expires = "";

        if (days) {
          const date = new Date();
          date.setTime(date.getTime() + days * 86400000);
          expires = "; expires=" + date.toUTCString();
        }

        document.cookie = `${name}=${value}${expires}; path=/`;
      } catch (e) {
        console.warn("cookie error:", e);
      }
    },

    getCookie(name) {
      try {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');

        for (let c of ca) {
          while (c.charAt(0) === ' ') c = c.substring(1);

          if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length);
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
