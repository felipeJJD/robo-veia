#!/bin/bash

# Script de setup para o Robo Veia
# Micro-serviço de elegibilidade de carteirinhas

set -e

echo "🤖 Robo Veia - Setup Script"
echo "=============================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.10 ou superior."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then 
    echo "❌ Python $PYTHON_VERSION encontrado. É necessário Python $REQUIRED_VERSION ou superior."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION encontrado"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Instalar Playwright
echo "🎭 Instalando Playwright Chromium..."
playwright install chromium

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado."
    echo "📝 Criando arquivo .env a partir do exemplo..."
    
    cat > .env << 'EOF'
# Credenciais do Amil
AMIL_LOGIN=10354263
AMIL_PASSWORD=imc@2025

# Configurações da aplicação
LOG_LEVEL=INFO
WEBHOOK_CALLBACK_URL=https://web-hook.imca.app.br/webhook/a4c4db28-1c03-4233-959d-6f89630daae4
WEBHOOK_TIMEOUT=10
WEBHOOK_MAX_RETRIES=3

# Configurações de timeout
AMIL_TIMEOUT=90000

# Configurações opcionais
PORT=8000
EOF
    
    echo "✅ Arquivo .env criado com valores padrão"
    echo "⚠️  Ajuste as credenciais conforme necessário"
else
    echo "✅ Arquivo .env já existe"
fi

echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "📚 Próximos passos:"
echo "1. Ativar o ambiente virtual: source venv/bin/activate"
echo "2. Verificar/ajustar variáveis em .env"
echo "3. Executar testes: pytest"
echo "4. Iniciar servidor: uvicorn app.main:app --reload"
echo ""
echo "📖 Documentação disponível em: http://localhost:8000/docs"
echo "🔍 Health check em: http://localhost:8000/health"
echo ""
echo "🚀 Happy coding!" 