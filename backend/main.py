from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, get_db
import models

# En producción no se suele usar create_all aquí, pero para el MVP es útil
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ITSM GenAI API")

@app.get("/")
def read_root():
    return {"mensaje": "API del Asistente ITSM funcionando"}

@app.get("/api/v1/incidentes")
def obtener_incidentes(db: Session = Depends(get_db)):
    # Retorna todos los incidentes para el dashboard del frontend
    incidentes = db.query(models.Incidente).all()
    return incidentes