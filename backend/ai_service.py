import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from schemas import RespuestaAgente

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    google_api_key=os.getenv("GEMINI_API_KEY"), # Tu clave actual sigue funcionando
    temperature=0.2
)

parser = PydanticOutputParser(pydantic_object=RespuestaAgente)

plantilla_sistema = """
Eres un Dispatcher ITIL y Asistente de Soporte TI. Tu trabajo es hablar con el usuario para resolver su incidente.

FLUJO DE TRABAJO (ESTADOS):
1. recolectando_info: Si el mensaje del usuario es vago (ej. "mi compu no va"), haz preguntas cortas para saber qué pasa, desde cuándo y a cuántos afecta.
2. listo_para_crear: Cuando ya sepas el problema real, su impacto y urgencia, extrae los datos, y en tu mensaje dale una sugerencia de cómo arreglarlo (ej. "Intenta reiniciar el router").
3. evaluando_solucion: Si ya le diste una sugerencia, pregúntale si funcionó.
4. resuelto: Si el usuario confirma que tu sugerencia arregló el problema.

REGLA DE ORO: 
Siempre debes responder en un formato JSON estricto basado en las siguientes instrucciones:
{format_instructions}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", plantilla_sistema),
    MessagesPlaceholder(variable_name="historial_chat"),
    ("human", "{mensaje_actual}")
]).partial(format_instructions=parser.get_format_instructions())

cadena_agente = prompt | llm | parser

# MEMORIA TEMPORAL (Diccionario para guardar el contexto de la charla)
memoria_sesiones = {}

def procesar_chat(session_id: str, mensaje: str) -> RespuestaAgente:
    # Si la sesión es nueva, creamos su lista de historial
    if session_id not in memoria_sesiones:
        memoria_sesiones[session_id] = []
    
    historial = memoria_sesiones[session_id]

    # Ejecutar LangChain con el historial
    resultado_ia = cadena_agente.invoke({
        "historial_chat": historial,
        "mensaje_actual": mensaje
    })

    # Guardar en la memoria el mensaje del usuario y la respuesta de la IA
    memoria_sesiones[session_id].append(HumanMessage(content=mensaje))
    memoria_sesiones[session_id].append(AIMessage(content=resultado_ia.mensaje_para_usuario))

    return resultado_ia