"""
Schemas Pydantic para validação de dados de entrada e saída
"""
from pydantic import BaseModel, Field
from typing import Literal


class WebhookInRequest(BaseModel):
    """Schema para requisição de entrada do webhook"""
    numero_carterinha: str = Field(..., description="Número da carteirinha do plano de saúde")
    plan_name: str = Field(..., description="Nome do plano de saúde")
    numero: str = Field(..., description="Número para callback (formato WhatsApp)")

    class Config:
        json_schema_extra = {
            "example": {
                "numero_carterinha": "086955681",
                "plan_name": "amil",
                "numero": "5517992749450@s.whatsapp.net"
            }
        }


class CallbackResponse(BaseModel):
    """Schema para resposta do callback"""
    numero: str = Field(..., description="Número para callback")
    status: Literal["elegivel", "nao_elegivel"] = Field(..., description="Status da elegibilidade")

    class Config:
        json_schema_extra = {
            "example": {
                "numero": "5517992749450@s.whatsapp.net",
                "status": "elegivel"
            }
        }


class WebhookResponse(BaseModel):
    """Schema para resposta do webhook"""
    success: bool = Field(default=True, description="Indica se a requisição foi processada com sucesso")
    message: str = Field(default="Processamento iniciado", description="Mensagem de status")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Processamento iniciado"
            }
        } 