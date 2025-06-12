"""
Sistema de dispatch para handlers de diferentes planos de saúde
"""
import os
from typing import Dict, Callable, Awaitable, Literal
from app.utils.logger import logger, log_with_context

# Importar handlers baseado no ambiente
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
    # Ambiente Railway - usar versão simplificada
    from app.handlers.amil_simple import amil_simple_handler as amil_handler
else:
    # Ambiente local - usar versão completa com Playwright
    try:
        from app.handlers.amil import amil_handler
    except ImportError:
        # Fallback para versão simplificada se Playwright não estiver disponível
        from app.handlers.amil_simple import amil_simple_handler as amil_handler

from app.handlers.generic import generic_handler


class HandlerRegistry:
    """Registry para handlers de diferentes planos"""
    
    def __init__(self):
        self._handlers: Dict[str, Callable[[str], Awaitable[Literal["elegivel", "nao_elegivel"]]]] = {}
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Registra todos os handlers disponíveis"""
        # Registrar handler do Amil (específico ou simplificado)
        self.register_handler("amil", amil_handler.check_eligibility)
        
        log_with_context(
            logger,
            "INFO",
            "Handlers registrados",
            registered_plans=list(self._handlers.keys()),
            generic_fallback=True,
            environment="railway" if os.getenv("RAILWAY_ENVIRONMENT") else "local"
        )
    
    def register_handler(
        self, 
        plan_name: str, 
        handler: Callable[[str], Awaitable[Literal["elegivel", "nao_elegivel"]]]
    ) -> None:
        """
        Registra um handler para um plano específico
        
        Args:
            plan_name: Nome do plano (ex: "amil", "unimed")
            handler: Função async que verifica elegibilidade
        """
        self._handlers[plan_name.lower()] = handler
        log_with_context(
            logger,
            "INFO",
            f"Handler registrado para plano: {plan_name}",
            plan_name=plan_name
        )
    
    def get_handler(self, plan_name: str) -> Callable[[str], Awaitable[Literal["elegivel", "nao_elegivel"]]]:
        """
        Retorna o handler para um plano específico
        
        Args:
            plan_name: Nome do plano
            
        Returns:
            Handler function (específico ou genérico)
        """
        plan_key = plan_name.lower()
        
        # Se existe handler específico, usar ele
        if plan_key in self._handlers:
            log_with_context(
                logger,
                "INFO",
                f"Usando handler específico para: {plan_name}",
                plan_name=plan_name,
                handler_type="específico"
            )
            return self._handlers[plan_key]
        
        # Caso contrário, usar handler genérico
        log_with_context(
            logger,
            "INFO",
            f"Usando handler genérico para: {plan_name}",
            plan_name=plan_name,
            handler_type="genérico"
        )
        
        # Retornar uma função wrapper que passa o plan_name para o handler genérico
        async def generic_wrapper(numero_carteirinha: str) -> Literal["elegivel", "nao_elegivel"]:
            return await generic_handler.check_eligibility(numero_carteirinha, plan_name)
        
        return generic_wrapper
    
    def list_supported_plans(self) -> list[str]:
        """
        Lista todos os planos suportados
        
        Returns:
            Lista de nomes dos planos suportados (sempre inclui "qualquer plano")
        """
        specific_plans = list(self._handlers.keys())
        return specific_plans + ["qualquer_plano_via_handler_generico"]
    
    async def process_eligibility(self, plan_name: str, numero_carteirinha: str) -> Literal["elegivel", "nao_elegivel"]:
        """
        Processa verificação de elegibilidade para um plano específico
        
        Args:
            plan_name: Nome do plano
            numero_carteirinha: Número da carteirinha
            
        Returns:
            Status da elegibilidade
        """
        log_with_context(
            logger,
            "INFO",
            "Iniciando processamento de elegibilidade",
            plan_name=plan_name,
            numero_carteirinha=numero_carteirinha
        )
        
        try:
            handler = self.get_handler(plan_name)
            result = await handler(numero_carteirinha)
            
            log_with_context(
                logger,
                "INFO",
                "Processamento de elegibilidade concluído",
                plan_name=plan_name,
                numero_carteirinha=numero_carteirinha,
                result=result
            )
            
            return result
            
        except Exception as e:
            log_with_context(
                logger,
                "ERROR",
                f"Erro no processamento de elegibilidade: {str(e)}",
                plan_name=plan_name,
                numero_carteirinha=numero_carteirinha,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            # Retornar não elegível por segurança
            return "nao_elegivel"


# Instância global do registry
handler_registry = HandlerRegistry() 