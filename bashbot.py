import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import os
import sys
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore
import importlib.util
import threading

init()

HISTORIAL_FILE = "history.txt"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def cargar_comandos():
    try:
        file_path = resource_path("comandos_comunes.py")
        spec = importlib.util.spec_from_file_location("comandos_comunes", file_path)
        if spec is None:
            print("Error: No se encontró el archivo comandos_comunes.py")
            return {}
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        if hasattr(modulo, 'comandos_comunes'):
            return modulo.comandos_comunes
        else:
            print("Error: comandos_comunes.py no contiene una variable 'comandos_comunes'.")
            return {}
    except Exception as e:
        print(f"Error al cargar comandos_comunes.py: {str(e)}")
        return {}

def guardar_historial(pregunta, respuesta, fuente="Local"):
    try:
        with open(resource_path(HISTORIAL_FILE), 'a', encoding='utf-8') as file:
            file.write(f"Pregunta: {pregunta}\nRespuesta: {respuesta}\nFuente: {fuente}\n---\n")
    except Exception as e:
        print(f"Error al guardar historial: {str(e)}")

def buscar_web(consulta):
    query = f"{consulta} comando bash linux ejemplo"
    resultados = []
    try:
        for url in search(query, num_results=3):
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            parrafos = soup.find_all('p')
            for p in parrafos:
                if consulta.lower() in p.text.lower():
                    resultados.append(p.text.strip())
            if resultados:
                break
    except Exception as e:
        return f"Error en la búsqueda web: {str(e)}"
    return resultados[0] if resultados else "No se encontraron resultados en la web."

class BashBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BashBot")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        self.comandos = cargar_comandos()
        self.is_searching = False
        self.gif_frames = []
        self.current_frame = 0
        self.is_dark_theme = True
        self.text_opacity = 0.0
        self.tooltip = None

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, font=("Helvetica", 10, "bold"), background="#3C3F41", foreground="#00B7EB")
        self.style.map("TButton", background=[("active", "#4CAF50")], foreground=[("active", "#00B7EB")])
        self.style.configure("TLabel", font=("Helvetica", 12, "bold"))
        self.bg_color = "#2E2E2E"
        self.fg_color = "#FFFFFF"
        self.text_bg = "#3C3F41"
        self.root.configure(bg=self.bg_color)

        try:
            self.load_gif(resource_path("loading.gif"))
            self.search_icon = ImageTk.PhotoImage(Image.open(resource_path("search.png")).resize((20, 20)))
            self.history_icon = ImageTk.PhotoImage(Image.open(resource_path("history.png")).resize((20, 20)))
            self.exit_icon = ImageTk.PhotoImage(Image.open(resource_path("x.png")).resize((20, 20)))
            self.clear_icon = ImageTk.PhotoImage(Image.open(resource_path("clean.png")).resize((20, 20)))
            self.sun_icon = ImageTk.PhotoImage(Image.open(resource_path("sun.png")).resize((20, 20)))
            self.moon_icon = ImageTk.PhotoImage(Image.open(resource_path("moon.png")).resize((20, 20)))
            self.info_icon = ImageTk.PhotoImage(Image.open(resource_path("info.png")).resize((20, 20)))
        except Exception as e:
            print(f"Error al cargar imágenes: {str(e)}")
            self.search_icon = None
            self.history_icon = None
            self.exit_icon = None
            self.clear_icon = None
            self.sun_icon = None
            self.moon_icon = None
            self.info_icon = None

        self.main_frame = ttk.Frame(self.root, padding=10, style="Main.TFrame")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.style.configure("Main.TFrame", background=self.bg_color)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Barra superior
        self.toolbar_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.toolbar_frame.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.style.configure("Main.TFrame", background=self.bg_color)

        self.boton_salir = ttk.Button(self.toolbar_frame, text=" ", image=self.exit_icon, compound="left", command=self.root.quit)
        self.boton_salir.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.boton_salir.bind("<Enter>", lambda e: [self.boton_salir.configure(style="Hover.TButton"), self.show_tooltip(e, "Cerrar la aplicación")])
        self.boton_salir.bind("<Leave>", lambda e: [self.boton_salir.configure(style="TButton"), self.hide_tooltip()])
        self.boton_info = ttk.Button(self.toolbar_frame, text=" ", image=self.info_icon, compound="left", command=self.mostrar_info)
        self.boton_info.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.boton_info.bind("<Enter>", lambda e: [self.boton_info.configure(style="Hover.TButton"), self.show_tooltip(e, "Información sobre BashBot")])
        self.boton_info.bind("<Leave>", lambda e: [self.boton_info.configure(style="TButton"), self.hide_tooltip()])
        self.boton_tema = ttk.Button(self.toolbar_frame, text=" ", image=self.moon_icon, compound="left", command=self.toggle_theme)
        self.boton_tema.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.boton_tema.bind("<Enter>", lambda e: [self.boton_tema.configure(style="Hover.TButton"), self.show_tooltip(e, "Alternar tema claro/oscuro")])
        self.boton_tema.bind("<Leave>", lambda e: [self.boton_tema.configure(style="TButton"), self.hide_tooltip()])

        self.label = ttk.Label(self.main_frame, text="Ingresa tu consulta:", foreground="#00B7EB")
        self.label.grid(row=1, column=0, columnspan=4, pady=10, sticky="w")
        self.entrada = ttk.Combobox(self.main_frame, width=47, font=("Helvetica", 11), values=list(self.comandos.keys()))
        self.entrada.grid(row=2, column=0, columnspan=4, pady=5, padx=5, sticky="ew")
        self.entrada.bind("<Return>", lambda event: self.iniciar_busqueda())
        self.entrada.bind("<KeyRelease>", self.actualizar_autocompletado)
        self.entrada.bind("<Control-l>", lambda event: self.limpiar_entrada())

        self.boton_buscar = ttk.Button(self.main_frame, text=" Buscar", image=self.search_icon, compound="left", command=self.iniciar_busqueda)
        self.boton_buscar.grid(row=3, column=0, pady=10, sticky="w")
        self.boton_buscar.bind("<Enter>", lambda e: [self.boton_buscar.configure(style="Hover.TButton"), self.show_tooltip(e, "Buscar comando")])
        self.boton_buscar.bind("<Leave>", lambda e: [self.boton_buscar.configure(style="TButton"), self.hide_tooltip()])
        self.boton_limpiar = ttk.Button(self.main_frame, text=" Limpiar", image=self.clear_icon, compound="left", command=self.limpiar_entrada)
        self.boton_limpiar.grid(row=3, column=1, pady=10, sticky="e")
        self.boton_limpiar.bind("<Enter>", lambda e: [self.boton_limpiar.configure(style="Hover.TButton"), self.show_tooltip(e, "Limpiar entrada y resultados")])
        self.boton_limpiar.bind("<Leave>", lambda e: [self.boton_limpiar.configure(style="TButton"), self.hide_tooltip()])
        self.style.configure("Hover.TButton", background="#4CAF50", foreground="#00B7EB")

        self.loading_label = ttk.Label(self.main_frame, background=self.bg_color)
        self.loading_label.grid(row=4, column=0, columnspan=4, pady=5)
        self.loading_text = ttk.Label(self.main_frame, text="", foreground="#00FF00", background=self.bg_color)
        self.loading_text.grid(row=5, column=0, columnspan=4)

        self.resultado_texto = scrolledtext.ScrolledText(self.main_frame, height=12, width=70, wrap=tk.WORD, font=("Helvetica", 10), bg=self.text_bg, fg=self.fg_color)
        self.resultado_texto.grid(row=6, column=0, columnspan=4, pady=10, padx=5, sticky="nsew")
        self.resultado_texto.config(state='disabled')

        self.boton_historial = ttk.Button(self.main_frame, text=" Ver Historial", image=self.history_icon, compound="left", command=self.ver_historial)
        self.boton_historial.grid(row=7, column=0, pady=10, sticky="w")
        self.boton_historial.bind("<Enter>", lambda e: [self.boton_historial.configure(style="Hover.TButton"), self.show_tooltip(e, "Ver historial de consultas")])
        self.boton_historial.bind("<Leave>", lambda e: [self.boton_historial.configure(style="TButton"), self.hide_tooltip()])

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.columnconfigure(3, weight=1)
        self.main_frame.rowconfigure(6, weight=1)

        self.resultado_texto.tag_configure("pregunta", foreground="#00B7EB")
        self.resultado_texto.tag_configure("respuesta", foreground="#00FF00")
        self.resultado_texto.tag_configure("fuente", foreground="#FFFFFF")

        if not self.comandos:
            messagebox.showwarning("Advertencia", "No se pudieron cargar los comandos locales. Solo se realizarán búsquedas web.")

    def load_gif(self, gif_path):
        try:
            img = Image.open(gif_path)
            self.gif_frames = []
            while True:
                try:
                    frame = ImageTk.PhotoImage(img.copy())
                    self.gif_frames.append(frame)
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
        except Exception as e:
            print(f"Error al cargar GIF: {str(e)}")

    def animate_gif(self):
        if self.is_searching and self.gif_frames:
            self.loading_label.configure(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.root.after(100, self.animate_gif)

    def fade_in_text(self):
        if self.text_opacity < 1.0:
            self.text_opacity += 0.1
            self.resultado_texto.tag_configure("fade", foreground=f"#{int(self.text_opacity * 255):02x}{int(self.text_opacity * 255):02x}{int(self.text_opacity * 255):02x}")
            self.root.after(50, self.fade_in_text)

    def show_tooltip(self, event, text):
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = tk.Label(self.tooltip, text=text, background="#FFFF99", foreground="#000000", relief="solid", borderwidth=1, font=("Helvetica", 8))
        label.pack()

    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def actualizar_autocompletado(self, event):
        texto = self.entrada.get().lower()
        if texto:
            sugerencias = [cmd for cmd in self.comandos.keys() if texto in cmd.lower()]
            self.entrada['values'] = sugerencias
        else:
            self.entrada['values'] = list(self.comandos.keys())

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.bg_color = "#FFFFFF" if not self.is_dark_theme else "#2E2E2E"
        self.fg_color = "#000000" if not self.is_dark_theme else "#FFFFFF"
        self.text_bg = "#F5F5F5" if not self.is_dark_theme else "#3C3F41"
        button_bg = "#E0E0E0" if not self.is_dark_theme else "#3C3F41"
        self.style.configure("TButton", background=button_bg, foreground="#00B7EB")
        self.style.map("TButton", background=[("active", "#4CAF50")], foreground=[("active", "#00B7EB")])
        self.style.configure("Hover.TButton", background="#4CAF50", foreground="#00B7EB")
        self.root.configure(bg=self.bg_color)
        self.main_frame.configure(style="Main.TFrame")
        self.style.configure("Main.TFrame", background=self.bg_color)
        self.loading_label.configure(background=self.bg_color)
        self.loading_text.configure(background=self.bg_color)
        self.resultado_texto.configure(bg=self.text_bg, fg=self.fg_color)
        self.label.configure(background=self.bg_color)
        self.boton_tema.configure(image=self.sun_icon if not self.is_dark_theme else self.moon_icon)

    def iniciar_busqueda(self):
        if self.is_searching:
            return
        consulta = self.entrada.get().strip()
        if not consulta:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una consulta.")
            return

        self.is_searching = True
        self.boton_buscar.state(['disabled'])
        self.loading_text.configure(text="Procesando...")
        if self.gif_frames:
            self.animate_gif()

        threading.Thread(target=self.buscar, args=(consulta,), daemon=True).start()

    def buscar(self, consulta):
        self.resultado_texto.config(state='normal')
        self.resultado_texto.delete(1.0, tk.END)
        self.text_opacity = 0.0

        respuesta = None
        fuente = "Local"
        for comando, descripcion in self.comandos.items():
            if consulta.lower() in comando.lower():
                respuesta = descripcion
                break

        if not respuesta:
            fuente = "Web"
            respuesta = buscar_web(consulta)

        self.resultado_texto.insert(tk.END, f"Pregunta: {consulta}\n", "pregunta")
        self.resultado_texto.insert(tk.END, f"Respuesta: {respuesta}\n", "respuesta")
        self.resultado_texto.insert(tk.END, f"Fuente: {fuente}\n", "fuente")
        self.resultado_texto.config(state='disabled')
        self.fade_in_text()

        guardar_historial(consulta, respuesta, fuente)

        self.is_searching = False
        self.boton_buscar.state(['!disabled'])
        self.loading_text.configure(text="")
        self.loading_label.configure(image="")

    def limpiar_entrada(self):
        self.entrada.delete(0, tk.END)
        self.entrada['values'] = list(self.comandos.keys())
        self.resultado_texto.config(state='normal')
        self.resultado_texto.delete(1.0, tk.END)
        self.resultado_texto.config(state='disabled')

    def ver_historial(self):
        if not os.path.exists(resource_path(HISTORIAL_FILE)):
            messagebox.showinfo("Historial", "No hay historial disponible.")
            return

        historial_ventana = tk.Toplevel(self.root)
        historial_ventana.title("Historial de Consultas")
        historial_ventana.geometry("600x400")
        historial_ventana.configure(bg=self.bg_color)

        texto_historial = scrolledtext.ScrolledText(historial_ventana, height=15, width=70, wrap=tk.WORD, font=("Helvetica", 10), bg=self.text_bg, fg=self.fg_color)
        texto_historial.pack(pady=10, padx=10, fill="both", expand=True)

        with open(resource_path(HISTORIAL_FILE), 'r', encoding='utf-8') as file:
            contenido = file.read()
            texto_historial.insert(tk.END, contenido)
        texto_historial.config(state='disabled')

    def mostrar_info(self):
        info_ventana = tk.Toplevel(self.root)
        info_ventana.title("Acerca de BashBot")
        info_ventana.geometry("400x300")
        info_ventana.configure(bg=self.bg_color)

        texto_info = scrolledtext.ScrolledText(info_ventana, height=15, width=40, wrap=tk.WORD, font=("Helvetica", 10), bg=self.text_bg, fg=self.fg_color)
        texto_info.pack(pady=10, padx=10, fill="both", expand=True)

        info_text = (
            f"Autor: Vazkyer\n\n"
            f"Descripción: BashBot es un asistente interactivo para la terminal que ayuda con comandos de Bash y conceptos de Linux. Utiliza un diccionario local de comandos y búsquedas web para proporcionar respuestas rápidas y útiles.\n\n"
            f"Atajos:\n"
            f"- <Enter>: Iniciar búsqueda\n"
            f"- <Ctrl+l>: Limpiar entrada y resultados\n"
        )
        texto_info.insert(tk.END, info_text)
        texto_info.config(state='disabled')

        boton_cerrar = ttk.Button(info_ventana, text=" Cerrar", command=info_ventana.destroy)
        boton_cerrar.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = BashBotGUI(root)
    root.mainloop()
