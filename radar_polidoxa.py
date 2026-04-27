import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from openai import OpenAI
from twilio.rest import Client
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# =========================
# CONFIGURACIÓN
# =========================

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

twilio_client = Client(
    os.environ["TWILIO_ACCOUNT_SID"],
    os.environ["TWILIO_AUTH_TOKEN"]
)

TWILIO_FROM = os.environ["TWILIO_FROM"]
TWILIO_TO = os.environ["TWILIO_TO"]

hoy = datetime.now().strftime("%d/%m/%Y")


# =========================
# 1. OBTENER NOTICIAS
# =========================

def obtener_noticias():
    url = "https://news.google.com/rss/search?q=politica%20argentina&hl=es-419&gl=AR&ceid=AR:es-419"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")

    noticias = []

    for item in soup.find_all("item")[:12]:
        noticias.append({
            "titulo": item.title.text,
            "link": item.link.text
        })

    return noticias


# =========================
# 2. ANALIZAR AGENDA
# =========================

def analizar_agenda(noticias):
    texto_noticias = "\n".join(
        [f"- {n['titulo']} | Link: {n['link']}" for n in noticias]
    )

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


# =========================
# 3. GENERAR PDF
# =========================

def generar_pdf(informe):
    archivo_pdf = "polidoxa_intelligence_brief.pdf"

    doc = SimpleDocTemplate(archivo_pdf, pagesize=A4)
    styles = getSampleStyleSheet()

    contenido = []
    contenido.append(Paragraph("<b>POLIDOXA | INTELLIGENCE BRIEF ARGENTINA</b>", styles["Title"]))
    contenido.append(Spacer(1, 12))
    contenido.append(Paragraph(f"<b>Fecha:</b> {hoy}", styles["Normal"]))
    contenido.append(Spacer(1, 12))

    for linea in informe.split("\n"):
        if linea.strip():
            texto = linea.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            contenido.append(Paragraph(texto, styles["Normal"]))
            contenido.append(Spacer(1, 6))

    doc.build(contenido)

    return archivo_pdf


# =========================
# 4. ENVIAR WHATSAPP
# =========================

def enviar_whatsapp(mensaje):
    twilio_client.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body=mensaje[:1500]
    )


# =========================
# 5. ALERTA AUTOMÁTICA
# =========================

def detectar_alerta(informe):
    palabras_alerta = [
        "crisis",
        "escándalo",
        "conflicto",
        "denuncia",
        "corrupción",
        "represión",
        "paro",
        "protesta",
        "judicialización",
        "riesgo alto",
        "riesgo crítico",
        "alerta roja"
    ]

    informe_lower = informe.lower()

    return any(palabra in informe_lower for palabra in palabras_alerta)


# =========================
# 6. EJECUCIÓN PRINCIPAL
# =========================

noticias = obtener_noticias()

if not noticias:
    mensaje_error = "POLIDOXA | ERROR: No se encontraron noticias para analizar."
    enviar_whatsapp(mensaje_error)
    print(mensaje_error)

else:
    informe = analizar_agenda(noticias)

    generar_pdf(informe)

    mensaje_whatsapp = informe[:1400] + "\n\n📄 PDF generado automáticamente por Polidoxa."

    enviar_whatsapp(mensaje_whatsapp)

    if detectar_alerta(informe):
        enviar_whatsapp("🚨 POLIDOXA ALERTA: posible foco de crisis detectado en la agenda pública argentina.")

    print(informe)
