from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="WhatsApp Business API")

################################################################
# Endpoints para Cuenta
################################################################
@app.post("/cuentas/", response_model=schemas.Cuenta)
def crear_cuenta(cuenta: schemas.CuentaCreate, db: Session = Depends(get_db)):
    db_cuenta = models.Cuenta(**cuenta.dict())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta

@app.get("/cuentas/", response_model=List[schemas.Cuenta])
def listar_cuentas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Cuenta).offset(skip).limit(limit).all()

# Buscar cuenta por instancia_evolution
@app.get("/cuentas/instancia/{instancia_evolution}", response_model=schemas.Cuenta)
def buscar_cuenta_por_instancia(instancia_evolution: str, db: Session = Depends(get_db)):
    cuenta = db.query(models.Cuenta).filter(models.Cuenta.instancia_evolution == instancia_evolution).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

################################################################
# Endpoints para Etiquetas
################################################################
@app.post("/etiquetas/", response_model=schemas.Etiqueta)
def crear_etiqueta(etiqueta: schemas.EtiquetaCreate, db: Session = Depends(get_db)):
    db_etiqueta = models.Etiqueta(**etiqueta.dict())
    db.add(db_etiqueta)
    db.commit()
    db.refresh(db_etiqueta)
    return db_etiqueta

@app.get("/etiquetas/cuenta/{cuenta_id}", response_model=List[schemas.Etiqueta])
def listar_etiquetas_por_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    return db.query(models.Etiqueta).filter(models.Etiqueta.cuenta_id == cuenta_id).all()

@app.delete("/etiquetas/{etiqueta_id}/{cuenta_id}")
def eliminar_etiqueta(etiqueta_id: int, cuenta_id: int, db: Session = Depends(get_db)):
    etiqueta = db.query(models.Etiqueta).filter(models.Etiqueta.id == etiqueta_id, models.Etiqueta.cuenta_id == cuenta_id).first()
    if not etiqueta:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    etiqueta.eliminado = True
    db.commit()
    return {"mensaje": "Etiqueta eliminada correctamente"}


################################################################
# Endpoints para CabeceraChat
################################################################
@app.post("/chats/", response_model=schemas.CabeceraChat)
def crear_chat(chat: schemas.CabeceraChatCreate, db: Session = Depends(get_db)):
    db_chat = models.CabeceraChat(**chat.dict())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@app.get("/chats/cuenta/{cuenta_id}", response_model=List[schemas.CabeceraChat])
def listar_chats_por_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    return db.query(models.CabeceraChat).filter(models.CabeceraChat.cuenta_id == cuenta_id).all()

# Buscar chat por numero_de_contacto
@app.get("/chats/numero/{numero_de_contacto}", response_model=schemas.CabeceraChat)
def buscar_chat_por_numero(numero_de_contacto: str, db: Session = Depends(get_db)):
    chat = db.query(models.CabeceraChat).filter(models.CabeceraChat.numero_de_contacto == numero_de_contacto).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    return chat


################################################################
# Endpoints para ChatEtiqueta
################################################################
@app.post("/chat-etiquetas/", response_model=schemas.ChatEtiqueta)
def asignar_etiqueta_a_chat(chat_etiqueta: schemas.ChatEtiquetaCreate, db: Session = Depends(get_db)):
    db_chat_etiqueta = models.ChatEtiqueta(**chat_etiqueta.dict())
    db.add(db_chat_etiqueta)
    db.commit()
    db.refresh(db_chat_etiqueta)
    return db_chat_etiqueta

@app.delete("/chat-etiquetas/{chat_id}/{etiqueta_id}/{cuenta_id}")
def eliminar_etiqueta_de_chat(chat_id: int, etiqueta_id: int, cuenta_id: int, db: Session = Depends(get_db)):
    db_chat_etiqueta = db.query(models.ChatEtiqueta).filter(
        models.ChatEtiqueta.chat_id == chat_id,
        models.ChatEtiqueta.etiqueta_id == etiqueta_id,
        models.ChatEtiqueta.cuenta_id == cuenta_id
    ).first()
    if not db_chat_etiqueta:
        raise HTTPException(status_code=404, detail="Relación chat-etiqueta no encontrada")
    db.delete(db_chat_etiqueta)
    db.commit()
    return {"mensaje": "Etiqueta removida del chat correctamente"}

@app.get("/chat-etiquetas/chat/{chat_id}", response_model=List[schemas.Etiqueta])
def obtener_etiquetas_de_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.CabeceraChat).filter(models.CabeceraChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    etiquetas = db.query(models.Etiqueta).join(models.ChatEtiqueta).filter(
        models.ChatEtiqueta.chat_id == chat_id
    ).all()
    return etiquetas 