"""
Cliente HTTP para envio de callbacks com retry e timeout
"""
import asyncio
import os
from typing import Dict, Any
import httpx
from app.utils.logger import logger, log_with_context
from app.schemas import CallbackResponse


class HTTPCallbackClient:
    """Cliente HTTP para envio de callbacks"""
    
    def __init__(self):
        self.callback_url = os.getenv(
            "WEBHOOK_CALLBACK_URL", 
            "https://web-hook.imca.app.br/webhook/a4c4db28-1c03-4233-959d-6f89630daae4"
        )
        self.timeout = int(os.getenv("WEBHOOK_TIMEOUT", "10"))
        self.max_retries = int(os.getenv("WEBHOOK_MAX_RETRIES", "3"))
    
    async def send_callback(self, payload: CallbackResponse) -> bool:
        """
        Envia callback com retry exponencial
        
        Args:
            payload: Dados para envio
            
        Returns:
            True se sucesso, False caso contrário
        """
        log_with_context(
            logger, 
            "INFO", 
            "Iniciando envio de callback",
            callback_url=self.callback_url,
            payload=payload.dict()
        )
        
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.callback_url,
                        json=payload.dict(),
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        log_with_context(
                            logger,
                            "INFO",
                            "Callback enviado com sucesso",
                            attempt=attempt,
                            status_code=response.status_code,
                            response_text=response.text[:500]  # Limitar tamanho do log
                        )
                        return True
                    else:
                        log_with_context(
                            logger,
                            "WARNING",
                            f"Callback falhou com status {response.status_code}",
                            attempt=attempt,
                            status_code=response.status_code,
                            response_text=response.text[:500]
                        )
                        
            except Exception as e:
                log_with_context(
                    logger,
                    "ERROR",
                    f"Erro no envio do callback: {str(e)}",
                    attempt=attempt,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            
            # Retry com backoff exponencial (exceto na última tentativa)
            if attempt < self.max_retries:
                wait_time = 2 ** attempt  # 2, 4, 8 segundos
                log_with_context(
                    logger,
                    "INFO",
                    f"Aguardando {wait_time}s antes da próxima tentativa",
                    attempt=attempt,
                    wait_time=wait_time
                )
                await asyncio.sleep(wait_time)
        
        log_with_context(
            logger,
            "ERROR",
            "Falha definitiva no envio do callback após todas as tentativas",
            max_retries=self.max_retries
        )
        return False


# Instância global do cliente
http_client = HTTPCallbackClient()


async def send_callback(numero: str, status: str) -> bool:
    """
    Função helper para envio de callback
    
    Args:
        numero: Número para callback
        status: Status da elegibilidade
        
    Returns:
        True se sucesso, False caso contrário
    """
    payload = CallbackResponse(numero=numero, status=status)
    return await http_client.send_callback(payload) 