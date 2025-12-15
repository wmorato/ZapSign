# ZapSign - Frontend

## Visão Geral

Este diretório contém o **frontend** do projeto ZapSign, desenvolvido em **Angular 17** utilizando **Standalone Components**, **Reactive Forms**, **Jest** para testes automatizados e integração completa com o backend Django via API REST e WebSocket.

O frontend é responsável por:

* Autenticação de usuários
* Gestão de documentos e signatários
* Visualização de relatórios
* Exibição do status de análises de IA em tempo real
* Integração com WebSocket para atualização automática de eventos

---

## Tecnologias Utilizadas

* Angular 17
* TypeScript
* RxJS
* Angular Reactive Forms
* Jest (testes unitários)
* WebSocket
* Docker

---

## Pré-requisitos

* Node.js 20+
* NPM 9+
* Docker e Docker Compose (opcional)

---

## Instalação

```bash
cd frontend
npm install
```

---

## Execução do Projeto

### Modo Desenvolvimento

```bash
npm start
```

A aplicação ficará disponível em:

```
http://localhost:4200
```

### Usando Docker

```bash
docker compose up -d frontend
```

---

## Estrutura de Pastas (Resumo)

```
src/app
├── core
│   ├── auth
│   ├── components
│   ├── interceptors
│   └── services
├── features
│   ├── auth
│   ├── company
│   ├── dashboard
│   └── document
└── shared
```

---

## Funcionalidades Principais

### Autenticação

* Tela de login integrada ao backend
* Interceptor HTTP injeta automaticamente o token de autenticação

### Dashboard

* Visão geral das funcionalidades
* Acesso rápido para documentos, empresas e relatórios

### Gestão de Empresas

* Listagem de empresas
* Visualização e gerenciamento de tokens de API

### Gestão de Documentos

* Criação de documentos por URL ou upload de PDF
* Gestão de signatários
* Status do documento sincronizado com ZapSign

### Análise por IA

* Exibição do status da análise
* Indicadores visuais para documentos com IA pendente ou concluída

### Relatórios

* Filtro por período
* Cards dinâmicos de status
* Exportação de dados

---

## Integração com WebSocket

O frontend se conecta automaticamente ao backend via **WebSocket** para:

* Atualização em tempo real do status dos documentos
* Atualização de signatários
* Notificação de conclusão da análise por IA

Essa comunicação elimina a necessidade de polling e mantém a interface sempre sincronizada.

---

## Testes Automatizados

O projeto possui cobertura extensa de testes unitários utilizando **Jest**.

### Executar testes

```bash
npm test
```

### Gerar relatório de cobertura

```bash
npm test -- --coverage
```

Relatório gerado em:

```
coverage/
```

---

## Integração com Backend

* Todas as chamadas de API passam pelo `ApiService`
* Interceptor de autenticação adiciona automaticamente headers
* Endpoints documentados via Swagger no backend

Exemplo de endpoint consumido:

```
GET /api/document/
```

---

## Observações Importantes

* O frontend foi projetado para desacoplamento total do backend
* É possível substituir ou evoluir a camada de IA sem impacto visual
* Componentes seguem boas práticas de SOLID e separação de responsabilidades

---

## Considerações Finais

Este frontend foi desenvolvido com foco em clareza, escalabilidade e testabilidade, atendendo plenamente aos critérios de um desafio técnico profissional e facilitando futuras evoluções do sistema.
