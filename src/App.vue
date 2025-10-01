<!-- Conteúdo CORRETO para: sofia-command-center/src/App.vue -->
<script setup>
// A única função deste arquivo é importar e renderizar o nosso layout principal.
import CommandCenter from './components/CommandCenter.vue';
</script>

<template>
  <!-- Renderiza o componente que contém toda a lógica e o visual -->
  <CommandCenter />
</template>

<style>
/* Estilos globais que se aplicam a toda a aplicação */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden; /* Previne barras de rolagem indesejadas */
}
</style>

