# Knowledge Base - Frontend Testing

Este documento contém soluções para problemas comuns encontrados ao configurar e executar testes com Jest e Angular.

## 📋 Índice

- [Configuração Inicial](#configuração-inicial)
- [Problemas Comuns e Soluções](#problemas-comuns-e-soluções)
- [Padrões de Teste](#padrões-de-teste)
- [Exemplos Práticos](#exemplos-práticos)
- [Referências](#referências)

---

## Configuração Inicial

### Por que Jest em vez de Karma/Jasmine?

- ⚡ **Mais rápido**: Execução de testes mais rápida que Karma.
- 🎯 **Melhor DX**: Mensagens de erro mais claras e sintaxe moderna.
- 🔧 **Configuração simples**: `jest-preset-angular` facilita a integração.

### Configuração do jest.config.js

```javascript
// jest.config.js
module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/src/test/jest-setup.ts'],
  globalSetup: 'jest-preset-angular/global-setup',
  testEnvironment: 'jsdom',
  // ... outras configurações
};