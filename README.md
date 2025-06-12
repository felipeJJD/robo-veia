# Robo Veia - Micro-serviço de Elegibilidade

Micro-serviço para verificação de elegibilidade de carteirinhas de planos de saúde.

## 🚀 Características

- **FastAPI** assíncrono para alta performance
- **Playwright** para automação de navegador
- **Logs estruturados** em JSON
- **Retry automático** com backoff exponencial
- **Docker** para containerização
- **Railway** ready para deploy
- **Testes** com cobertura ≥ 80%

## 📋 Pré-requisitos

- Python ≥ 3.10
- Docker (opcional, para containerização)
- Railway CLI (opcional, para deploy)

## 🛠️ Instalação

### Ambiente Local

```bash
# Clonar repositório
git clone <url-do-repo>
cd robo_veia

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Instalar Chromium para Playwright
playwright install chromium
```

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
# Credenciais do Amil
AMIL_LOGIN=10354263
AMIL_PASSWORD=imc@2025

# Configurações da aplicação
LOG_LEVEL=INFO
WEBHOOK_CALLBACK_URL=https://web-hook.imca.app.br/webhook/a4c4db28-1c03-4233-959d-6f89630daae4
WEBHOOK_TIMEOUT=10
WEBHOOK_MAX_RETRIES=3
```

## 🏃‍♂️ Executando

### Desenvolvimento

```bash
# Executar servidor de desenvolvimento
uvicorn app.main:app --reload

# Ou usando Python
python app/main.py
```

### Produção

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build da imagem
docker build -t robo-veia .

# Executar container
docker run -p 8000:8000 --env-file .env robo-veia
```

## 📡 API Endpoints

### POST /webhook/in

Endpoint principal para verificação de elegibilidade.

**Request:**
```json
{
  "numero_carterinha": "086955681",
  "plan_name": "amil",
  "numero": "5517992749450@s.whatsapp.net"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Processamento iniciado"
}
```

### GET /health

Health check da aplicação.

**Response:**
```json
{
  "status": "healthy",
  "service": "robo_veia",
  "supported_plans": ["amil"]
}
```

### GET /plans

Lista planos suportados.

**Response:**
```json
{
  "supported_plans": ["amil"],
  "total": 1
}
```

### GET /

Informações gerais da API.

### GET /docs

Documentação interativa (Swagger UI).

## 🔄 Fluxo de Processamento

1. **Recebimento**: Webhook recebe requisição POST
2. **Validação**: Schema Pydantic valida dados
3. **Dispatch**: Sistema identifica handler do plano
4. **Processamento**: Handler executa automação Playwright
5. **Callback**: Resultado é enviado para webhook externo
6. **Logging**: Tudo é registrado em logs estruturados

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Testes específicos
pytest tests/test_api.py
pytest tests/test_schemas.py
pytest tests/test_dispatch.py
```

## 🏗️ Arquitetura

```
app/
├── main.py          # FastAPI app principal
├── router.py        # Endpoints e lógica de roteamento
├── dispatch.py      # Registry de handlers
├── schemas.py       # Modelos Pydantic
├── handlers/        # Handlers específicos por plano
│   └── amil.py     # Handler do Amil
└── utils/          # Utilitários
    ├── logger.py   # Logger estruturado
    └── http.py     # Cliente HTTP para callbacks
```

## 🔧 Extensibilidade

Para adicionar suporte a um novo plano:

1. **Criar handler**: `app/handlers/novo_plano.py`
2. **Implementar interface**: Função async que retorna `"elegivel"` ou `"nao_elegivel"`
3. **Registrar handler**: No `dispatch.py`
4. **Adicionar testes**: Em `tests/`

Exemplo:
     
```python
# app/handlers/unimed.py
print(">>> Entrou no handler Amil!")
async def check_eligibility(numero_carteirinha: str) -> Literal["elegivel", "nao_elegivel"]:
    # Implementar lógica específica
    return "elegivel"

# app/dispatch.py
from app.handlers.unimed import check_eligibility as unimed_handler

class HandlerRegistry:
    def _register_handlers(self):
        self.register_handler("amil", amil_handler.check_eligibility)
        self.register_handler("unimed", unimed_handler)  # Novo handler
```

## 🚀 Deploy no Railway

1. **Preparar repositório**:
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Deploy**:
```bash
railway login
railway link
railway up
```

3. **Configurar variáveis de ambiente no Railway**:
- `AMIL_LOGIN`
- `AMIL_PASSWORD`
- `AMIL_TIMEOUT` (opcional, padrão: 90000ms)
- Outras conforme necessário

## 📊 Observabilidade

### Logs Estruturados

Todos os logs são estruturados em JSON:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Verificação concluída",
  "module": "amil",
  "function": "check_eligibility",
  "numero_carteirinha": "086955681",
  "status": "elegivel"
}
```

### Monitoramento

- **Health Check**: `/health`
- **Métricas**: Logs estruturados permitem agregação
- **Alertas**: Configurar com base nos logs de erro

## 🔒 Segurança

- **Variáveis de ambiente** para credenciais
- **Timeouts** para evitar travamentos
- **Rate limiting** (implementar se necessário)
- **CORS** configurado
- **Validation** com Pydantic
- **Error handling** robusto

## 🐛 Troubleshooting

### Problemas Comuns

1. **Playwright não encontra Chromium**:
```bash
playwright install chromium
```

2. **Variáveis de ambiente não carregadas**:
- Verificar arquivo `.env`
- Verificar configuração no Railway

3. **Handler falha**:
- Verificar logs estruturados
- Site do plano pode ter mudado
- Credenciais podem estar inválidas

### Debug

```bash
# Logs detalhados
LOG_LEVEL=DEBUG uvicorn app.main:app

# Playwright com modo visual (desenvolvimento)
# Modificar handler para headless=False
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit as mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Verifique os logs estruturados
- Consulte a documentação em `/docs`

---

**Versão**: 1.0.0  
**Status**: Produção  
**Maintainer**: Equipe de Desenvolvimento 