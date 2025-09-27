# main_menu.py
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import pandas as pd
import json
import re
from collections import Counter
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def ensure_llama3_model():
    model_path = os.path.expandvars(r"C:\Users\%USERNAME%\Ollama\models\llama3-8b")
    if not os.path.exists(model_path):
        print("Descargando modelo llama3:8b, esto puede tardar varios minutos...")
        subprocess.run([
            r"C:\Program Files\Ollama\ollama.exe", "pull", "llama3:8b"
        ], check=True)

ensure_llama3_model()

def guardar_credenciales(usuario, password, termino_busqueda, num_scrolls=5):
    with open("credenciales_temp.json", "w", encoding="utf-8") as f:
        json.dump({
            "usuario": usuario,
            "password": password,
            "hashtag": termino_busqueda,
            "num_scrolls": num_scrolls
        }, f)

class MenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Bot X - Menú Principal")
        self.root.geometry("750x550")
        self.crear_menu_inicio()

    def crear_menu_inicio(self):
        self.limpiar_ventana()

        tk.Label(self.root, text="Iniciar Sesión y Búsqueda", font=("Arial", 16, "bold")).pack(pady=15)

        # Usuario
        tk.Label(self.root, text="Usuario:").pack()
        self.entry_usuario = tk.Entry(self.root, width=40)
        self.entry_usuario.pack(pady=3)

        # Contraseña
        tk.Label(self.root, text="Contraseña:").pack()
        self.entry_password = tk.Entry(self.root, show="*", width=40)
        self.entry_password.pack(pady=3)

        # Término de búsqueda
        tk.Label(self.root, text="Término de búsqueda (ej: #IA, Trump, clima):").pack(pady=(10, 0))
        self.entry_busqueda = tk.Entry(self.root, width=40)
        self.entry_busqueda.insert(0, "#IA")  # valor por defecto
        self.entry_busqueda.pack(pady=3)

        # Botones
        tk.Button(self.root, text="Scraping", command=self.iniciar_scraping, bg="#4CAF50", fg="white", width=20).pack(
            pady=12)
        tk.Button(self.root, text="Análisis", command=self.iniciar_analisis, bg="#2196F3", fg="white", width=20).pack(
            pady=8)
        tk.Button(self.root, text="Crear Post", command=self.iniciar_post, bg="#FF9800", fg="white", width=20).pack(
            pady=8)

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def ejecutar_script(self, script):

        try:
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300
            )
            if result.returncode != 0:
                messagebox.showerror("Error", f"El script falló:\n{result.stderr}")
                return False
            return True
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "El script tardó demasiado.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar {script}:\n{str(e)}")
            return False

    def iniciar_scraping(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        busqueda = self.entry_busqueda.get().strip()
        if not usuario or not password or not busqueda:
            messagebox.showwarning("Advertencia", "Completa todos los campos.")
            return
        guardar_credenciales(usuario, password, busqueda)
        if self.ejecutar_script("scraper.py"):
            self.mostrar_resultados_scraping()

    def iniciar_analisis(self):
        if self.ejecutar_script("analisis.py"):
            self.mostrar_graficos()

    def iniciar_post(self):
        if self.ejecutar_script("post.py"):
            self.mostrar_tweet_generado()


    def mostrar_resultados_scraping(self):
        self.limpiar_ventana()
        tk.Label(self.root, text="📊 Top 5 Tweets del Scraping", font=("Arial", 14, "bold")).pack(pady=10)

        try:
            df = pd.read_csv("tweets_api_puro.csv")
            df_top = df.head(5)
        except Exception as e:
            tk.Label(self.root, text=f"Error al cargar CSV: {e}", fg="red").pack(pady=20)
            tk.Button(self.root, text="Volver", command=self.crear_menu_inicio, bg="#9E9E9E", fg="white").pack(pady=10)
            return

        frame = tk.Frame(self.root)
        frame.pack(pady=5, padx=10, fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=("Tweet", "Likes", "Retweets"), show="headings")
        tree.heading("Tweet", text="Tweet")
        tree.heading("Likes", text="Likes")
        tree.heading("Retweets", text="Retweets")
        tree.column("Tweet", width=350)
        tree.column("Likes", width=70)
        tree.column("Retweets", width=70)

        for _, row in df_top.iterrows():
            texto = str(row["Texto"])[:60] + "..." if len(str(row["Texto"])) > 60 else str(row["Texto"])
            tree.insert("", "end", values=(texto, row["Likes"], row["Retweets"]))

        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        tk.Button(self.root, text="Volver al menú", command=self.crear_menu_inicio, bg="#9E9E9E", fg="white").pack(
            pady=15)

    def mostrar_graficos(self):
        self.limpiar_ventana()
        tk.Label(self.root, text="📈 Gráficos de Análisis", font=("Arial", 14, "bold")).pack(pady=10)
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        try:
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

            # Leer palabras clave
            with open("palabras_clave.txt", "r", encoding="utf-8") as f:
                palabras = [line.strip() for line in f if line.strip()][:10]

            fig = Figure(figsize=(9, 10), dpi=100)  # Altura aumentada para mejor visualización
            ax1 = fig.add_subplot(211)
            ax2 = fig.add_subplot(212)

            totals = {"Likes": df["Likes"].sum(), "Retweets": df["Retweets"].sum()}
            ax1.bar(totals.keys(), totals.values(), color=["#E53935", "#43A047"])
            ax1.set_title("Interacciones totales")
            ax1.set_ylabel("Cantidad")
            for i, v in enumerate(totals.values()):
                ax1.text(i, v + max(totals.values()) * 0.01, f'{int(v):,}', ha='center')

            if palabras:
                freq = list(range(len(palabras), 0, -1))
                ax2.barh(palabras[::-1], freq[::-1], color="#0077B6")
                ax2.set_title("Palabras clave (Top tweets)")
                ax2.set_xlabel("Frecuencia relativa")
            else:
                ax2.text(0.5, 0.5, "Sin palabras clave", ha='center', va='center')

            fig.tight_layout()

            canvas_fig = FigureCanvasTkAgg(fig, scrollable_frame)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(pady=10)

        except Exception as e:
            tk.Label(scrollable_frame, text=f"Error al generar gráficos: {e}", fg="red", wraplength=500).pack(pady=20)

        tk.Button(self.root, text="Volver al menú", command=self.crear_menu_inicio, bg="#9E9E9E", fg="white").pack(
            pady=10)

    def mostrar_tweet_generado(self):
        self.limpiar_ventana()
        tk.Label(self.root, text="🔥 Tweet Generado", font=("Arial", 14, "bold")).pack(pady=10)

        try:
            with open("tweet_proposal.txt", "r", encoding="utf-8") as f:
                tweet = f.read().strip()
        except Exception as e:
            tweet = f"Error al cargar el tweet: {e}"

        text_widget = tk.Text(self.root, height=6, width=70, wrap="word", font=("Arial", 12))
        text_widget.insert("1.0", tweet)
        text_widget.config(state="disabled")
        text_widget.pack(pady=10, padx=20)

        tk.Button(self.root, text="Volver al menú", command=self.crear_menu_inicio, bg="#9E9E9E", fg="white").pack(
            pady=15)


if __name__ == "__main__":
    root = tk.Tk()
    app = MenuApp(root)
    root.mainloop()