import os, json, csv, base64, requests
from datetime import datetime
from bs4 import BeautifulSoup
from openai import OpenAI
from twilio.rest import Client
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
twilio = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

TWILIO_FROM = os.environ["TWILIO_FROM"]
TWILIO_TO = os.environ["TWILIO_TO"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = "main"

hoy = datetime.now().strftime("%d/%m/%Y")
fecha_archivo = datetime.now().strftime("%Y-%m-%d")


def obtener_noticias():
    urls = [
        "https://news.google.com/rss/search?q=politica%20argentina&hl=es-419&gl=AR&ceid=AR:es-419",
        "https://news.google.com/rss/search?q=economia%20argentina%20gobierno&hl=es-419&gl=AR&ceid=AR:es-419",
        "https://news.google.com/rss/search?q=congreso%20argentina%20milei&hl=es-419&gl=AR&ceid=AR:es-419",
    ]

    palabras_clave = [
        "milei", "gobierno", "congreso", "senado", "diputados", "oposición",
        "elecciones", "inflación", "dólar", "paro", "protesta", "justicia",
        "reforma", "ley", "sindicatos", "provincia", "kicillof", "ucr"
    ]

    noticias = []
    vistos = set()

    for url in urls:
        r = requests.get(url, timeout=20)
        soup = BeautifulSoup(r.content, "xml")

        for item in soup.find_all("item"):
            titulo = item.title.text.strip()
            link = item.link.text.strip()
            titulo_lower = titulo.lower()

            if titulo in vistos:
                continue

            if any(p in titulo_lower for p in palabras_clave):
                noticias.append({"titulo": titulo, "link": link})
                vistos.add(titulo)

            if len(noticias) >= 18:
                break

    return noticias


def analizar_agenda(noticias):
    texto_noticias = "\n".join(
        [f"- {n['titulo']} | Link: {n['link']}" for n in noticias]
    )

    prompt = f"""
Sos director de inteligencia política de Polidoxa.

REGLAS:
- No inventes información.
- Usá únicamente estas noticias.
- Si un tema aparece una sola vez, marcá "señal débil".
- No proyectes escenarios futuros.
- Incluí links reales.

Noticias:
{texto_noticias}

Devolvé SOLO JSON válido, sin texto adicional, con esta estructura exacta:

{{
  "fecha": "{hoy}",
  "resumen_ejecutivo": "",
  "tema_dominante": {{
    "tema": "",
    "descripcion": "",
    "actores": [],
    "riesgo": "bajo/medio/alto/crítico"
  }},
  "ejes_secundarios": [
    {{"tema": "", "impacto": "", "riesgo": "bajo/medio/alto/crítico"}}
  ],
  "matriz_riesgo": {{
    "riesgo_politico": 0,
    "viralidad": 0,
    "danio_reputacional": 0,
    "oportunidad_comunicacional": 0
  }},
  "narrativas": {{
    "oficialismo": "",
    "oposicion": "",
    "social_emergente": ""
  }},
  "actores_clave": {{
    "ganan": [],
    "pierden": [],
    "expuestos": []
  }},
  "alertas": [
    {{"nivel": "roja/amarilla/verde", "tema": "", "motivo": ""}}
  ],
  "oportunidades": {{
    "oficialismo": "",
    "oposicion_moderada": "",
    "actores_territoriales": ""
  }},
  "recomendacion_polidoxa": "",
  "fuentes": [
    {{"titulo": "", "link": ""}}
  ]
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    texto = response.output_text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
    return json.loads(texto)


def generar_pdf(data):
    archivo = f"polidoxa_brief_{fecha_archivo}.pdf"
    doc = SimpleDocTemplate(archivo, pagesize=A4)
    styles = getSampleStyleSheet()
    contenido = []

    contenido.append(Paragraph("<b>POLIDOXA | INTELLIGENCE BRIEF ARGENTINA</b>", styles["Title"]))
    contenido.append(Paragraph(f"<b>Fecha:</b> {data['fecha']}", styles["Normal"]))
    contenido.append(Spacer(1, 12))

    secciones = [
        ("1. Resumen ejecutivo", data["resumen_ejecutivo"]),
        ("2. Tema dominante", f"{data['tema_dominante']['tema']} | Riesgo: {data['tema_dominante']['riesgo']}<br/>{data['tema_dominante']['descripcion']}"),
        ("3. Batalla narrativa", f"Oficialismo: {data['narrativas']['oficialismo']}<br/>Oposición: {data['narrativas']['oposicion']}<br/>Social emergente: {data['narrativas']['social_emergente']}"),
        ("4. Recomendación Polidoxa", data["recomendacion_polidoxa"]),
    ]

    for titulo, texto in secciones:
        contenido.append(Paragraph(f"<b>{titulo}</b>", styles["Heading2"]))
        contenido.append(Paragraph(str(texto), styles["Normal"]))
        contenido.append(Spacer(1, 10))

    contenido.append(Paragraph("<b>5. Fuentes</b>", styles["Heading2"]))
    for f in data["fuentes"]:
        contenido.append(Paragraph(f"{f['titulo']}<br/>{f['link']}", styles["Normal"]))
        contenido.append(Spacer(1, 6))

    doc.build(contenido)
    return archivo


def generar_dashboard_html(data):
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Polidoxa Dashboard</title>
<style>
body {{ font-family: Arial; background:#f4f7f7; color:#163B3F; padding:30px; }}
.card {{ background:white; padding:20px; border-radius:14px; margin-bottom:18px; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
h1 {{ color:#0E6F78; }}
.metric {{ display:inline-block; width:22%; background:#e7f3f3; padding:15px; border-radius:12px; margin:5px; }}
</style>
</head>
<body>
<h1>POLIDOXA | DASHBOARD DE RIESGO POLÍTICO</h1>
<p><b>Fecha:</b> {data['fecha']}</p>

<div class="card">
<h2>Tema dominante</h2>
<p><b>{data['tema_dominante']['tema']}</b></p>
<p>{data['tema_dominante']['descripcion']}</p>
<p><b>Riesgo:</b> {data['tema_dominante']['riesgo']}</p>
</div>

<div class="card">
<h2>Matriz de riesgo</h2>
<div class="metric">Riesgo político<br><b>{data['matriz_riesgo']['riesgo_politico']}/100</b></div>
<div class="metric">Viralidad<br><b>{data['matriz_riesgo']['viralidad']}/100</b></div>
<div class="metric">Daño reputacional<br><b>{data['matriz_riesgo']['danio_reputacional']}/100</b></div>
<div class="metric">Oportunidad<br><b>{data['matriz_riesgo']['oportunidad_comunicacional']}/100</b></div>
</div>

<div class="card">
<h2>Alertas</h2>
<ul>
{''.join([f"<li><b>{a['nivel'].upper()}</b>: {a['tema']} — {a['motivo']}</li>" for a in data['alertas']])}
</ul>
</div>

<div class="card">
<h2>Fuentes</h2>
<ul>
{''.join([f"<li><a href='{f['link']}'>{f['titulo']}</a></li>" for f in data['fuentes']])}
</ul>
</div>

</body>
</html>
"""
    archivo = "index.html"
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(html)
    return archivo


def generar_csv_dashboard(data):
    archivo = "dashboard_polidoxa.csv"
    existe = os.path.exists(archivo)

    with open(archivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not existe:
            writer.writerow([
                "fecha", "tema_dominante", "riesgo", "riesgo_politico",
                "viralidad", "danio_reputacional", "oportunidad"
            ])

        writer.writerow([
            data["fecha"],
            data["tema_dominante"]["tema"],
            data["tema_dominante"]["riesgo"],
            data["matriz_riesgo"]["riesgo_politico"],
            data["matriz_riesgo"]["viralidad"],
            data["matriz_riesgo"]["danio_reputacional"],
            data["matriz_riesgo"]["oportunidad_comunicacional"]
        ])

    return archivo


def subir_a_github(local_file, repo_path):
    url = f"https://api.github.com/repos/{REPO}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    with open(local_file, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    sha = None
    get = requests.get(url, headers=headers, params={"ref": BRANCH})
    if get.status_code == 200:
        sha = get.json()["sha"]

    payload = {
        "message": f"Actualizar {repo_path} - {fecha_archivo}",
        "content": content,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=headers, json=payload)
    r.raise_for_status()


def armar_mensaje_whatsapp(data, pdf_url, dashboard_url):
    ejes = "\n".join([
        f"- {e['tema']} | Riesgo: {e['riesgo']}"
        for e in data["ejes_secundarios"][:3]
    ])

    alertas = "\n".join([
        f"- {a['nivel'].upper()}: {a['tema']}"
        for a in data["alertas"][:3]
    ])

    fuentes = "\n".join([
        f"- {f['titulo']}: {f['link']}"
        for f in data["fuentes"][:3]
    ])

    return f"""
📊 POLIDOXA | INTELLIGENCE BRIEF ARGENTINA
📅 {data['fecha']}

1. RESUMEN EJECUTIVO
{data['resumen_ejecutivo']}

2. TEMA DOMINANTE
{data['tema_dominante']['tema']}
Riesgo: {data['tema_dominante']['riesgo']}
{data['tema_dominante']['descripcion']}

3. EJES SECUNDARIOS
{ejes}

4. ALERTAS
{alertas}

5. RECOMENDACIÓN POLIDOXA
{data['recomendacion_polidoxa']}

🔗 PDF: {pdf_url}
📊 Dashboard: {dashboard_url}

FUENTES
{fuentes}
""".strip()


def enviar_whatsapp(mensaje):
    twilio.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body=mensaje[:1500]
    )


def enviar_pdf_whatsapp(pdf_url):
    twilio.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body="📄 POLIDOXA | Informe completo en PDF",
        media_url=[pdf_url]
    )


def hay_alerta_roja(data):
    return any(a["nivel"].lower() == "roja" for a in data["alertas"])


noticias = obtener_noticias()

if not noticias:
    enviar_whatsapp("POLIDOXA | ERROR: no se encontraron noticias para analizar.")
else:
    data = analizar_agenda(noticias)

    pdf = generar_pdf(data)
    html = generar_dashboard_html(data)
    csv_file = generar_csv_dashboard(data)

    subir_a_github(pdf, f"docs/{pdf}")
    subir_a_github(html, "docs/index.html")
    subir_a_github(csv_file, "dashboard/dashboard_polidoxa.csv")

    pdf_url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/docs/{pdf}"
    dashboard_url = f"https://{REPO.split('/')[0]}.github.io/{REPO.split('/')[1]}/"

    mensaje = armar_mensaje_whatsapp(data, pdf_url, dashboard_url)

    print("MENSAJE A ENVIAR:")
print(mensaje)

enviar_whatsapp(mensaje)
    enviar_pdf_whatsapp(pdf_url)

    if hay_alerta_roja(data):
        enviar_whatsapp("🚨 POLIDOXA ALERTA ROJA: se detectó un foco de crisis de alto riesgo.")

    print(mensaje)
