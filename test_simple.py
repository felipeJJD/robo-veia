import asyncio
import os
from app.handlers.amil_simple import amil_simple_handler

async def test():
    print("Testando handler simplificado...")
    
    # Simular ambiente Railway
    os.environ["RAILWAY_ENVIRONMENT"] = "true"
    
    result = await amil_simple_handler.check_eligibility('086955681')
    print(f'Resultado para 086955681: {result}')
    
    result2 = await amil_simple_handler.check_eligibility('123456789')
    print(f'Resultado para 123456789: {result2}')

if __name__ == "__main__":
    asyncio.run(test()) 