# ZapSign Backend

## Visão Geral

Este backend foi projetado para ser consumido não apenas pelo frontend Angular, mas também por **terceiros**, **automações (n8n)** e **sistemas externos** que desejem gerar **insights, relatórios e análises inteligentes** a partir de documentos assinados via ZapSign.

A API expõe endpoints REST, Webhooks e WebSockets, com autenticação via **JWT** (usuários) e **API Keys** (integrações), permitindo fácil integração com pipelines de dados, BI, CRMs, ERPs e ferramentas de automação.

---

## Arquitetura

* Django + Django REST Framework
* PostgreSQL
* Celery + Redis (processamento assíncrono)
* Django Channels (WebSocket)
* Integração ZapSign
* Camada de IA desacoplada e extensível

Fluxo resumido:

1. Documento é criado
2. ZapSign gera assinatura
3. Conteúdo do PDF é extraído
4. IA analisa o conteúdo
5. Resultados são persistidos
6. Eventos são propagados via WebSocket
7. APIs expõem dados para consumo externo

---

## Exposição de APIs para Terceiros

### Autenticação por API Key

Integrações externas devem utilizar **API Keys**, sem necessidade de login ou JWT.

Header obrigatório:

```
X-API-KEY: <sua_api_key>
```

### Geração de API Key (Integrações)

O backend possui um comando dedicado para geração de tokens de integração.

```bash
docker compose exec backend python manage.py create_api_key "n8n_automation"
```

Saída esperada:

```
API Key criada para n8n_automation:
ed124ecbb42a401e5980341251c40de7a4a9649ab921579d0cdb5cb0c029be41
```

Essa chave pode ser usada por:

* n8n
* Sistemas externos
* Scripts de BI
* Processos de auditoria

---

## Integração com n8n

O projeto já inclui um **fluxo n8n funcional**, localizado em:

```
backend/Docs/N8N_FLOWS/Envio de Email de Alerta de mensagem.json
```

### O que esse fluxo faz

* Consulta documentos assinados
* Gera relatórios diários
* Envia alertas por e-mail
* Utiliza os endpoints de automação
* Usa autenticação por API Key

Este fluxo foi **testado** e pode ser adaptado para:

* Slack
* WhatsApp
* CRM
* ERP
* Data Warehouse

---

## Endpoints de Automação (Consumo Externo)

### Consultar Análise de Documento

```bash
curl --location 'http://localhost:8000/api/automations/documents/24/analysis/' \
--header 'X-API-KEY: SUA_API_KEY'
```

Retorna:

* Resumo do contrato
* Pontos de risco
* Tópicos ausentes
* Insights jurídicos

---

### Reanalisar Documento

```bash
curl --location --request POST 'http://localhost:8000/api/automations/documents/24/reanalyze/' \
--header 'X-API-KEY: SUA_API_KEY'
```

Utilizado quando:

* Prompt foi alterado
* Modelo de IA mudou
* Novas regras de análise foram adicionadas

---

### Relatórios Automatizados

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

Permite geração de:

* Relatórios mensais
* Auditorias
* Dashboards externos

---

## Lógica de IA

### Como funciona

1. PDF é obtido (URL ou Base64)
2. Texto é extraído
3. Contexto é montado
4. Prompt é enviado ao modelo
5. Resposta é normalizada
6. Resultado é persistido

### Onde configurar a IA

Arquivo principal:

```
app/ai/ai_service.py
```

### Alterar o contexto da análise

O contexto enviado para a IA pode ser ajustado diretamente no prompt base:

* Linguagem jurídica
* Ênfase em riscos
* Ênfase em cláusulas abusivas
* Compliance
* LGPD

Isso permite criar **perfis de análise** por empresa ou integração.

---

## Adicionar Novos Modelos de IA

O sistema foi desenhado para permitir múltiplos modelos.

Para adicionar um novo:

1. Criar um adapter em `ai_service.py`
2. Implementar método `analyze(text, context)`
3. Registrar o modelo por nome
4. Configurar chave via `.env`

Exemplos suportados:

* Google Gemini
* OpenAI GPT
* Azure OpenAI
* LLM local

---

## WebSocket (Tempo Real)

O backend notifica eventos automaticamente.

### Eventos disponíveis

* `document_created`
* `document_updated`
* `document_deleted`
* `analysis_completed`
* `analysis_failed`

### Uso

* Frontend em tempo real
* Dashboards externos
* Painéis de monitoramento

---

## Webhook ZapSign

Endpoint:

```
POST /webhook/zapsign/
```

Utilizado para:

* Atualizar status do documento
* Atualizar status de signatários
* Salvar link final do PDF assinado

---

## Swagger e OpenAPI

### Swagger UI

```
http://localhost:8000/api/docs/
```

### Schema JSON (Postman)

```
http://localhost:8000/api/schema.json
```

---

## Testes

```bash
pytest
pytest --cov=app --cov-report=html
```

Cobertura atual superior a **70%**, incluindo:

* IA
* Automações
* Webhooks
* Autenticação

---

## Conclusão

Este backend foi projetado para:

* Ser consumido por múltiplos sistemas
* Escalar integrações
* Facilitar automações
* Gerar insights de alto valor
* Permitir evolução contínua da IA

Ele atende cenários reais de produção, auditoria e análise inteligente de contratos.
