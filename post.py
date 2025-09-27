# post.py
import requests
import json
import re
import random
import os


def detectar_tema(palabras):
    palabras = [p.lower() for p in palabras]
    if any(p in palabras for p in ["trump", "biden", "elecciones", "guerra", "otan", "política", "gobierno", "rom"]):
        return "politica"
    elif any(p in palabras for p in
             ["ia", "ai", "blockchain", "internet", "tecnología", "digital", "robot", "cisternas", "camión", "tren"]):
        return "tecnologia"
    elif any(p in palabras for p in ["clima", "medio ambiente", "calentamiento", "eco", "sostenible"]):
        return "medioambiente"
    else:
        return "general"


def generar_tweet_local(keywords: str) -> str:
    palabras = [w.strip() for w in keywords.split(",") if w.strip()]
    if not palabras:
        palabras = ["verdad", "futuro", "acción"]

    tema = detectar_tema(palabras)
    p1 = palabras[0].capitalize()
    p2 = palabras[1] if len(palabras) > 1 else "verdad"
    p3 = palabras[2] if len(palabras) > 2 else "actuar"

    if tema == "politica":
        plantillas = [
            f"¿{p1} defiende al pueblo o al sistema? La respuesta define nuestro futuro.",
            f"No se trata de {p1}. Se trata de si {p2} aún importa en este país.",
            f"Ellos hablan de {p1}. Nosotros exigimos {p2}. ¿Hasta cuándo esperamos para {p3}?",
            f"La historia no juzgará tus tweets. Juzgará si {p3} cuando era necesario.",
        ]
    elif tema == "tecnologia":
        plantillas = [
            f"La verdadera {p2} no es tener tecnología, sino saber usarla con propósito.",
            f"{p1} no es el futuro. Es el presente. Y quien no {p3} hoy, desaparecerá mañana.",
            f"No necesitas más innovación. Necesitas más {p2}. El resto es ruido.",
            f"¿Tu empresa usa {p1} para resolver problemas o solo para parecer moderna?",
        ]
    elif tema == "medioambiente":
        plantillas = [
            f"El planeta no necesita más promesas. Necesita {p3} concreto. Hoy.",
            f"Decir que te importa el clima no basta. ¿Qué haces con {p1} y {p2}?",
        ]
    else:
        plantillas = [
            f"{p1} no es un lujo. Es una necesidad. Y {p2} es el precio de ignorarlo.",
            f"El mundo no necesita más opiniones. Necesita más {p3}. Empieza por ti.",
            f"¿Hablas de {p1} o haces algo al respecto? La diferencia define tu impacto.",
            f"Detrás de cada gran cambio hay alguien que decidió {p3}, no esperar.",
        ]

    tweet = random.choice(plantillas)
    if len(tweet) > 280:
        tweet = tweet[:277] + "…"
    return tweet


def generar_tweet_viral(keywords: str) -> str:

    url = "http://localhost:11434/api/generate"
    prompt = f"""
Eres un estratega de redes sociales experto. Genera UN SOLO TWEET que:
- Use naturalmente: {keywords}
- Sea provocador, breve (200-280 chars), y genere debate usa preguntas sarcasticas
- Suene 100% humano. Sin hashtags ni URLs.
Solo el tweet. Nada más.
"""

    payload = {
        "model": "llama3:8b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.85, "top_p": 0.9}
    }

    try:
        requests.get("http://localhost:11434", timeout=0.1)
        response = requests.post(url, json=payload, timeout=1)
        response.raise_for_status()
        result = response.json()
        tweet = result.get("response", "").strip()
        tweet = re.sub(r"\s+", " ", tweet)
        if len(tweet) > 280:
            tweet = tweet[:277] + "…"
        return tweet
    except Exception as e:
        print(f"ℹ️ Ollama no disponible ({type(e).__name__}). Usando generación local...")
        return generar_tweet_local(keywords)

if __name__ == "__main__":


    try:
        with open("palabras_clave.txt", "r", encoding="utf-8") as f:
            keywords = f.read().strip().replace("\n", ", ")
        if not keywords:
            raise ValueError("Archivo vacío")
    except Exception as e:
        print(f"❌ Error al leer 'palabras_clave.txt': {e}")
        exit(1)


    try:
        tweet = generar_tweet_viral(keywords)
        print("\n" + "=" * 60)
        print("✅ TWEET GENERADO:")
        print("=" * 60)
        print(tweet)
        print("=" * 60)

        with open("tweet_proposal.txt", "w", encoding="utf-8") as f:
            f.write(tweet)
        print("\n📄 Guardado en 'tweet_proposal.txt'")
    except Exception as e:
        print(f"\n❌ Error final: {e}")
        exit(1)