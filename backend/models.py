from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    # Corregido: primary_key=True
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    rol = Column(String(50), default="empleado") # 'empleado', 'agente_ti', 'admin'
    departamento = Column(String(100))

    # Relaciones actualizadas para manejar creadores y agentes asignados
    incidentes_creados = relationship("Incidente", foreign_keys="[Incidente.usuario_id]", back_populates="creador")
    incidentes_asignados = relationship("Incidente", foreign_keys="[Incidente.asignado_a_id]", back_populates="asignado_a")

class Incidente(Base):
    __tablename__ = "incidentes"

    # Corregido: primary_key=True
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion_original = Column(Text, nullable=False)
    
    # --- Datos Operativos del ITSM ---
    estado = Column(String(50), default="abierto") # abierto, en_progreso, resuelto, cerrado
    canal_ingreso = Column(String(50), default="portal_web") # portal_web, email, chatbot
    equipo_afectado = Column(String(100), nullable=True) # Ej: "Laptop Dell", "Servidor Correo"
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_resolucion = Column(DateTime, nullable=True)
    
    # --- Datos extraídos o generados por LangChain (IA Generativa) ---
    categoria_sugerida_ia = Column(String(100), nullable=True)
    subcategoria_sugerida_ia = Column(String(100), nullable=True) # Más detalle
    impacto_ia = Column(String(50), nullable=True) # Alto, Medio, Bajo
    urgencia_ia = Column(String(50), nullable=True) # Alta, Media, Baja
    prioridad_sugerida_ia = Column(String(50), nullable=True) # Crítica, Alta, Media, Baja
    sentimiento_usuario = Column(String(50), nullable=True) # Ej: "Frustrado", "Neutral", "Urgente"
    tags_extraidos = Column(String(255), nullable=True) # Palabras clave (ej: "vpn, error 809, red")
    respuesta_sugerida_ia = Column(Text, nullable=True)
    # ------------------------------------------------------------------

    # Llaves foráneas
    usuario_id = Column(Integer, ForeignKey("usuarios.id")) # Quien reporta el problema
    asignado_a_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Agente de TI a cargo
    
    # Relaciones inversas
    creador = relationship("Usuario", foreign_keys=[usuario_id], back_populates="incidentes_creados")
    asignado_a = relationship("Usuario", foreign_keys=[asignado_a_id], back_populates="incidentes_asignados")