"""
Testes para o sistema de dispatch
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.dispatch import HandlerRegistry


class TestHandlerRegistry:
    """Testes para HandlerRegistry"""
    
    @pytest.fixture
    def registry(self):
        """Fixture para criar um registry fresh"""
        with patch('app.dispatch.amil_handler'):
            return HandlerRegistry()
    
    def test_list_supported_plans(self, registry):
        """Testa listagem de planos suportados"""
        plans = registry.list_supported_plans()
        assert isinstance(plans, list)
        assert "amil" in plans
    
    def test_get_handler_existing_plan(self, registry):
        """Testa obtenção de handler para plano existente"""
        handler = registry.get_handler("amil")
        assert callable(handler)
        
        # Testa case insensitive
        handler_upper = registry.get_handler("AMIL")
        assert callable(handler_upper)
    
    def test_get_handler_nonexistent_plan(self, registry):
        """Testa erro ao obter handler para plano inexistente"""
        with pytest.raises(ValueError) as exc_info:
            registry.get_handler("plano_inexistente")
        
        assert "não suportado" in str(exc_info.value)
        assert "plano_inexistente" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_process_eligibility_success(self, registry):
        """Testa processamento de elegibilidade com sucesso"""
        # Mock do handler
        mock_handler = AsyncMock(return_value="elegivel")
        
        with patch.object(registry, 'get_handler', return_value=mock_handler):
            result = await registry.process_eligibility("amil", "123456")
            assert result == "elegivel"
            mock_handler.assert_called_once_with("123456")
    
    @pytest.mark.asyncio
    async def test_process_eligibility_handler_error(self, registry):
        """Testa processamento quando handler falha"""
        # Mock do handler que levanta exceção
        mock_handler = AsyncMock(side_effect=Exception("Erro no handler"))
        
        with patch.object(registry, 'get_handler', return_value=mock_handler):
            result = await registry.process_eligibility("amil", "123456")
            # Deve retornar não elegível por segurança
            assert result == "nao_elegivel"
    
    @pytest.mark.asyncio
    async def test_process_eligibility_plan_not_found(self, registry):
        """Testa processamento para plano não suportado"""
        result = await registry.process_eligibility("plano_ficticio", "123456")
        # Deve retornar não elegível por segurança
        assert result == "nao_elegivel"
    
    def test_register_handler(self, registry):
        """Testa registro de novo handler"""
        mock_handler = AsyncMock(return_value="elegivel")
        
        initial_count = len(registry.list_supported_plans())
        registry.register_handler("unimed", mock_handler)
        
        assert len(registry.list_supported_plans()) == initial_count + 1
        assert "unimed" in registry.list_supported_plans()
        
        # Testa se o handler foi registrado corretamente
        handler = registry.get_handler("unimed")
        assert handler == mock_handler 