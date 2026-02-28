import os
from dotenv import load_dotenv

# Esto busca el archivo .env en tu carpeta y carga las variables en os.environ
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Variable global para almacenar el motor de búsqueda en memoria
vectorstore = None

# ==========================================
# 1. LÓGICA DE INICIALIZACIÓN
# ==========================================
def inicializar_base_vectorial():
    global vectorstore
    print("Iniciando microservicio RAG: Cargando documentos desde /data...")
    
    # 1. Cargar documentos
    loader = DirectoryLoader('./data', glob="**/*.txt", loader_cls=TextLoader)
    documentos = loader.load()
    
    if not documentos:
        print("Advertencia: No hay documentos en /data.")
        return
        
    # 2. Dividir en fragmentos
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    fragmentos = text_splitter.split_documents(documentos)
    
    # 3. Crear Embeddings con Gemini y guardar en Chroma (memoria)
    # ¡Ahora tomará la llave automáticamente de tu .env!
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma.from_documents(documents=fragmentos, embedding=embeddings)
    print(f"RAG listo. {len(fragmentos)} fragmentos indexados.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_base_vectorial()
    yield

# ==========================================
# 2. CONFIGURACIÓN DE LA API
# ==========================================
app = FastAPI(title="Microservicio RAG - Búsqueda Vectorial", lifespan=lifespan)

class ConsultaRAG(BaseModel):
    query: str
    k: int = 3

class RespuestaRAG(BaseModel):
    resultados: List[str]

# ==========================================
# 3. EL ENDPOINT ÚNICO
# ==========================================
@app.post("/buscar", response_model=RespuestaRAG)
async def buscar_contexto(consulta: ConsultaRAG):
    if not vectorstore:
        raise HTTPException(status_code=500, detail="La BD vectorial no está inicializada.")
    
    try:
        docs_similares = vectorstore.similarity_search(consulta.query, k=consulta.k)
        textos_limpios = [doc.page_content for doc in docs_similares]
        return RespuestaRAG(resultados=textos_limpios)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))