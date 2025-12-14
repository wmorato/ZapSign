# ZapSign Backend - Desafio Técnico

## Visão Geral

Este projeto implementa o backend para o desafio técnico da ZapSign, focado na gestão de documentos, integração com a API ZapSign, análise de conteúdo via Inteligência Artificial (IA) e automações via n8n.

A arquitetura segue os princípios SOLID e utiliza Django com Django Rest Framework (DRF), PostgreSQL, Celery e Redis para processamento assíncrono e WebSockets (Channels) para comunicação em tempo real.

## Stacks Utilizadas

*   **Framework:** Python 3.11, Django 5.2, Django Rest Framework (DRF)
*   **Banco de Dados:** PostgreSQL
*   **Assíncrono/Mensageria:** Celery, Redis
*   **IA:** Google Gemini (padrão) e OpenAI (GPT-4)
*   **WebSockets:** Django Channels, Redis Channel Layer
*   **Infraestrutura Local:** Docker, Docker Compose
*   **Utilitários:** PyPDF2 (extração de texto de PDF)

## Configuração e Setup Local

### Pré-requisitos

1.  Docker e Docker Compose instalados.
2.  Conta no Sandbox da ZapSign para obter o `api_token`.
3.  Chave de API do Google Gemini ou OpenAI.

### 1. Configuração do Ambiente

Crie o arquivo `.env` na pasta `backend/docker/` e preencha as variáveis de ambiente.

#### 1.1 Ativação do Ambiente

source venv/Scripts/activate

**Caminho do Arquivo:** `backend/docker/.env`

```bash
# PostgreSQL
POSTGRES_DB=zapsign
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5433

# Django
DJANGO_SECRET_KEY=secret-key-alterar-na-producao
DJANGO_DEBUG=True

# ZapSign Token (Token de Sandbox da ZapSign)
ZAPSIGN_API_TOKEN=SEU_TOKEN_ZAPSIGN_AQUI

# API Keys para serviços de IA
GEMINI_API_KEY=SUA_CHAVE_GEMINI_AQUI
OPENAI_API_KEY=SUA_CHAVE_OPENAI_AQUI
```

### 2. Inicialização dos Serviços

Execute o comando na pasta `backend/docker/`:

```bash
docker-compose build
docker-compose up -d
```

Aguarde alguns minutos para que todos os serviços (`db`, `redis`, `backend`, `worker`, `n8n`) estejam em execução.

### 3. Inicialização de Dados

Execute os comandos na pasta `backend/`:

```bash
docker-compose exec backend python manage.py init_data
```

### 3.1 API Key

Execute os comandos na pasta `backend/`:

```bash
docker-compose exec backend python manage.py create_api_key n8n_automation_key
```


O comando `init_data` cria:
*   Empresas de teste (`Empresa A`, `Empresa B`, etc.).
*   Usuários de teste (`gerente_a@teste.com`, `assistente_a@teste.com`) com senha `123`.
*   Associa o `ZAPSIGN_API_TOKEN` à `Empresa A`.

O comando `create_api_key` gera a chave para o n8n (exemplo: `ed124ecbb42a401e5980341251c40de7a4a9649ab921579d0cdb5cb0c029be41`).

## Autenticação

### 1. Autenticação de Usuário (Frontend)

Use o endpoint de login para obter o token JWT:

*   **Endpoint:** `POST /auth/login/`
*   **Corpo:** `{"username": "gerente_a@teste.com", "password": "123"}`
*   **Uso:** O token de acesso retornado deve ser enviado no header `Authorization: Bearer <token>` para todas as rotas de API (exceto automações e webhook).

### 2. Autenticação de Automação (n8n)

Use a chave de API gerada no passo 3.

*   **Header:** `X-API-KEY: <chave_gerada>`
*   **Uso:** Necessário para acessar os endpoints em `/api/automations/`.

## Endpoints Principais (API RESTful)

| Módulo | Método | Endpoint | Descrição |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/auth/login/` | Obtém tokens JWT. |
| **Company** | `GET/PUT` | `/api/company/<id>/` | Gerencia a empresa do usuário logado (inclui `apiToken`). |
| **Document** | `GET/POST` | `/api/document/` | Cria um novo documento (dispara ZapSign e IA). |
| **Document** | `GET/PUT/DEL` | `/api/document/<id>/` | Detalhes, atualização e exclusão de documento. |
| **Document** | `GET` | `/api/document/<id>/pdf/` | Obtém o link de download do PDF assinado. |
| **Document** | `POST` | `/api/document/<id>/sync/` | Sincroniza manualmente o status com a ZapSign. |
| **Webhook** | `POST` | `/webhook/zapsign/` | Recebe atualizações de status da ZapSign. |

## Endpoints de Automação (n8n)

Estes endpoints exigem o header `X-API-KEY`.

| Módulo | Método | Endpoint | Descrição |
| :--- | :--- | :--- | :--- |
| **Automação** | `GET` | `/api/automations/documents/<id>/analysis/` | Obtém o resultado da análise de IA de um documento. |
| **Automação** | `POST` | `/api/automations/documents/<id>/reanalyze/` | Dispara uma nova análise de IA para um documento. |
| **Automação** | `POST` | `/api/automations/reports/` | Gera um relatório de documentos por período e empresa. |

## Lógica de IA Aplicada

A análise de IA é disparada de forma assíncrona (Celery) após a criação de um documento com `url_pdf`.

*   **Processo:** O backend baixa o PDF, extrai o texto com `PyPDF2` e envia o conteúdo para o modelo de IA (Gemini ou OpenAI) usando um prompt estruturado.
*   **Resultado:** O resultado (`summary`, `missing_topics`, `insights`) é salvo no modelo `DocumentAnalysis` e notificado ao frontend via WebSocket.

## WebSockets (Comunicação em Tempo Real)

O sistema utiliza WebSockets para notificar o frontend sobre eventos assíncronos, eliminando a necessidade de polling.

*   **Detalhe do Documento:** `ws://localhost:8000/ws/document/<document_id>/?token=<JWT>`
    *   Recebe eventos de `analysis_completed` e `analysis_status_update`.
*   **Lista de Documentos:** `ws://localhost:8000/ws/document/list/?token=<JWT>`
    *   Recebe eventos de `document_created`, `document_updated` e `document_deleted`.

## Execução de Testes

Execute os testes unitários e de integração na pasta `backend/`:

```bash
docker-compose exec backend pytest
```


