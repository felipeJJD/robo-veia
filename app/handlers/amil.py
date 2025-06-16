"""
Handler para verificação de elegibilidade no plano Amil
🎯 Versão com automação real usando Playwright
"""
import os
import asyncio
from typing import Literal
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from app.utils.logger import logger, log_with_context


class AmilHandler:
    """Handler para verificação de elegibilidade no Amil com automação real"""
    
    def __init__(self):
        self.login = os.getenv("AMIL_LOGIN", "10354263")
        self.password = os.getenv("AMIL_PASSWORD", "imc@2025")
        self.timeout = int(os.getenv("AMIL_TIMEOUT", "30000"))  # 30 segundos
        self.base_url = "https://credenciado.amil.com.br"
        
        # Browser instances para reutilização
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.session_ativa = False
        
        if not self.login or not self.password:
            raise ValueError("Credenciais do Amil não configuradas (AMIL_LOGIN e AMIL_PASSWORD)")

    async def _iniciar_browser(self) -> bool:
        """🚀 Inicia o browser Playwright"""
        
        try:
            log_with_context(logger, "INFO", "Iniciando browser Playwright")
            
            playwright = await async_playwright().start()
            
            # Configura browser para ambiente Railway
            self.browser = await playwright.chromium.launch(
                headless=True,  # Sempre headless em produção
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            # Cria contexto com user-agent realista
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1366, 'height': 768},
                locale='pt-BR',
                timezone_id='America/Sao_Paulo'
            )
            
            # Cria página
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.timeout)
            
            log_with_context(logger, "INFO", "Browser iniciado com sucesso")
            return True
            
        except Exception as e:
            log_with_context(
                logger, "ERROR", 
                f"Erro ao iniciar browser: {str(e)}",
                error_type=type(e).__name__
            )
            return False

    async def _fazer_login(self) -> bool:
        """🔑 Faz login automático no portal Amil"""
        
        log_with_context(logger, "INFO", "Fazendo login no portal Amil")
        
        try:
            # Navega para página inicial
            await self.page.goto(self.base_url, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Aceita cookies se aparecer
            try:
                await self.page.click('button:has-text("Aceitar")', timeout=3000)
                await asyncio.sleep(1)
            except:
                pass
            
            # Preenche credenciais
            await self.page.fill('input[type="text"], input[name="usuario"]', self.login)
            await asyncio.sleep(0.5)
            
            await self.page.fill('input[type="password"], input[name="senha"]', self.password)
            await asyncio.sleep(0.5)
            
            # Clica em entrar
            await self.page.click('button.btn-primary, button:has-text("Entrar"), input[type="submit"]')
            await asyncio.sleep(5)
            
            # Verifica se login foi bem-sucedido
            current_url = self.page.url
            is_logged_in = ('/login' not in current_url and 
                          ('/institucional' in current_url or 
                           '/dashboard' in current_url or
                           '/home' in current_url or
                           '/pedidos' in current_url))
            
            if is_logged_in:
                log_with_context(logger, "INFO", "Login realizado com sucesso")
                self.session_ativa = True
                return True
            else:
                log_with_context(logger, "ERROR", f"Falha no login - URL atual: {current_url}")
                return False
                
        except Exception as e:
            log_with_context(
                logger, "ERROR",
                f"Erro durante login: {str(e)}",
                error_type=type(e).__name__
            )
            return False

    async def _consultar_carteirinha(self, numero_carteirinha: str) -> Literal["elegivel", "nao_elegivel"]:
        """🎯 Consulta elegibilidade da carteirinha via interface visual"""
        
        try:
            # Navega para página de consulta
            url_consulta = f"{self.base_url}/pedidos-autorizacao;numeroAssociado={numero_carteirinha}"
            log_with_context(logger, "INFO", f"Navegando para consulta: {numero_carteirinha}")
            
            await self.page.goto(url_consulta, wait_until='networkidle')
            await asyncio.sleep(3)
            
            # Analisa a página para detectar elegibilidade
            resultado = await self.page.evaluate("""
                () => {
                    // Analisa elementos visuais na página
                    const pageText = document.body.innerText.toLowerCase();
                    
                    // Verifica indicadores de ELEGÍVEL
                    const indicadoresElegivel = [
                        'cliente elegível',
                        'beneficiário está elegível', 
                        'elegibilidade.elegivel',
                        'status: ativo',
                        'plano válido',
                        'amil s750',
                        'ambulatorial'
                    ];
                    
                    // Verifica indicadores de NÃO ELEGÍVEL
                    const indicadoresNaoElegivel = [
                        'contrato não encontrado',
                        'beneficiário não encontrado',
                        'carteirinha inválida',
                        'plano cancelado',
                        'não elegível',
                        'bloqueado'
                    ];
                    
                    let elegivel = null;
                    let motivo = '';
                    
                    // Primeiro verifica se é elegível
                    for (const indicador of indicadoresElegivel) {
                        if (pageText.includes(indicador)) {
                            elegivel = true;
                            motivo = `Encontrado indicador: "${indicador}"`;
                            break;
                        }
                    }
                    
                    // Se não encontrou elegível, verifica não elegível
                    if (elegivel === null) {
                        for (const indicador of indicadoresNaoElegivel) {
                            if (pageText.includes(indicador)) {
                                elegivel = false;
                                motivo = `Encontrado indicador: "${indicador}"`;
                                break;
                            }
                        }
                    }
                    
                    // Verifica elementos visuais específicos
                    const elementoVerde = document.querySelector('.alert-success, .text-success, .bg-success');
                    const elementoVermelho = document.querySelector('.alert-danger, .text-danger, .bg-danger');
                    
                    if (elegivel === null) {
                        if (elementoVerde) {
                            elegivel = true;
                            motivo = 'Elemento visual verde detectado';
                        } else if (elementoVermelho) {
                            elegivel = false;
                            motivo = 'Elemento visual vermelho detectado';
                        }
                    }
                    
                    return {
                        elegivel,
                        motivo,
                        tamanhoConteudo: pageText.length,
                        url: window.location.href
                    };
                }
            """)
            
            if resultado['elegivel'] is True:
                log_with_context(
                    logger, "INFO",
                    f"Carteirinha ELEGÍVEL: {numero_carteirinha}",
                    numero_carteirinha=numero_carteirinha,
                    motivo=resultado['motivo']
                )
                return "elegivel"
            elif resultado['elegivel'] is False:
                log_with_context(
                    logger, "INFO",
                    f"Carteirinha NÃO ELEGÍVEL: {numero_carteirinha}",
                    numero_carteirinha=numero_carteirinha,
                    motivo=resultado['motivo']
                )
                return "nao_elegivel"
            else:
                log_with_context(
                    logger, "WARNING",
                    f"Status indeterminado para carteirinha: {numero_carteirinha}",
                    numero_carteirinha=numero_carteirinha
                )
                # Em caso de indeterminado, assumir não elegível por segurança
                return "nao_elegivel"
            
        except Exception as e:
            log_with_context(
                logger, "ERROR",
                f"Erro na consulta da carteirinha: {str(e)}",
                numero_carteirinha=numero_carteirinha,
                error_type=type(e).__name__
            )
            # Em caso de erro, assumir não elegível por segurança
            return "nao_elegivel"

    async def _fechar_browser(self):
        """🔒 Fecha browser e limpa recursos"""
        
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            
            self.session_ativa = False
            log_with_context(logger, "INFO", "Browser fechado com sucesso")
            
        except Exception as e:
            log_with_context(
                logger, "ERROR",
                f"Erro ao fechar browser: {str(e)}",
                error_type=type(e).__name__
            )

    async def check_eligibility(self, numero_carteirinha: str) -> Literal["elegivel", "nao_elegivel"]:
        """
        Verifica elegibilidade da carteirinha no site do Amil usando automação real
        
        Args:
            numero_carteirinha: Número da carteirinha a ser verificada
            
        Returns:
            Status da elegibilidade baseado na automação real do site
        """
        log_with_context(
            logger, "INFO",
            "Iniciando verificação de elegibilidade Amil com automação real",
            numero_carteirinha=numero_carteirinha
        )
        
        try:
            # Inicia browser se necessário
            if not self.browser or not self.session_ativa:
                if not await self._iniciar_browser():
                    log_with_context(logger, "ERROR", "Falha ao iniciar browser")
                    return "nao_elegivel"
                
                if not await self._fazer_login():
                    log_with_context(logger, "ERROR", "Falha no login")
                    return "nao_elegivel"
            
            # Consulta carteirinha
            resultado = await self._consultar_carteirinha(numero_carteirinha)
            
            log_with_context(
                logger, "INFO",
                "Verificação concluída com sucesso",
                numero_carteirinha=numero_carteirinha,
                status=resultado
            )
            
            return resultado
                    
        except Exception as e:
            log_with_context(
                logger, "ERROR",
                f"Erro durante verificação de elegibilidade: {str(e)}",
                numero_carteirinha=numero_carteirinha,
                error_type=type(e).__name__
            )
            return "nao_elegivel"
        
        finally:
            # Fecha browser após cada consulta para economizar recursos
            await self._fechar_browser()


# Instância global do handler
amil_handler = AmilHandler()