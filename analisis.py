# 1_analisis_palabras.py
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("📥 Descargando recursos de NLTK...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

df = pd.read_csv("tweets_api_puro.csv")
def parse_number(x):
    try:
        x = str(x).strip().lower()
        if x in ["", "nan", "n/a", "none", "0"]:
            return 0
        x = re.sub(r'[^\d.km]', '', x)
        if "k" in x:
            return float(x.replace("k", "")) * 1_000
        elif "m" in x:
            return float(x.replace("m", "")) * 1_000_000
        return float(x) if x else 0
    except:
        return 0


df["Likes"] = df["Likes"].apply(parse_number)
df["Retweets"] = df["Retweets"].apply(parse_number)

totals = {"Likes": df["Likes"].sum(), "Retweets": df["Retweets"].sum()}
plt.figure(figsize=(8, 5))
bars = plt.bar(totals.keys(), totals.values(), color=["#E53935", "#43A047"])
plt.title("Interacciones totales en tweets", fontsize=14, weight='bold')
plt.ylabel("Cantidad")
for bar in bars:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(totals.values()) * 0.01,
             f'{int(bar.get_height()):,}', ha='center', va='bottom')
plt.tight_layout()

top_n = max(5, len(df) // 10)
top_tweets = df.nlargest(top_n, "Retweets")

print(f"🔍 Analizando palabras clave en los {len(top_tweets)} tweets con más retweets...")

text_viral = " ".join(top_tweets["Texto"].dropna().astype(str))

def clean_text(text):
    text = re.sub(r"http\S+|www\S+", "", text)  # URLs
    text = re.sub(r"[@#]\w+", "", text)  # @usuario, #hashtag
    text = re.sub(r"[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s]", " ", text)  # Solo letras
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


cleaned_text = clean_text(text_viral)
tokens = word_tokenize(cleaned_text)

try:
    spanish_stops = set(stopwords.words('spanish'))
    english_stops = set(stopwords.words('english'))
except:
    spanish_stops = {"el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le", "da", "por",
                     "con", "para", "su", "al", "del"}
    english_stops = {"the", "and", "to", "of", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are",
                     "as", "with", "his", "they", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word",
                     "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "each",
                     "which", "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them",
                     "these", "so", "some", "her", "would", "make", "like", "into", "him", "time", "two", "more", "go",
                     "no", "way", "could", "my", "than", "first", "been", "call", "who", "oil", "sit", "now", "find",
                     "down", "day", "did", "get", "come", "made", "may", "part"}

stop_words = spanish_stops | english_stops | {"rt", "amp", "via", "tco", "https", "http", "twitter", "com", "co"}

keywords = [word for word in tokens if len(word) > 2 and word not in stop_words]
word_freq = Counter(keywords)
top_words = word_freq.most_common(15)

if top_words:
    words, counts = zip(*top_words)
    plt.figure(figsize=(10, 6))
    plt.barh(words[::-1], counts[::-1], color="#0077B6")
    plt.title("Palabras clave en tweets con más retweets\n(Español + Inglés)", fontsize=14, weight='bold')
    plt.xlabel("Frecuencia")
    plt.tight_layout()


    print("\nTop palabras clave (español + inglés):")
    for word, count in top_words:
        print(f"  • {word}: {count}")

    palabras_solo = [word for word, _ in top_words[:8]]  # Tomamos top 8
    with open("palabras_clave.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(palabras_solo))
    print("\n✅ Palabras clave exportadas a 'palabras_clave.txt'")

else:
    print(" No se encontraron palabras clave significativas.")
    with open("palabras_clave.txt", "w", encoding="utf-8") as f:
        f.write("truth\nfreedom\namerica")
    print(" Archivo 'palabras_clave.txt' creado con valores por defecto.")