from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from ai_service import procesar_chat, memoria_sesiones

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ITSM GenAI Assistant API")

# ==========================================
# ENDPOINT PARA EL DASHBOARD DE TI (Técnicos)
# ==========================================
@app.get("/api/v1/incidentes")
def obtener_todos_los_incidentes(db: Session = Depends(get_db)):
    # Esto es lo que consumiría la pantalla de Vercel para listar tickets
    return db.query(models.Incidente).order_by(models.Incidente.creado_en.desc()).all()

# ==========================================
# ENDPOINT DEL CHAT (El Orquestador)
# ==========================================
@app.post("/api/v1/chat")
def interactuar_con_agente(chat: schemas.MensajeChat, db: Session = Depends(get_db)):
    
    # 1. El Agente (Gemini) evalúa el mensaje y el contexto de la charla
    respuesta_ia = procesar_chat(chat.session_id, chat.mensaje)
    
    # 2. Tomar decisiones en la Base de Datos según el ESTADO
    
    if respuesta_ia.estado_conversacion == "listo_para_crear" and respuesta_ia.datos_extraidos:
        # La IA decidió que ya tiene toda la info. Guardamos el incidente.
        nuevo_incidente = models.Incidente(
            titulo=f"Incidente: {respuesta_ia.datos_extraidos.categoria}",
            descripcion_original=chat.mensaje, # O idealmente un resumen de la charla
            usuario_id=chat.usuario_id,
            estado="abierto",
            canal_ingreso="chatbot_ia",
            categoria_sugerida_ia=respuesta_ia.datos_extraidos.categoria,
            impacto_ia=respuesta_ia.datos_extraidos.impacto,
            urgencia_ia=respuesta_ia.datos_extraidos.urgencia,
            respuesta_sugerida_ia=respuesta_ia.mensaje_para_usuario
        )
        db.add(nuevo_incidente)
        db.commit()
        db.refresh(nuevo_incidente)
        
        # Opcional: Podrías guardar el ID del ticket en la memoria para actualizarlo después
        # memoria_sesiones[chat.session_id + "_ticket_id"] = nuevo_incidente.id

    elif respuesta_ia.estado_conversacion == "resuelto":
        # El usuario dijo "¡Gracias, ya funcionó!". Buscamos el último ticket del usuario y lo cerramos.
        # (En un flujo real, usarías el ticket_id guardado en la sesión)
        ticket_abierto = db.query(models.Incidente).filter(
            models.Incidente.usuario_id == chat.usuario_id,
            models.Incidente.estado != "resuelto"
        ).order_by(models.Incidente.creado_en.desc()).first()
        
        if ticket_abierto:
            ticket_abierto.estado = "resuelto"
            db.commit()
            
        # Limpiamos la memoria porque ya se resolvió
        if chat.session_id in memoria_sesiones:
            del memoria_sesiones[chat.session_id]

    # 3. Responder al Frontend (Next.js solo muestra el 'mensaje_para_usuario')
    return {
        "estado_flujo": respuesta_ia.estado_conversacion,
        "mensaje_bot": respuesta_ia.mensaje_para_usuario
    }