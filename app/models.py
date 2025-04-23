from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Cuenta(Base):
    __tablename__ = "cuenta"

    id = Column(Integer, primary_key=True, index=True)
    nombre_cuenta = Column(String)
    instancia_evolution = Column(String)
    numero_corporativo = Column(String)
    numero_personal = Column(String)
    nombre_personal = Column(String)

    # Relaciones
    cabeceras_chat = relationship("CabeceraChat", back_populates="cuenta")


class CabeceraChat(Base):
    __tablename__ = "cabecera_chat"

    id = Column(Integer, primary_key=True, index=True)
    cuenta_id = Column(Integer, ForeignKey("cuenta.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    bloqueado_at = Column(DateTime, nullable=True)
    numero_de_contacto = Column(String)
    intentos_maliciosos = Column(Integer, default=0)

    # Relaciones
    cuenta = relationship("Cuenta", back_populates="cabeceras_chat")
    etiquetas = relationship(
        "ChatEtiqueta",  # Relación con la tabla intermedia
        back_populates="chat"
    )


class Etiqueta(Base):
    __tablename__ = "etiqueta"
    
    id = Column(Integer, primary_key=True)
    cuenta_id = Column(Integer, ForeignKey("cuenta.id"), primary_key=True)  # Llave compuesta
    nombre = Column(String)
    color = Column(String)
    eliminado = Column(Boolean, default=False)

    # Relaciones
    chats = relationship(
        "ChatEtiqueta",  # Relación con la tabla intermedia
        back_populates="etiqueta"
    )


class ChatEtiqueta(Base):
    __tablename__ = "chat_etiqueta"

    chat_id = Column(Integer, ForeignKey("cabecera_chat.id"), primary_key=True)
    etiqueta_id = Column(Integer, ForeignKey("etiqueta.id"), primary_key=True)
    cuenta_id = Column(Integer, ForeignKey("cuenta.id"), primary_key=True)

    # Relaciones
    chat = relationship("CabeceraChat", back_populates="etiquetas")
    etiqueta = relationship("Etiqueta", back_populates="chats")