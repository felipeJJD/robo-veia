"""
Aplicação FastAPI principal do micro-serviço de elegibilidade
"""
from dotenv import load_dotenv
load_dotenv()
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.router import router
from app.utils.logger import logger, log_with_context


# Carregar variáveis de ambiente
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    # Startup
    log_with_context(
        logger,
        "INFO",
        "Iniciando micro-serviço de elegibilidade",
        service="robo_veia",
        version="1.0.0"
    )
    
    # Verificar variáveis de ambiente essenciais
    required_env_vars = ["AMIL_LOGIN", "AMIL_PASSWORD"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        log_with_context(
            logger,
            "ERROR",
            "Variáveis de ambiente faltando",
            missing_vars=missing_vars
        )
        raise Exception(f"Variáveis de ambiente faltando: {missing_vars}")
    
    log_with_context(
        logger,
        "INFO",
        "Micro-serviço iniciado com sucesso",
        status="ready"
    )
    
    yield
    
    # Shutdown
    log_with_context(
        logger,
        "INFO",
        "Encerrando micro-serviço",
        status="shutdown"
    )


# Criar aplicação FastAPI
app = FastAPI(
    title="Robo Veia - Elegibilidade de Carteirinhas",
    description="Micro-serviço para verificação de elegibilidade de carteirinhas de planos de saúde",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router, prefix="", tags=["webhook"])


@app.get("/")
async def root():
    """
    Endpoint raiz
    """
    return {
        "service": "robo_veia",
        "version": "1.0.0",
        "status": "operational",
        "description": "Micro-serviço de elegibilidade de carteirinhas de planos de saúde",
        "endpoints": {
            "webhook": "/webhook/in",
            "health": "/health",
            "plans": "/plans",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configuração para desenvolvimento
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Usar nosso logger customizado
    ) 