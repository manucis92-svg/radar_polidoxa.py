import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from twilio.rest import Client

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

twilio_client = Client(
    os.environ["TWILIO_ACCOUNT_SID"],
    os.environ["TWILIO_AUTH_TOKEN"]
)

TWILIO_FROM = os.environ["TWILIO_FROM"]
TWILIO_TO = os.environ["TWILIO_TO"]


def obtener_noticias():
    url = "https://news.google.com/rss/search?q=politica%20argentina&hl=es-419&gl=AR&ceid=AR:es-419"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")

    noticias = []

    for item in soup.find_all("item")[:10]:
        noticias.append({
            "titulo": item.title.text,
            "link": item.link.text
        })

    return noticias


prompt = f"""
Sos director de inteligencia política de Polidoxa, una consultora especializada en escucha digital, opinión pública y análisis estratégico.

Trabajás con estándares de consultoría internacional: claridad ejecutiva, análisis de riesgo, lectura narrativa, impacto político y recomendaciones accionables.

Analizá la agenda pública y política argentina a partir de estas noticias reales:

{texto_noticias}

Elaborá un informe profesional en formato ejecutivo para WhatsApp, con lenguaje claro, estratégico y no partidario.

Formato obligatorio:

📊 POLIDOXA | INTELLIGENCE BRIEF ARGENTINA
📅 Fecha: {hoy}

1. RESUMEN EJECUTIVO
Sintetizá en 3 líneas qué está pasando y por qué importa.

2. TEMA DOMINANTE
Identificá el tema que ordena la agenda del día.
Incluí:
- descripción breve
- actores involucrados
- nivel de riesgo: bajo / medio / alto / crítico

3. EJES SECUNDARIOS
Listá hasta 3 temas relevantes.
Para cada uno:
- tema
- impacto político
- riesgo

4. MATRIZ DE RIESGO
Asigná puntajes de 0 a 100:
- riesgo político
- viralidad
- daño reputacional
- oportunidad comunicacional

5. BATALLA NARRATIVA
Separá:
- narrativa oficialista
- narrativa opositora
- narrativa social emergente

6. ACTORES CLAVE
Identificá quién gana, quién pierde y quién queda expuesto.

7. ALERTAS DE CRISIS
Indicá si hay:
- alerta roja
- alerta amarilla
- alerta verde
Explicá brevemente por qué.

8. OPORTUNIDADES DE COMUNICACIÓN
Recomendá 3 acciones concretas para:
- oficialismo
- oposición moderada
- actores territoriales

9. RECOMENDACIÓN POLIDOXA
Una recomendación estratégica breve, accionable y profesional.

10. FUENTES
Incluí los links principales usados.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def enviar_whatsapp(mensaje):
    twilio_client.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body=mensaje[:1500]
    )


noticias = obtener_noticias()
informe = analizar_agenda(noticias)
enviar_whatsapp(informe)

print(informe)
