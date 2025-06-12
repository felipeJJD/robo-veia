#!/usr/bin/env python3
"""
Script para testar importações e detectar problemas
"""
import os
import sys
import traceback

def test_imports():
    """Testa todas as importações críticas"""
    try:
        print("🔍 Testando importações...")
        
        # Testar importações básicas
        import os
        print("✅ os")
        
        import asyncio
        print("✅ asyncio")
        
        # Testar FastAPI
        from fastapi import FastAPI
        print("✅ FastAPI")
        
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ CORSMiddleware")
        
        # Testar importações do app
        from app.router import router
        print("✅ app.router")
        
        from app.utils.logger import logger
        print("✅ app.utils.logger")
        
        from app.dispatch import handler_registry
        print("✅ app.dispatch")
        
        from app.handlers.generic import generic_handler
        print("✅ app.handlers.generic")
        
        # Testar handler específico baseado no ambiente
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
            from app.handlers.amil_simple import amil_simple_handler
            print("✅ app.handlers.amil_simple (Railway)")
        else:
            try:
                from app.handlers.amil import amil_handler
                print("✅ app.handlers.amil (Local)")
            except ImportError:
                from app.handlers.amil_simple import amil_simple_handler
                print("✅ app.handlers.amil_simple (Fallback)")
        
        print("\n🎉 Todas as importações funcionaram!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na importação: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

def test_app_creation():
    """Testa criação da aplicação FastAPI"""
    try:
        print("\n🔍 Testando criação da aplicação...")
        from app.main import app
        print("✅ Aplicação FastAPI criada com sucesso")
        return True
    except Exception as e:
        print(f"\n❌ Erro na criação da aplicação: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🤖 Robo Veia - Teste de Importações")
    print("=" * 40)
    
    # Mostrar informações do ambiente
    print(f"Python: {sys.version}")
    print(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
    print(f"Railway Project ID: {os.getenv('RAILWAY_PROJECT_ID', 'Not set')}")
    print(f"PORT: {os.getenv('PORT', 'Not set')}")
    print()
    
    success = True
    
    # Testar importações
    if not test_imports():
        success = False
    
    # Testar criação da aplicação
    if not test_app_creation():
        success = False
    
    if success:
        print("\n🎉 Todos os testes passaram! A aplicação deve funcionar.")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1) 