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


def analizar_agenda(noticias):
    texto_noticias = "\n".join(
        [f"- {n['titulo']} | Link: {n['link']}" for n in noticias]
    )

    prompt = f"""
Sos consultor senior de la consultora Polidoxa.

Analizá la agenda pública y política argentina a partir de estas noticias reales:

{texto_noticias}

Elaborá un informe breve para WhatsApp con este formato:

POLIDOXA | RADAR PÚBLICO ARGENTINA

1. Tema dominante:
2. Ejes secundarios:
3. Actores clave:
4. Narrativas en disputa:
5. Alertas de crisis:
6. Clima general:
7. Oportunidades de comunicación:
8. Síntesis ejecutiva:
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
