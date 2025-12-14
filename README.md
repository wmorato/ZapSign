# Desafio Técnico - ZapSign: Módulo de Gestão de Documentos

## 🎯 Objetivo do Projeto

Implementar um novo módulo de gestão de documentos para clientes ZapSign, com foco em:
1.  **CRUD** (Create, Read, Update, Delete) de Documentos e Signatários.
2.  **Integração** com a API ZapSign (Sandbox) para envio de documentos.
3.  **Análise Inteligente** de conteúdo via IA (Gemini/OpenAI) em background.
4.  **Comunicação em Tempo Real** (WebSockets) para atualizações de status.
5.  Exposição de **Endpoints RESTful autenticados** para automações externas (n8n).

## 🏗️ Arquitetura e Tecnologias

O projeto segue uma arquitetura de microsserviços orquestrada via Docker Compose, com forte adesão aos princípios **SOLID** e padrões de **Clean Architecture** no Backend.

| Componente | Tecnologia | Função Principal |
| :--- | :--- | :--- |
| **Backend** | Python, Django, DRF, Pytest | APIs RESTful, Lógica de Negócio, Multi-Tenancy, Integração ZapSign. |
| **Frontend** | Angular 17, TypeScript, Vitest | Interface de Usuário (SPA), Componentes Reativos, Comunicação WebSocket. |
| **Banco de Dados** | PostgreSQL 16 | Persistência de dados (Company, Document, Signer, DocumentAnalysis). |
| **Mensageria** | Redis, Celery | Broker de mensagens, Cache, Processamento assíncrono de tarefas (Análise de IA). |
| **Servidor WS** | Daphne (via Channels) | Servidor ASGI para WebSockets. |
| **Servidor Web** | Nginx (via Docker Frontend) | Proxy Reverso para Backend (API/Auth/WS) e Servidor de Arquivos Estáticos do Frontend. |
| **IA** | Google Gemini, OpenAI | Análise de conteúdo de PDFs (Resumo, Tópicos Faltantes, Insights). |

## 🚀 Quick Start (Setup da Infraestrutura)

Este projeto utiliza Docker Compose para garantir um ambiente de desenvolvimento idêntico ao de produção.

### Pré-requisitos

*   Docker e Docker Compose instalados.
*   Conta no Sandbox da ZapSign e API Token gerado.
*   API Key do Gemini ou OpenAI.

### 1. Configuração Inicial

Crie e configure o arquivo de variáveis de ambiente na pasta `backend`:

```bash
# Na pasta D:\Projetos\DesafioTecnico\ZapSign\backend
cp .env.example .env