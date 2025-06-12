"""
Router principal para endpoints do micro-serviço
"""
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas import WebhookInRequest, WebhookResponse
from app.dispatch import handler_registry
from app.utils.http import send_callback
from app.utils.logger import logger, log_with_context
import os
import sys


router = APIRouter()


@router.post("/webhook/in", response_model=WebhookResponse)
async def webhook_in(
    request: WebhookInRequest,
    background_tasks: BackgroundTasks
) -> WebhookResponse:
    """
    Endpoint principal para recebimento de webhooks de verificação de elegibilidade
    
    Args:
        request: Dados da requisição
        background_tasks: Tarefas em background do FastAPI
        
    Returns:
        Resposta imediata confirmando recebimento
    """
    log_with_context(
        logger,
        "INFO",
        "Webhook recebido",
        numero_carteirinha=request.numero_carterinha,
        plan_name=request.plan_name,
        numero=request.numero
    )
    
    # Não há mais validação de planos - aceita qualquer plano via handler genérico
    log_with_context(
        logger,
        "INFO",
        f"Processando plano: {request.plan_name}",
        plan_name=request.plan_name,
        supports_any_plan=True
    )

    # Adicionar processamento às tarefas em background
    background_tasks.add_task(
        process_eligibility_background,
        request.numero_carterinha,
        request.plan_name,
        request.numero
    )
    
    log_with_context(
        logger,
        "INFO",
        "Processamento iniciado em background",
        numero_carteirinha=request.numero_carterinha,
        plan_name=request.plan_name
    )
    
    return WebhookResponse(
        success=True,
        message="Processamento iniciado"
    )


async def process_eligibility_background(
    numero_carteirinha: str,
    plan_name: str,
    numero: str
) -> None:
    """
    Processa verificação de elegibilidade em background
    
    Args:
        numero_carteirinha: Número da carteirinha
        plan_name: Nome do plano
        numero: Número para callback
    """
    try:
        log_with_context(
            logger,
            "INFO",
            "Iniciando processamento em background",
            numero_carteirinha=numero_carteirinha,
            plan_name=plan_name,
            numero=numero
        )
        
        # Verificar elegibilidade
        status = await handler_registry.process_eligibility(plan_name, numero_carteirinha)
        
        # Enviar callback
        callback_success = await send_callback(numero, status)
        
        if callback_success:
            log_with_context(
                logger,
                "INFO",
                "Processamento completo com sucesso",
                numero_carteirinha=numero_carteirinha,
                plan_name=plan_name,
                numero=numero,
                status=status
            )
        else:
            log_with_context(
                logger,
                "WARNING",
                "Processamento concluído mas callback falhou",
                numero_carteirinha=numero_carteirinha,
                plan_name=plan_name,
                numero=numero,
                status=status
            )
            
    except Exception as e:
        log_with_context(
            logger,
            "ERROR",
            f"Erro no processamento em background: {str(e)}",
            numero_carteirinha=numero_carteirinha,
            plan_name=plan_name,
            numero=numero,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        # Tentar enviar callback com status de erro
        try:
            await send_callback(numero, "nao_elegivel")
        except Exception as callback_error:
            log_with_context(
                logger,
                "ERROR",
                f"Falha também no envio do callback de erro: {str(callback_error)}",
                numero_carteirinha=numero_carteirinha,
                numero=numero,
                callback_error=str(callback_error)
            )


@router.get("/debug")
async def debug_info() -> dict:
    """
    Endpoint de debug para verificar configurações (apenas para desenvolvimento)
    
    Returns:
        Informações de debug do ambiente
    """
    return {
        "environment": {
            "railway_env": os.getenv("RAILWAY_ENVIRONMENT"),
            "railway_project": os.getenv("RAILWAY_PROJECT_ID"),
            "port": os.getenv("PORT"),
            "python_version": sys.version,
        },
        "handlers": {
            "registered_plans": handler_registry.list_supported_plans(),
        },
        "status": "debug_active"
    }


@router.get("/health")
async def health_check() -> dict:
    """
    Endpoint de health check
    
    Returns:
        Status da aplicação
    """
    supported_plans = handler_registry.list_supported_plans()
    
    return {
        "status": "healthy",
        "service": "robo_veia",
        "supported_plans": supported_plans
    }


@router.get("/plans")
async def list_supported_plans() -> dict:
    """
    Lista os planos suportados
    
    Returns:
        Lista de planos suportados
    """
    supported_plans = handler_registry.list_supported_plans()
    
    log_with_context(
        logger,
        "INFO",
        "Consulta de planos suportados",
        supported_plans=supported_plans
    )
    
    return {
        "supported_plans": supported_plans,
        "total": len(supported_plans)
    } 