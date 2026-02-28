from database import engine, SessionLocal, Base
from models import Usuario, Incidente

def init_db():
    print("Limpiando base de datos (Drop & Create) para actualizar estructura...")
    # ATENCIÓN: drop_all borra todas las tablas. Es ideal para MVP/Desarrollo, 
    # pero NO se usa en producción.
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas con la nueva estructura ITSM.")

def seed_data():
    db = SessionLocal()

    print("Insertando datos de prueba...")
    
    # 1. Crear usuarios (un empleado normal y un agente de soporte TI)
    user_empleado = Usuario(nombre="Ana López", email="ana.lopez@empresa.com", rol="empleado", departamento="Ventas")
    user_agente = Usuario(nombre="Carlos Dev", email="carlos.dev@empresa.com", rol="agente_ti", departamento="Sistemas")
    
    db.add_all([user_empleado, user_agente])
    db.commit()
    # Refrescamos para obtener los IDs generados por MySQL
    db.refresh(user_empleado)
    db.refresh(user_agente)

    # 2. Crear un incidente NUEVO (Simulando que acaba de entrar, la IA aún no lo procesa)
    incidente_nuevo = Incidente(
        titulo="Problema con la VPN",
        descripcion_original="No me puedo conectar a la VPN desde mi casa, me sale error 809 y necesito entrar al servidor urgentemente para una presentación.",
        canal_ingreso="portal_web",
        usuario_id=user_empleado.id
        # No tiene campos de IA ni agente asignado todavía
    )

    # 3. Crear un incidente PROCESADO (Simulando que LangChain ya lo analizó y un agente lo tomó)
    incidente_procesado = Incidente(
        titulo="Pantalla azul al abrir Excel",
        descripcion_original="Cada vez que intento abrir el reporte financiero en Excel, la laptop se reinicia con una pantalla azul. Estoy muy frustrado porque pierdo mi trabajo.",
        canal_ingreso="email",
        equipo_afectado="Laptop Lenovo T14",
        estado="en_progreso",
        usuario_id=user_empleado.id,
        asignado_a_id=user_agente.id, # Ya está asignado a Carlos Dev
        
        # --- Datos simulados generados por la IA ---
        categoria_sugerida_ia="Hardware/SO",
        subcategoria_sugerida_ia="Fallo de Sistema / BSOD",
        impacto_ia="Alto",
        urgencia_ia="Alta",
        prioridad_sugerida_ia="Crítica",
        sentimiento_usuario="Frustrado",
        tags_extraidos="excel, pantalla azul, bsod, reinicio, lenovo",
        respuesta_sugerida_ia="Hola Ana, lamento el inconveniente. Este error de pantalla azul (BSOD) al usar Excel podría deberse a un problema con los controladores de video o un fallo en la RAM. Por favor, guarda cualquier otro trabajo y acércate a la mesa de ayuda de TI, o indícanos si prefieres que nos conectemos remotamente en modo seguro."
    )

    db.add_all([incidente_nuevo, incidente_procesado])
    db.commit()

    print("¡Datos insertados correctamente! Tienes 2 usuarios y 2 incidentes listos para probar.")
    db.close()

if __name__ == "__main__":
    init_db()
    seed_data()