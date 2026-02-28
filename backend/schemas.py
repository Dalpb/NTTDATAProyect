from pydantic import BaseModel, Field
from typing import Optional

# 1. Lo que recibimos del Frontend (Usuario Final)
class TicketCreate(BaseModel):
    descripcion_original: str = Field(..., example="Mi pantalla se puso azul y perdí mi Excel.")
    usuario_id: int

# 2. Lo que LangChain/Gemini debe devolver obligatoriamente (JSON Estricto)
class ResultadoIA(BaseModel):
    categoria_sugerida_ia: str = Field(description="Categoría principal: Hardware, Software, Redes, Accesos")
    subcategoria_sugerida_ia: str = Field(description="Subcategoría específica del problema")
    impacto_ia: str = Field(description="Nivel de impacto: Alto, Medio, Bajo")
    urgencia_ia: str = Field(description="Nivel de urgencia: Alta, Media, Baja")
    prioridad_sugerida_ia: str = Field(description="Prioridad calculada: Crítica, Alta, Media, Baja")
    sentimiento_usuario: str = Field(description="Estado emocional del usuario: Frustrado, Neutral, Urgente, etc.")
    tags_extraidos: str = Field(description="3 a 5 palabras clave separadas por comas")
    respuesta_sugerida_ia: str = Field(description="Respuesta amable de primer nivel sugerida para el usuario")

# 3. Lo que devolvemos al Frontend como respuesta final
class TicketResponse(BaseModel):
    id: int
    titulo: str
    estado: str
    resultado_ia: Optional[ResultadoIA] = None

    class Config:
        from_attributes = True

class DatosTicket(BaseModel):
    categoria: str = Field(description="Hardware, Software, Redes, Accesos")
    impacto: str = Field(description="Alto, Medio, Bajo")
    urgencia: str = Field(description="Alta, Media, Baja")
    tags: str = Field(description="Palabras clave")

# El esquema MAESTRO que el LLM debe devolver en cada turno
class RespuestaAgente(BaseModel):
    estado_conversacion: str = Field(
        description="DEBE SER UNO DE ESTOS: 'recolectando_info' (si faltan datos), 'listo_para_crear' (si ya hay info suficiente), 'evaluando_solucion' (si diste un paso a seguir y esperas respuesta), 'resuelto' (si el usuario dice que ya funciona)."
    )
    mensaje_para_usuario: str = Field(description="La respuesta amable o la pregunta que el asistente le hace al usuario.")
    datos_extraidos: Optional[DatosTicket] = Field(description="Solo llénalo si el estado es 'listo_para_crear' o posterior. Si estás recolectando info, déjalo nulo.")

# Lo que entra desde tu frontend (Next.js)
class MensajeChat(BaseModel):
    session_id: str # Para identificar la conversación del usuario
    usuario_id: int
    mensaje: str