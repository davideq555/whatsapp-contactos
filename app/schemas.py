from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Esquemas para Cuenta
class CuentaBase(BaseModel):
    nombre_cuenta: str
    instancia_evolution: str
    numero_corporativo: str
    numero_personal: str
    nombre_personal: str

class CuentaCreate(CuentaBase):
    pass

class Cuenta(CuentaBase):
    id: int

    class Config:
        from_attributes = True

# Esquemas para Etiqueta
class EtiquetaBase(BaseModel):
    nombre: str
    color: Optional[str]
    cuenta_id: int
    id: int

class EtiquetaCreate(EtiquetaBase):
    pass

class Etiqueta(EtiquetaBase):
    id: int
    eliminado: bool = False

    class Config:
        from_attributes = True

# Esquemas para CabeceraChat
class CabeceraChatBase(BaseModel):
    cuenta_id: int
    numero_de_contacto: str

class CabeceraChatCreate(CabeceraChatBase):
    pass

class CabeceraChat(CabeceraChatBase):
    id: int
    created_at: datetime
    bloqueado_at: Optional[datetime] = None
    intentos_maliciosos: int = 0

    class Config:
        from_attributes = True

# Esquemas para ChatEtiqueta
class ChatEtiquetaBase(BaseModel):
    chat_id: int
    etiqueta_id: int
    cuenta_id: int

class ChatEtiquetaCreate(ChatEtiquetaBase):
    pass

class ChatEtiqueta(ChatEtiquetaBase):
    class Config:
        from_attributes = True 