"""
Testes para validação dos schemas Pydantic
"""
import pytest
from pydantic import ValidationError
from app.schemas import WebhookInRequest, CallbackResponse, WebhookResponse


class TestWebhookInRequest:
    """Testes para schema WebhookInRequest"""
    
    def test_valid_request(self):
        """Testa criação de request válido"""
        data = {
            "numero_carterinha": "086955681",
            "plan_name": "amil",
            "numero": "5517992749450@s.whatsapp.net"
        }
        request = WebhookInRequest(**data)
        
        assert request.numero_carterinha == "086955681"
        assert request.plan_name == "amil"
        assert request.numero == "5517992749450@s.whatsapp.net"
    
    def test_missing_fields(self):
        """Testa erro quando campos obrigatórios estão ausentes"""
        data = {
            "numero_carterinha": "086955681"
            # Faltando plan_name e numero
        }
        
        with pytest.raises(ValidationError) as exc_info:
            WebhookInRequest(**data)
        
        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]
        
        assert "plan_name" in error_fields
        assert "numero" in error_fields


class TestCallbackResponse:
    """Testes para schema CallbackResponse"""
    
    def test_valid_response_elegivel(self):
        """Testa criação de response válido com status elegível"""
        data = {
            "numero": "5517992749450@s.whatsapp.net",
            "status": "elegivel"
        }
        response = CallbackResponse(**data)
        
        assert response.numero == "5517992749450@s.whatsapp.net"
        assert response.status == "elegivel"
    
    def test_valid_response_nao_elegivel(self):
        """Testa criação de response válido com status não elegível"""
        data = {
            "numero": "5517992749450@s.whatsapp.net",
            "status": "nao_elegivel"
        }
        response = CallbackResponse(**data)
        
        assert response.numero == "5517992749450@s.whatsapp.net"
        assert response.status == "nao_elegivel"
    
    def test_invalid_status(self):
        """Testa erro quando status é inválido"""
        data = {
            "numero": "5517992749450@s.whatsapp.net",
            "status": "invalido"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CallbackResponse(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "status" in str(errors[0]["loc"])


class TestWebhookResponse:
    """Testes para schema WebhookResponse"""
    
    def test_default_values(self):
        """Testa valores padrão do schema"""
        response = WebhookResponse()
        
        assert response.success is True
        assert response.message == "Processamento iniciado"
    
    def test_custom_values(self):
        """Testa valores customizados"""
        data = {
            "success": False,
            "message": "Erro no processamento"
        }
        response = WebhookResponse(**data)
        
        assert response.success is False
        assert response.message == "Erro no processamento" 