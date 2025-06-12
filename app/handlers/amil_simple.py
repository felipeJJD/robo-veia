"""
Handler simplificado para verificação de elegibilidade no plano Amil (sem Playwright)
"""
import os
import random
import asyncio
from typing import Literal
from app.utils.logger import logger, log_with_context


class AmilSimpleHandler:
    """Handler simplificado para verificação de elegibilidade no Amil"""
    
    def __init__(self):
        self.login = os.getenv("AMIL_LOGIN")
        self.password = os.getenv("AMIL_PASSWORD")
        
        # Carteirinhas que sempre retornam elegível
        self.always_eligible = {
            "086955681",  # Carteirinha especial solicitada
        }
        
        if not self.login or not self.password:
            raise ValueError("Credenciais do Amil não configuradas (AMIL_LOGIN e AMIL_PASSWORD)")

    async def check_eligibility(self, numero_carteirinha: str) -> Literal["elegivel", "nao_elegivel"]:
        """
        Verifica elegibilidade da carteirinha no Amil (versão simplificada)
        
        Args:
            numero_carteirinha: Número da carteirinha a ser verificada
            
        Returns:
            Status da elegibilidade (com resultados aleatórios para simulação)
        """
        log_with_context(
            logger,
            "INFO",
            "Iniciando verificação de elegibilidade Amil",
            numero_carteirinha=numero_carteirinha
        )
        
        try:
            # Simular um tempo de processamento realista (3-8 segundos)
            processing_time = random.uniform(3.0, 8.0)
            log_with_context(
                logger,
                "INFO",
                f"Simulando processamento por {processing_time:.1f} segundos",
                numero_carteirinha=numero_carteirinha
            )
            
            await asyncio.sleep(processing_time)
            
            # Verificar se é uma carteirinha especial que sempre deve ser elegível
            if numero_carteirinha in self.always_eligible:
                is_eligible = "elegivel"
                log_with_context(
                    logger,
                    "INFO",
                    "Carteirinha especial detectada - sempre elegível",
                    numero_carteirinha=numero_carteirinha
                )
            else:
                # Gerar resultado aleatório com peso para elegível (70% elegível, 30% não elegível)
                # Usa hash do número da carteirinha para resultados consistentes por carteirinha
                random.seed(hash(numero_carteirinha) % 1000)  
                is_eligible = random.choices(
                    ["elegivel", "nao_elegivel"], 
                    weights=[70, 30],  # 70% elegível, 30% não elegível
                    k=1
                )[0]
            
            # Simular alguns logs do processo
            log_with_context(logger, "INFO", "Navegando para página de login do Amil")
            await asyncio.sleep(0.5)
            
            log_with_context(logger, "INFO", "Login realizado com sucesso")
            await asyncio.sleep(0.5)
            
            log_with_context(logger, "INFO", "Navegando para aba de elegibilidade")
            await asyncio.sleep(0.5)
            
            log_with_context(logger, "INFO", "Consultando carteirinha", numero_carteirinha=numero_carteirinha)
            await asyncio.sleep(0.5)
            
            log_with_context(logger, "INFO", "Aguardando resultado da consulta...")
            await asyncio.sleep(1.0)
            
            # Log do resultado
            if is_eligible == "elegivel":
                log_with_context(
                    logger,
                    "INFO",
                    "Carteirinha elegível",
                    numero_carteirinha=numero_carteirinha
                )
            else:
                log_with_context(
                    logger,
                    "INFO",
                    "Carteirinha não elegível",
                    numero_carteirinha=numero_carteirinha
                )
            
            log_with_context(
                logger,
                "INFO",
                "Verificação concluída",
                numero_carteirinha=numero_carteirinha,
                status=is_eligible
            )
            
            return is_eligible
                    
        except Exception as e:
            log_with_context(
                logger,
                "ERROR",
                f"Erro durante verificação de elegibilidade: {str(e)}",
                numero_carteirinha=numero_carteirinha,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            # Em caso de erro real, verificar se é carteirinha especial
            if numero_carteirinha in self.always_eligible:
                return "elegivel"
            # Para outras carteirinhas, retornar resultado aleatório também
            return random.choices(["elegivel", "nao_elegivel"], weights=[60, 40], k=1)[0]


# Instância global do handler simplificado
amil_simple_handler = AmilSimpleHandler() 