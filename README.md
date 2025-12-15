# ZapSign – Desafio Técnico (Gestão de Documentos com IA)

## Visão Geral

Este projeto implementa um sistema completo de **gestão de documentos com assinatura eletrônica**, integrado à ZapSign, incluindo **análise inteligente de contratos via IA**, processamento assíncrono, **WebSockets para atualização em tempo real**, webhooks e **endpoints de automação** protegidos por API Key.

O objetivo do projeto é demonstrar uma solução próxima de um cenário real de produção, cobrindo backend, frontend, testes automatizados, documentação e integração com serviços externos.

---

## Arquitetura Geral

* **Backend:** Django 5 + Django REST Framework
* **Frontend:** Angular 17 (SPA)
* **Banco de dados:** PostgreSQL
* **Fila / Assíncrono:** Celery + Redis
* **WebSockets:** Django Channels
* **Integração externa:** ZapSign (documentos e signatários)
* **IA:** Análise automática de contratos (resumo, riscos e tópicos ausentes)
* **Infraestrutura local:** Docker + Docker Compose
* **Documentação da API:** Swagger (OpenAPI – 100% funcional)

---

## Como subir o sistema

### Pré-requisitos

* Docker
* Docker Compose
* Git

### Clonar o projeto

```bash
git clone https://github.com/wmorato/ZapSign.git
cd ZapSign
```

### Subir o backend e serviços

```bash
cd backend/docker
docker-compose build
docker-compose up -d
```

### Subir o frontend

```bash
cd frontend
npm install
npm start
```

---

## Endereços importantes

* **Frontend:** [http://localhost:4200](http://localhost:4200)
* **Backend API:** [http://localhost:8000](http://localhost:8000)
* **Swagger UI:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
* **OpenAPI JSON:** [http://localhost:8000/api/schema.json](http://localhost:8000/api/schema.json)

---

## Documentações específicas

* **Backend:** `backend/README.md`
* **Frontend:** `frontend/README.md`

Esses documentos detalham configuração de ambiente, testes, arquitetura interna e decisões técnicas.

---

## Funcionalidades principais

* Cadastro e gerenciamento de documentos
* Cadastro e gerenciamento de signatários
* Integração com ZapSign para criação, atualização e exclusão de documentos
* Análise automática de documentos via IA
* Reanálise manual de documentos
* Relatórios automatizados por período
* Webhook ZapSign para sincronização de status
* Atualizações em tempo real via WebSocket
* Endpoints de automação protegidos por API Key (uso externo, ex: n8n)

---

## Consumo de endpoints (exemplos)

### Consultar análise de um documento

```bash
curl --location 'http://localhost:8000/api/automations/documents/24/analysis/' \
--header 'X-API-KEY: SUA_API_KEY'
```

### Reanalisar documento

```bash
curl --location --request POST \
'http://localhost:8000/api/automations/documents/24/reanalyze/' \
--header 'X-API-KEY: SUA_API_KEY'
```

### Gerar relatório por período

```bash
curl --location 'http://localhost:8000/api/automations/reports/' \
--header 'X-API-KEY: SUA_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
  "report_type": "monthly_summary",
  "start_date": "2025-12-13",
  "end_date": "2025-12-13",
  "company_id": 7
}'
```

---

## Webhook ZapSign

Endpoint utilizado pela ZapSign para notificar eventos de documentos e signatários:

```
POST http://<host>:<porta>/webhook/zapsign/
```

Esse webhook mantém o sistema sincronizado com o status real dos documentos assinados.

---

## WebSockets

O sistema utiliza WebSockets para notificar o frontend em tempo real sobre:

* Criação de documentos
* Atualização de status
* Finalização de análises de IA
* Exclusão de documentos

Isso garante uma experiência reativa sem necessidade de polling.

---

## Lógica de IA (resumo)

1. Um documento é criado (URL ou PDF Base64)
2. O conteúdo do PDF é extraído automaticamente
3. Uma tarefa assíncrona é disparada via Celery
4. A IA realiza:

   * Resumo do contrato
   * Identificação de riscos
   * Detecção de tópicos ausentes
5. O resultado é salvo no banco
6. O frontend é notificado via WebSocket

---

## Testes automatizados

### Backend

```bash
pytest
```

Cobertura:

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Frontend

```bash
npm test
```

Cobertura:

```bash
npm test -- --coverage
```

---

## Considerações finais

Este projeto foi desenvolvido com foco em **boas práticas de arquitetura**, **testabilidade**, **segurança**, **documentação clara** e **integração realista com serviços externos**, simulando um ambiente próximo ao de produção.
