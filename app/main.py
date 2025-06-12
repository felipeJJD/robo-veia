"""
Aplicação principal FastAPI para o micro-serviço de elegibilidade
"""
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import router
from app.utils.logger import logger, log_with_context


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação
    """
    # Startup
    log_with_context(
        logger,
        "INFO",
        "Iniciando micro-serviço de elegibilidade",
        service="robo_veia",
        version="1.0.0"
    )
    
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
    
    # Configuração para Railway
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    log_with_context(
        logger,
        "INFO",
        f"Iniciando servidor na porta {port}",
        host=host,
        port=port,
        environment="railway" if os.getenv("RAILWAY_ENVIRONMENT") else "local"
    )
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # Desabilitado em produção
        access_log=True
    ) 