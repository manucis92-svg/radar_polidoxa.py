from twilio.rest import Client
import os

twilio_client = Client(
    os.environ["TWILIO_ACCOUNT_SID"],
    os.environ["TWILIO_AUTH_TOKEN"]
)

TWILIO_FROM = os.environ["TWILIO_FROM"]
TWILIO_TO = os.environ["TWILIO_TO"]






import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def obtener_noticias():
    print("Noticias:", noticias)
    import requests
    from bs4 import BeautifulSoup

    url = "https://news.google.com/rss/search?q=politica%20argentina&hl=es-419&gl=AR&ceid=AR:es-419"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "xml")

    noticias = []

    for item in soup.find_all("item")[:10]:
        titulo = item.title.text
        link = item.link.text
        noticias.append({"titulo": titulo, "link": link})

    return noticias


def analizar_agenda(noticias):
    texto = "\n".join([f"- {n['titulo']} ({n['link']})" for n in noticias])

    prompt = f"""
    Sos consultor senior de Polidoxa.

    Analizá esta agenda política argentina:

    {texto}

    Respondé en formato profesional:

    🔴 TEMA DOMINANTE:
    (breve)

    🟠 EJES SECUNDARIOS:
    (3 puntos)

    👥 ACTORES CLAVE:

    🧠 NARRATIVAS:

    🚨 ALERTAS:

    📈 CLIMA GENERAL:

    🎯 OPORTUNIDADES:

    🧩 SÍNTESIS EJECUTIVA:
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def generar_pdf(informe):
    doc = SimpleDocTemplate("radar_polidoxa.pdf", pagesize=A4)
    styles = getSampleStyleSheet()

    contenido = []
    contenido.append(Paragraph("<b>POLIDOXA | RADAR PÚBLICO</b>", styles["Title"]))

    for linea in informe.split("\n"):
        contenido.append(Paragraph(linea, styles["Normal"]))

    doc.build(contenido)


noticias = obtener_noticias()
informe = analizar_agenda(noticias)

print(informe)

generar_pdf(informe)







import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def obtener_noticias():
    url = "https://news.google.com/search?q=politica%20argentina&hl=es-419&gl=AR&ceid=AR:es-419"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    noticias = []

    for item in soup.find_all("article")[:10]:
        link = item.find("a")
        if link:
            titulo = link.text
            href = "https://news.google.com" + link.get("href")[1:]
            noticias.append({"titulo": titulo, "link": href})

    return noticias


def analizar_agenda(noticias):
    texto = "\n".join([f"- {n['titulo']} ({n['link']})" for n in noticias])

    prompt = f"""
    Sos consultor senior de Polidoxa.

    Analizá esta agenda política argentina:

    {texto}

    Respondé en formato profesional:

    🔴 TEMA DOMINANTE:
    (breve)

    🟠 EJES SECUNDARIOS:
    (3 puntos)

    👥 ACTORES CLAVE:

    🧠 NARRATIVAS:

    🚨 ALERTAS:

    📈 CLIMA GENERAL:

    🎯 OPORTUNIDADES:

    🧩 SÍNTESIS EJECUTIVA:
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def generar_pdf(informe):
    doc = SimpleDocTemplate("radar_polidoxa.pdf", pagesize=A4)
    styles = getSampleStyleSheet()

    contenido = []
    contenido.append(Paragraph("<b>POLIDOXA | RADAR PÚBLICO</b>", styles["Title"]))

    for linea in informe.split("\n"):
        contenido.append(Paragraph(linea, styles["Normal"]))

    doc.build(contenido)


noticias = obtener_noticias()
informe = analizar_agenda(noticias)

print(informe)
twilio_client.messages.create(
    from_=TWILIO_FROM,
    to=TWILIO_TO,
    body=informe[:1500]
)
generar_pdf(informe)


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])




with open("radar_polidoxa.txt", "w") as f:
    f.write(informe)




with open("radar_polidoxa.txt", "w") as f:
    f.write(informe)
