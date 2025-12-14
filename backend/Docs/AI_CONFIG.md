# Configuração das APIs de IA

## 📋 Resumo

O módulo de IA foi **completamente implementado** e está pronto para uso! As integrações com Gemini e OpenAI estão funcionais.

## ✅ O que foi implementado

### 1. **Gemini AI (Google)**
- ✅ Integração completa com `google-generativeai`
- ✅ Modelo: `gemini-pro`
- ✅ Carregamento do template de prompt
- ✅ Parsing de JSON com fallback
- ✅ Tratamento de erros robusto

### 2. **OpenAI (GPT-4)**
- ✅ Integração completa com `openai` SDK
- ✅ Modelo: `gpt-4-turbo-preview` (pode usar `gpt-3.5-turbo` para economia)
- ✅ JSON mode ativado
- ✅ Temperatura 0.3 (mais determinístico)
- ✅ Tratamento de erros robusto

### 3. **Infraestrutura**
- ✅ Task Celery assíncrona (`analyze_document_content_task`)
- ✅ Modelo `DocumentAnalysis` para armazenar resultados
- ✅ Template de prompt (`prompt_template.txt`)
- ✅ Integração nas views de Document

## 🔧 Configuração

### Passo 1: Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

Isso instalará:
- `google-generativeai==0.3.2`
- `openai==1.12.0`

### Passo 2: Configurar API Keys

Adicione as chaves no arquivo `.env`:

```bash
# backend/.env
GEMINI_API_KEY=sua-chave-gemini-aqui
OPENAI_API_KEY=sua-chave-openai-aqui
```

#### Como obter as chaves:

**Gemini (Google):**
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma nova API key
3. Copie e cole no `.env`

**OpenAI:**
1. Acesse: https://platform.openai.com/api-keys
2. Crie uma nova secret key
3. Copie e cole no `.env`

### Passo 3: Configurar Celery (para processamento assíncrono)

O Celery já está configurado no `docker-compose.yml` com Redis.

Para rodar localmente sem Docker:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A config worker -l info

# Terminal 3: Django
python manage.py runserver
```

## 🚀 Como usar

### Automático (ao criar documento)

Quando você cria um documento via API, a análise de IA é disparada automaticamente:

```python
# POST /api/document/
{
    "name": "Contrato de Serviços",
    "company": 1,
    "url_pdf": "https://example.com/contrato.pdf",
    "signers": [...]
}
```

A task Celery será executada em background e salvará os resultados em `DocumentAnalysis`.

### Manual (via código)

```python
from app.ai.ai_service import AIProvider
from app.ai.tasks import analyze_document_content_task

# Opção 1: Síncrono (para testes)
provider = AIProvider(default_model="gemini")
service = provider.get_service("gemini")  # ou "openai"
result = service.analyze_document("Texto do documento aqui...")

# Opção 2: Assíncrono (produção)
analyze_document_content_task.delay(
    document_id=123,
    document_content="Texto do documento...",
    model_name="gemini"  # ou "openai"
)
```

## 📊 Estrutura da Resposta

```json
{
    "summary": "Resumo conciso do documento...",
    "missing_topics": [
        "Cláusula de rescisão",
        "Garantias",
        "Prazos de entrega"
    ],
    "insights": [
        "Documento focado em aspectos legais",
        "Necessidade de clareza em obrigações",
        "Potencial para otimização de linguagem"
    ]
}
```

## 🔍 Verificar resultados

### Via API

```bash
GET /api/document/{id}/
```

Resposta incluirá:
```json
{
    "id": 1,
    "name": "Contrato",
    "ai_analysis": {
        "status": "completed",  // pending, processing, completed, failed
        "summary": "...",
        "missing_topics": [...],
        "insights": [...],
        "model_used": "gemini",
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

### Via Django Admin

1. Acesse: http://localhost:8000/admin/
2. Navegue para: AI → Document Analysis
3. Veja todos os resultados de análise

## ⚙️ Configurações Avançadas

### Trocar modelo padrão

Em `document/views.py` linha 131:

```python
analyze_document_content_task.delay(
    document_id=document.id,
    document_content=document_content,
    model_name="openai",  # Trocar para "openai" se preferir
)
```

### Ajustar temperatura (OpenAI)

Em `ai/ai_service.py` linha 165:

```python
temperature=0.3,  # 0.0 = mais determinístico, 1.0 = mais criativo
```

### Usar GPT-3.5 (mais barato)

Em `ai/ai_service.py` linha 157:

```python
model="gpt-3.5-turbo",  # Trocar de gpt-4-turbo-preview
```

## 🧪 Testar

### Teste unitário

```bash
cd backend
pytest app/tests/test_ai.py -v
```

### Teste manual

```python
# python manage.py shell
from app.ai.ai_service import AIProvider

provider = AIProvider()
gemini = provider.get_service("gemini")
result = gemini.analyze_document("Este é um contrato de prestação de serviços...")
print(result)
```

## 📝 Logs

Os logs estão configurados para mostrar:
- ✅ Inicialização dos services
- ✅ Início e fim de análises
- ❌ Erros de API
- ❌ Erros de parsing JSON

Verifique em:
```bash
# Console do Django/Celery
# Ou configure logging em settings.py
```

## 💰 Custos estimados

### Gemini
- **Gratuito** até 60 requisições/minuto
- Modelo: gemini-pro

### OpenAI
- **GPT-4 Turbo**: ~$0.01 por 1K tokens (~750 palavras)
- **GPT-3.5 Turbo**: ~$0.001 por 1K tokens (10x mais barato)

Para um documento de 2000 palavras:
- Gemini: **Grátis**
- GPT-4: ~$0.03
- GPT-3.5: ~$0.003

## ✅ Checklist de Configuração

- [ ] Instalar dependências (`pip install -r requirements.txt`)
- [ ] Obter API key do Gemini
- [ ] Obter API key do OpenAI (opcional)
- [ ] Adicionar keys no `.env`
- [ ] Rodar Redis (ou usar Docker)
- [ ] Rodar Celery worker
- [ ] Testar criação de documento
- [ ] Verificar análise no admin ou via API

## 🚨 Troubleshooting

### Erro: "google-generativeai não instalado"
```bash
pip install google-generativeai==0.3.2
```

### Erro: "openai não instalado"
```bash
pip install openai==1.12.0
```

### Erro: "API Key não configurada"
Verifique se o `.env` está correto e se as variáveis estão sendo carregadas.

### Task Celery não executa
1. Verifique se Redis está rodando: `redis-cli ping`
2. Verifique se Celery worker está ativo
3. Veja logs do Celery

### Análise fica em "pending"
- Celery worker pode não estar rodando
- Verifique logs do Celery para erros

## 📚 Próximos passos (opcional)

- [ ] Adicionar mais modelos (Claude, LLaMA, etc.)
- [ ] Implementar cache de análises
- [ ] Dashboard de métricas de IA
- [ ] Comparação entre modelos
- [ ] Fine-tuning de prompts

---

**Status**: ✅ **TOTALMENTE FUNCIONAL**

As integrações de IA estão prontas para uso em produção!
