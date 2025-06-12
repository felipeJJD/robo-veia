"""
Configuração de logger estruturado para o micro-serviço
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar informações extras se disponíveis
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        # Adicionar traceback se for um erro
        if record.exc_info:
            log_data["traceback"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name: str = "robo_veia", level: str = "INFO") -> logging.Logger:
    """
    Configura e retorna um logger estruturado
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar configurar múltiplas vezes
    if logger.handlers:
        return logger
        
    logger.setLevel(getattr(logging, level.upper()))
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs: Any) -> None:
    """
    Faz log com contexto adicional
    
    Args:
        logger: Logger a ser usado
        level: Nível do log
        message: Mensagem principal
        **kwargs: Dados adicionais para incluir no log
    """
    log_level = getattr(logging, level.upper())
    extra_data = kwargs if kwargs else {}
    
    logger.log(log_level, message, extra={"extra_data": extra_data})


# Instância global do logger
logger = setup_logger() 