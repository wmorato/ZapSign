# ZapSign Frontend - Desafio Técnico

## Visão Geral

Este projeto implementa o frontend para o desafio técnico da ZapSign, utilizando **Angular** com componentes reativos e **TypeScript**. O objetivo é fornecer uma interface de usuário fluida (sem recarregamento de página) para a gestão de documentos, integrando-se com o backend Django via APIs RESTful e WebSockets.

## Stacks Utilizadas

*   **Framework:** Angular 17+
*   **Linguagem:** TypeScript
*   **Estilização:** SCSS
*   **Testes:** Vitest (substituindo Karma/Jasmine)
*   **Infraestrutura Local:** Docker, Docker Compose, Nginx (para servir e proxy)

## Configuração e Setup Local

### Pré-requisitos

1.  Docker e Docker Compose instalados.
2.  O backend deve estar em execução (consulte o README do Backend).

### 1. Inicialização dos Serviços

Execute o comando na pasta `backend/docker/` (o `docker-compose.yml` nesta pasta gerencia o frontend também):

```bash
docker-compose build
docker-compose up -d
```

Aguarde alguns minutos para que o contêiner `zapsign_frontend` inicie.

### 2. Acesso à Aplicação

Acesse a aplicação no seu navegador:

```
http://localhost:4200
```

## Autenticação e Acesso

### Credenciais de Teste

Utilize as credenciais criadas pelo script `init_data` do backend:

*   **Email:** `gerente_a@teste.com`
*   **Senha:** `123`

### Fluxo de Autenticação

1.  O usuário faz login na rota `/login`.
2.  O `AuthService` obtém o token JWT do backend.
3.  O `AuthInterceptor` anexa o token JWT (`Authorization: Bearer <token>`) a todas as requisições subsequentes para o backend.

## Funcionalidades Implementadas

### 1. Gestão de Documentos (CRUD)

*   **Lista de Documentos (`/documents`):** Exibe todos os documentos da empresa.
    *   **Atualização em Tempo Real:** Utiliza **WebSocket** para receber notificações de criação, atualização e exclusão de documentos sem recarregar a página.
*   **Criação/Edição de Documentos (`/documents/new` ou `/documents/:id/edit`):** Formulário unificado para criar ou editar documentos, incluindo a gestão de signatários aninhados.
*   **Detalhes do Documento (`/documents/:id`):** Exibe informações completas, incluindo a análise de IA.

### 2. Análise de IA e WebSockets

*   **Visualização da Análise:** O `DocumentDetailComponent` exibe o `ai_analysis` (resumo, tópicos faltantes, insights).
*   **Status em Tempo Real:** Utiliza **WebSocket** para receber o status da análise de IA (`pending`, `processing`, `completed`, `failed`) em tempo real, garantindo que o usuário não precise atualizar a página.
*   **Reanálise:** Botão para disparar a reanálise de IA via endpoint de automação do backend.

### 3. Automação e Relatórios

*   **Sincronização Manual:** Botão "Sincronizar" na lista de documentos para forçar a atualização do status com a ZapSign.
*   **Relatórios (`/reports`):** O `DocumentReportsComponent` permite:
    *   Filtrar documentos por período.
    *   Visualizar um resumo de métricas (Assinados, Pendentes, Alto Risco, IA Concluída).
    *   Exportar a lista detalhada para CSV.
*   **Gestão de Risco (`/documents/risk`):** Painel dedicado para visualizar documentos pendentes classificados por nível de risco (dias pendentes) e realizar ações em massa (simuladas).

### 4. Componentes Reativos e Boas Práticas

*   **Componentes Reativos:** Uso extensivo de `FormGroup` e `FormArray` para o formulário de documentos e signatários.
*   **Serviços Dedicados:** Separação da lógica de comunicação com a API em `ApiService`, `AuthService`, `CompanyService` e `DocumentService`.

## Execução de Testes (Vitest)

O projeto utiliza Vitest para testes unitários, focando no mocking manual de dependências para garantir a velocidade e o isolamento dos testes.

Execute os testes na pasta `frontend/`:

```bash
npm test

npm test nome_do_teste
```

**Observação:** O arquivo `vitest.config.ts` e o `KB/KB.md` contêm a configuração e as boas práticas para o ambiente de teste Angular/Vitest.