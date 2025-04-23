from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .security import validate_api_key
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="WhatsApp Business API")

################################################################
# Endpoints para Cuenta
################################################################
@app.post("/cuentas/", response_model=schemas.Cuenta, dependencies=[Depends(validate_api_key)])
def crear_cuenta(cuenta: schemas.CuentaCreate, db: Session = Depends(get_db)):
    db_cuenta = models.Cuenta(**cuenta.dict())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta

@app.get("/cuentas/", response_model=List[schemas.Cuenta], dependencies=[Depends(validate_api_key)])
def listar_cuentas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Cuenta).offset(skip).limit(limit).all()

# Buscar cuenta por instancia_evolution
@app.get("/cuentas/instancia/{instancia_evolution}", response_model=schemas.Cuenta, dependencies=[Depends(validate_api_key)])
def buscar_cuenta_por_instancia(instancia_evolution: str, db: Session = Depends(get_db)):
    cuenta = db.query(models.Cuenta).filter(models.Cuenta.instancia_evolution == instancia_evolution).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

################################################################
# Endpoints para Etiquetas
################################################################
@app.post("/etiquetas/", response_model=schemas.Etiqueta, dependencies=[Depends(validate_api_key)])
def crear_etiqueta(etiqueta: schemas.EtiquetaCreate, db: Session = Depends(get_db)):
    db_etiqueta = models.Etiqueta(**etiqueta.dict())
    db.add(db_etiqueta)
    db.commit()
    db.refresh(db_etiqueta)
    return db_etiqueta

@app.get("/etiquetas/cuenta/{cuenta_id}", response_model=List[schemas.Etiqueta], dependencies=[Depends(validate_api_key)])
def listar_etiquetas_por_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    return db.query(models.Etiqueta).filter(models.Etiqueta.cuenta_id == cuenta_id).all()

@app.delete("/etiquetas/{etiqueta_id}/{cuenta_id}", dependencies=[Depends(validate_api_key)])
def eliminar_etiqueta(etiqueta_id: int, cuenta_id: int, db: Session = Depends(get_db)):
    etiqueta = db.query(models.Etiqueta).filter(models.Etiqueta.id == etiqueta_id, models.Etiqueta.cuenta_id == cuenta_id).first()
    if not etiqueta:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    # eliminar relacion de etiquetas con chats
    db_chat_etiquetas = db.query(models.ChatEtiqueta).filter(
        models.ChatEtiqueta.etiqueta_id == etiqueta_id, 
        models.ChatEtiqueta.cuenta_id == cuenta_id
    ).all()
    for chat_etiqueta in db_chat_etiquetas:
        db.delete(chat_etiqueta)
    etiqueta.eliminado = True
    db.commit()
    return {"mensaje": "Etiqueta eliminada correctamente"}


################################################################
# Endpoints para CabeceraChat
################################################################
@app.post("/chats/", response_model=schemas.ChatResponse, dependencies=[Depends(validate_api_key)])
def crear_o_obtener_chat(chat: schemas.CabeceraChatCreate, db: Session = Depends(get_db)):
    # Intentar obtener el chat existente
    db_chat = db.query(models.CabeceraChat).filter(
        models.CabeceraChat.numero_de_contacto == chat.numero_de_contacto,
        models.CabeceraChat.cuenta_id == chat.cuenta_id
    ).first()
    if db_chat:
        return {
            "mensaje": "Chat ya existente",
            "chat": schemas.CabeceraChat.from_orm(db_chat)
        }
    else:
        # Crear un nuevo chat si no existe
        db_chat = models.CabeceraChat(**chat.dict())
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return {
            "mensaje": "Chat creado exitosamente",
            "chat": schemas.CabeceraChat.from_orm(db_chat)
        }

@app.get("/chats/cuenta/{cuenta_id}", response_model=List[schemas.CabeceraChat], dependencies=[Depends(validate_api_key)])
def listar_chats_por_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    return db.query(models.CabeceraChat).filter(models.CabeceraChat.cuenta_id == cuenta_id).all()


################################################################
# Endpoints para ChatEtiqueta
################################################################
@app.post("/chat-etiquetas/", response_model=schemas.ChatEtiqueta, dependencies=[Depends(validate_api_key)])
def asignar_etiqueta_a_chat(chat_etiqueta: schemas.ChatEtiquetaCreate, db: Session = Depends(get_db)):
    db_chat_etiqueta = models.ChatEtiqueta(**chat_etiqueta.dict())
    db.add(db_chat_etiqueta)
    db.commit()
    db.refresh(db_chat_etiqueta)
    return db_chat_etiqueta

@app.delete("/chat-etiquetas/{chat_id}/{etiqueta_id}/{cuenta_id}", dependencies=[Depends(validate_api_key)])
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

@app.delete("/chat-etiquetas/{numero_de_contacto}/{etiqueta_id}/{cuenta_id}", dependencies=[Depends(validate_api_key)])
def eliminar_etiqueta_de_chat_por_numero(
    numero_de_contacto: str,
    etiqueta_id: int,
    cuenta_id: int,
    db: Session = Depends(get_db)
):
    # Buscar el chat por numero_de_contacto y cuenta_id
    chat = db.query(models.CabeceraChat).filter(
        models.CabeceraChat.numero_de_contacto == numero_de_contacto,
        models.CabeceraChat.cuenta_id == cuenta_id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")

    # Buscar la relación en ChatEtiqueta
    chat_etiqueta = db.query(models.ChatEtiqueta).filter(
        models.ChatEtiqueta.chat_id == chat.id,
        models.ChatEtiqueta.etiqueta_id == etiqueta_id,
        models.ChatEtiqueta.cuenta_id == cuenta_id
    ).first()

    if not chat_etiqueta:
        raise HTTPException(status_code=404, detail="Relación chat-etiqueta no encontrada")

    # Eliminar la relación
    db.delete(chat_etiqueta)
    db.commit()

    return {"mensaje": "Etiqueta removida del chat correctamente"}

@app.get("/chat-etiquetas/chat/{chat_id}", response_model=List[schemas.Etiqueta], dependencies=[Depends(validate_api_key)])
def obtener_etiquetas_de_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.CabeceraChat).filter(models.CabeceraChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    etiquetas = db.query(models.Etiqueta).join(models.ChatEtiqueta).filter(
        models.ChatEtiqueta.chat_id == chat_id
    ).all()
    return etiquetas 

# Obtiene etiquetas de un chat específico usando el numero_de_contacto y cuenta_id
@app.get("/chat-etiquetas/chat/{numero_de_contacto}/{cuenta_id}", response_model=List[schemas.Etiqueta], dependencies=[Depends(validate_api_key)])
def obtener_etiquetas_de_chat(numero_de_contacto: str, cuenta_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.CabeceraChat).filter(
        models.CabeceraChat.numero_de_contacto == numero_de_contacto,
        models.CabeceraChat.cuenta_id == cuenta_id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    etiquetas = db.query(models.Etiqueta).join(models.ChatEtiqueta).filter(
        models.ChatEtiqueta.chat_id == chat.id
    ).all()
    return etiquetas

@app.post("/chats/etiquetas/", response_model=schemas.ChatEtiqueta, dependencies=[Depends(validate_api_key)])
def crear_chat_etiqueta(
    numero_de_contacto: str,
    cuenta_id: int,
    etiqueta_id: int,
    db: Session = Depends(get_db)
):
    # Buscar el chat por numero_de_contacto y cuenta_id
    chat = db.query(models.CabeceraChat).filter(
        models.CabeceraChat.numero_de_contacto == numero_de_contacto,
        models.CabeceraChat.cuenta_id == cuenta_id
    ).first()

    # Si no existe, crear el chat
    if not chat:
        chat = models.CabeceraChat(
            numero_de_contacto=numero_de_contacto,
            cuenta_id=cuenta_id
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)

    # Verificar si ya existe la relación en ChatEtiqueta
    chat_etiqueta = db.query(models.ChatEtiqueta).filter(
        models.ChatEtiqueta.chat_id == chat.id,
        models.ChatEtiqueta.etiqueta_id == etiqueta_id,
        models.ChatEtiqueta.cuenta_id == cuenta_id
    ).first()

    if chat_etiqueta:
        raise HTTPException(status_code=400, detail="La etiqueta ya está asociada a este chat")

    # Crear la relación en ChatEtiqueta
    chat_etiqueta = models.ChatEtiqueta(
        chat_id=chat.id,
        etiqueta_id=etiqueta_id,
        cuenta_id=cuenta_id
    )
    db.add(chat_etiqueta)
    db.commit()
    db.refresh(chat_etiqueta)

    return schemas.ChatEtiqueta.from_orm(chat_etiqueta)