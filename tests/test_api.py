"""
Testes end-to-end para a API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app


client = TestClient(app)


class TestWebhookEndpoint:
    """Testes para o endpoint /webhook/in"""
    
    def test_webhook_valid_request(self):
        """Testa requisição válida para webhook"""
        payload = {
            "numero_carterinha": "086955681",
            "plan_name": "amil",
            "numero": "5517992749450@s.whatsapp.net"
        }
        
        response = client.post("/webhook/in", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Processamento iniciado" in data["message"]
    
    def test_webhook_missing_fields(self):
        """Testa erro quando campos obrigatórios estão ausentes"""
        payload = {
            "numero_carterinha": "086955681"
            # Faltando plan_name e numero
        }
        
        response = client.post("/webhook/in", json=payload)
        
        assert response.status_code == 422  # Validation Error
    
    def test_webhook_unsupported_plan(self):
        """Testa erro para plano não suportado"""
        payload = {
            "numero_carterinha": "086955681",
            "plan_name": "plano_inexistente",
            "numero": "5517992749450@s.whatsapp.net"
        }
        
        response = client.post("/webhook/in", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "Plano não suportado" in data["detail"]["error"]
    
    def test_webhook_empty_payload(self):
        """Testa erro com payload vazio"""
        response = client.post("/webhook/in", json={})
        
        assert response.status_code == 422


class TestHealthEndpoint:
    """Testes para o endpoint /health"""
    
    def test_health_check(self):
        """Testa endpoint de health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "robo_veia"
        assert "supported_plans" in data
        assert isinstance(data["supported_plans"], list)


class TestPlansEndpoint:
    """Testes para o endpoint /plans"""
    
    def test_list_plans(self):
        """Testa listagem de planos suportados"""
        response = client.get("/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert "supported_plans" in data
        assert "total" in data
        assert isinstance(data["supported_plans"], list)
        assert data["total"] == len(data["supported_plans"])
        assert "amil" in data["supported_plans"]


class TestRootEndpoint:
    """Testes para o endpoint raiz"""
    
    def test_root_endpoint(self):
        """Testa endpoint raiz"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "robo_veia"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
        assert "endpoints" in data
        
        endpoints = data["endpoints"]
        assert endpoints["webhook"] == "/webhook/in"
        assert endpoints["health"] == "/health"
        assert endpoints["plans"] == "/plans"
        assert endpoints["docs"] == "/docs"


class TestBackgroundProcessing:
    """Testes para processamento em background"""
    
    @patch('app.router.handler_registry.process_eligibility')
    @patch('app.router.send_callback')
    def test_background_processing_success(self, mock_send_callback, mock_process):
        """Testa processamento em background com sucesso"""
        # Configurar mocks
        mock_process.return_value = "elegivel"
        mock_send_callback.return_value = True
        
        payload = {
            "numero_carterinha": "086955681",
            "plan_name": "amil",
            "numero": "5517992749450@s.whatsapp.net"
        }
        
        response = client.post("/webhook/in", json=payload)
        
        assert response.status_code == 200
        # O processamento acontece em background, então só validamos a resposta imediata
    
    def test_invalid_json(self):
        """Testa erro com JSON inválido"""
        response = client.post(
            "/webhook/in",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422 