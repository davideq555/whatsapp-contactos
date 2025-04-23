from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde el archivo .env

# Define el nombre del header donde se enviará la API Key
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", "default-api-key")  # Obtiene la API Key de las variables de entorno
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: API Key inválida"
        )
    return api_key