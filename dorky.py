# ================== BOOTSTRAP — solo stdlib, debe ir PRIMERO ===============
import sys
import subprocess

def _bootstrap():
    """Instala dependencias usando solo stdlib. Se ejecuta antes de cualquier import externo."""
    import importlib.util
    paquetes = [
        ('customtkinter', 'customtkinter'),
        ('PIL',           'Pillow'),
        ('requests',      'requests'),
    ]
    missing = [pip for mod, pip in paquetes
               if importlib.util.find_spec(mod) is None]

    if not missing:
        return

    import tkinter as _tk
    import tkinter.ttk as _ttk
    import threading

    win = _tk.Tk()
    win.title("Dorky — Instalando dependencias")
    win.geometry("460x130")
    win.resizable(False, False)
    win.configure(bg="#23272A")
    _tk.Label(win, text="Instalando dependencias, espera un momento…",
              bg="#23272A", fg="white", font=("Segoe UI", 11)).pack(pady=(22, 8))
    bar = _ttk.Progressbar(win, mode="indeterminate", length=380)
    bar.pack()
    bar.start(12)

    done = threading.Event()
    failed = []

    def instalar():
        for pkg in missing:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--quiet", pkg],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                failed.append(pkg)
        done.set()

    threading.Thread(target=instalar, daemon=True).start()

    while not done.is_set():
        win.update()
        done.wait(timeout=0.05)

    bar.stop()
    win.destroy()

    if failed:
        import tkinter.messagebox as _mb
        _mb.showerror(
            "Error de instalación",
            f"No se pudieron instalar los siguientes paquetes:\n\n"
            + "\n".join(f"  • {p}" for p in failed)
            + "\n\nEjecuta manualmente:\n"
            + f"  pip install {' '.join(failed)}"
        )
        sys.exit(1)

_bootstrap()

# ================== IMPORTS ================================
import os
import customtkinter as ctk
from tkinter import messagebox, Listbox, EXTENDED
import tkinter as tk
import requests
from urllib.parse import quote
import threading
import webbrowser
from datetime import datetime
from PIL import Image
import urllib.request
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================== APLICACIÓN ===============================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ResultadoBusqueda:
    def __init__(self, title, url, api_name, dork):
        self.title    = title
        self.url      = url
        self.api_name = api_name
        self.dork     = dork
        self.ts       = datetime.now().strftime("%H:%M:%S")


class Dorky(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dorky - Google Dorking")
        self.geometry("1550x930")
        self.minsize(1480, 830)

        self.scrapedo_token  = None
        self.scraperapi_key  = None
        self.all_dorks: dict = {}
        self.resultados: list[ResultadoBusqueda] = []

        self.mod_vars = {
            "site:":       ctk.BooleanVar(value=False),
            "inurl:":      ctk.BooleanVar(value=False),
            "allinurl:":   ctk.BooleanVar(value=False),
            "intext:":     ctk.BooleanVar(value=False),
            "allintext:":  ctk.BooleanVar(value=False),
            "intitle:":    ctk.BooleanVar(value=False),
            "allintitle:": ctk.BooleanVar(value=False),
            "filetype:":   ctk.BooleanVar(value=False),
            "cache:":      ctk.BooleanVar(value=False),
        }
        self._dorks_originales: list[str] = []
        self._cancel_event = threading.Event()

        self.cargar_dorks_desde_archivo()
        self.setup_ui()

    # ════════════════════════════════════════════════════════════════════════
    # CARGA DE DORKS
    # ════════════════════════════════════════════════════════════════════════
    def cargar_dorks_desde_archivo(self):
        dorks_path = os.path.join(BASE_DIR, "dorks.txt")
        try:
            with open(dorks_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró dorks.txt\n({dorks_path})")
            return
        current_cat = None
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("# === ") and line.endswith(" ==="):
                current_cat = line.replace("# === ", "").replace(" ===", "").strip()
                self.all_dorks[current_cat] = []
            elif line and not line.startswith("#") and current_cat:
                self.all_dorks[current_cat].append(line)

    # ════════════════════════════════════════════════════════════════════════
    # UI
    # ════════════════════════════════════════════════════════════════════════
    def setup_ui(self):

        # ── Toolbar ──────────────────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, height=70, fg_color="#2C2F33")
        toolbar.pack(fill="x", padx=12, pady=(12, 6))
        toolbar.pack_propagate(False)

        ctk.CTkLabel(toolbar, text="DORKY",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="#00ff9d").pack(side="left", padx=(25, 6))

        # Logo mascota junto al nombre
        try:
            logo_url = "https://i.ibb.co/q3RkZTV9/dorky.png"
            with urllib.request.urlopen(logo_url, timeout=5) as resp:
                img_data = resp.read()
            pil_img = Image.open(io.BytesIO(img_data)).resize((46, 46), Image.LANCZOS)
            self._logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(46, 46))
            ctk.CTkLabel(toolbar, image=self._logo_img, text="").pack(side="left", padx=(0, 20))
        except Exception:
            pass  # Sin red → se omite silenciosamente

        ctk.CTkLabel(toolbar, text="Categoría:",
                     font=ctk.CTkFont(size=14)).pack(side="left", padx=(40, 8))

        self.cat_var = ctk.StringVar(value="Seleccionar categoría")
        ctk.CTkOptionMenu(
            toolbar, variable=self.cat_var,
            values=["Seleccionar categoría"] + list(self.all_dorks.keys()),
            width=380, command=self.mostrar_dorks_de_categoria
        ).pack(side="left", padx=5)

        ctk.CTkButton(toolbar, text="🔑 APIs", fg_color="#7289DA", width=140,
                      command=self.mostrar_popup_apis).pack(side="right", padx=20)

        # ── Main ─────────────────────────────────────────────────────────────
        main = ctk.CTkFrame(self, fg_color="#36393F")
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # ── Panel izquierdo ───────────────────────────────────────────────────
        left = ctk.CTkFrame(main, width=360, fg_color="#2C2F33")
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        mod_frame = ctk.CTkFrame(left, fg_color="#23272A")
        mod_frame.pack(fill="x", padx=10, pady=13)
        ctk.CTkLabel(mod_frame,
                     text="Modificadores (se aplican / quitan de todos los dorks):",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=16, pady=(2, 6))

        mods = list(self.mod_vars.keys())
        for fila in range(3):
            row_f = ctk.CTkFrame(mod_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=10, pady=2)
            for col in range(3):
                i = fila * 3 + col
                if i < len(mods):
                    mod = mods[i]
                    ctk.CTkCheckBox(row_f, text=mod, variable=self.mod_vars[mod],
                                   font=ctk.CTkFont(size=11), width=90,
                                   command=lambda m=mod: self.on_modificador(m)
                                   ).pack(side="left", padx=4)

        self.dorks_listbox = Listbox(
            left, selectmode=EXTENDED, bg="#2C2F33", fg="white",
            font=("Consolas", 11), selectbackground="#7289DA", activestyle="none")
        sb = ctk.CTkScrollbar(left, command=self.dorks_listbox.yview)
        self.dorks_listbox.configure(yscrollcommand=sb.set)
        self.dorks_listbox.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=8)
        sb.pack(side="right", fill="y", padx=(0, 12), pady=8)
        self.dorks_listbox.bind("<ButtonRelease-1>", self.agregar_por_clic)

        # ── Panel derecho ─────────────────────────────────────────────────────
        right = ctk.CTkFrame(main, fg_color="#36393F")
        right.pack(side="right", fill="both", expand=True)

        # Fila: "Dorks a buscar (editable)"  
        dorks_header = ctk.CTkFrame(right, fg_color="transparent")
        dorks_header.pack(fill="x", padx=15, pady=(12, 2))

        ctk.CTkLabel(dorks_header, text="Dorks a buscar (editable)",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")

        gh_label = ctk.CTkLabel(
            dorks_header, text="⭐ Github",
            font=ctk.CTkFont(size=12),
            text_color="#5dade2", cursor="hand2")
        gh_label.pack(side="right", padx=(0, 2))
        gh_label.bind("<Button-1>",
                      lambda e: webbrowser.open("https://github.com/aisurf3r/Dorky"))
        gh_label.bind("<Enter>", lambda e: gh_label.configure(text_color="#aed6f1"))
        gh_label.bind("<Leave>", lambda e: gh_label.configure(text_color="#5dade2"))

        self.dorks_text = ctk.CTkTextbox(right, height=170, font=("Consolas", 12))
        self.dorks_text.pack(fill="x", padx=15, pady=(0, 5))

        # Fila de botones
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(btn_frame, text="Buscar con scrape.do", fg_color="#43B581", height=42,
                      command=lambda: self.iniciar_busqueda("scrapedo")).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btn_frame, text="Buscar con ScraperAPI", fg_color="#FAA61A", height=42,
                      command=lambda: self.iniciar_busqueda("scraperapi")).pack(side="left", padx=6)

        ctk.CTkLabel(btn_frame, text="Resultados:",
                     font=ctk.CTkFont(size=13)).pack(side="left", padx=(16, 4))
        self.num_results_var = ctk.StringVar(value="10")
        ctk.CTkOptionMenu(
            btn_frame, variable=self.num_results_var,
            values=["10", "15", "20", "25", "30"],
            width=80
        ).pack(side="left")

        ctk.CTkButton(btn_frame, text="Limpiar todo", fg_color="#F04747", height=42, width=130,
                      command=self.limpiar_todo).pack(side="right")
        ctk.CTkButton(btn_frame, text="⏹ Cancelar búsqueda", fg_color="#555555", height=42, width=160,
                      command=self.cancelar_busqueda).pack(side="right", padx=(0, 6))

        # Cabecera resultados
        res_header = ctk.CTkFrame(right, fg_color="transparent")
        res_header.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(res_header, text="Resultados en tiempo real",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#00ff9d").pack(side="left")
        ctk.CTkButton(res_header, text="📋 Exportar URLs", fg_color="#23272A",
                      border_width=1, border_color="#00ff9d", height=32, width=130,
                      command=self.exportar_urls).pack(side="right")

        # Área de resultados — tk.Text + CTkScrollbar
        res_frame = ctk.CTkFrame(right, fg_color="transparent")
        res_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        res_sb = ctk.CTkScrollbar(res_frame, fg_color="#1a1a1a", button_color="#1a1a1a",
                                   button_hover_color="#333")
        res_sb.pack(side="right", fill="y")

        self.results_text = tk.Text(
            res_frame, bg="#2C2F33", fg="white",
            font=("Consolas", 11), wrap="word",
            cursor="arrow", bd=0, highlightthickness=0,
            yscrollcommand=res_sb.set)
        self.results_text.pack(side="left", fill="both", expand=True)
        res_sb.configure(command=self.results_text.yview)

        for tag, color in [
            ("success", "#00ff9d"), ("error", "#ff5555"),
            ("api",     "#7289DA"), ("info",  "white"),
        ]:
            self.results_text.tag_config(tag, foreground=color)

        self.results_text.configure(state="disabled")

    # ════════════════════════════════════════════════════════════════════════
    # DORKS
    # ════════════════════════════════════════════════════════════════════════
    def mostrar_dorks_de_categoria(self, cat):
        if cat == "Seleccionar categoría":
            return
        self.dorks_listbox.delete(0, "end")
        for dork in self.all_dorks.get(cat, []):
            self.dorks_listbox.insert("end", dork)

    def agregar_por_clic(self, event=None):
        try:
            idx  = self.dorks_listbox.curselection()[0]
            dork = self.dorks_listbox.get(idx)
            self.agregar_dork(dork)
        except Exception:
            pass

    def agregar_dork(self, dork):
        if not dork:
            return
        if dork not in self._dorks_originales:
            self._dorks_originales.append(dork)
            self.aplicar_modificadores_a_todos()
            self.log_result(f"✓ Agregado: {dork[:75]}", "success")

    def on_modificador(self, mod):
        # Resincronizar por si el usuario editó el textbox a mano
        prefijo_actual = "".join(m for m, var in self.mod_vars.items() if var.get() and m != mod)
        self._dorks_originales = [
            l.replace(prefijo_actual, "", 1)
            for l in self.dorks_text.get("1.0", "end").splitlines()
            if l.strip()
        ]
        marcado = self.mod_vars[mod].get()
        if self._dorks_originales:
            if marcado:
                cursor_col = int(self.dorks_text.index("insert").split(".")[1])
                lineas = self.dorks_text.get("1.0", "end").splitlines()
                nuevas = []
                for linea in lineas:
                    col = min(cursor_col, len(linea))
                    nuevas.append(linea[:col] + mod + linea[col:])
                self.dorks_text.delete("1.0", "end")
                self.dorks_text.insert("1.0", "\n".join(nuevas))
            else:
                lineas = self.dorks_text.get("1.0", "end").splitlines()
                nuevas = [l.replace(mod, "", 1) for l in lineas]
                self.dorks_text.delete("1.0", "end")
                self.dorks_text.insert("1.0", "\n".join(nuevas))
        else:
            if marcado:
                self.dorks_text.insert("insert", mod)
                self.dorks_text.focus_set()
            else:
                cursor = self.dorks_text.index("insert")
                row    = cursor.split(".")[0]
                linea  = self.dorks_text.get(f"{row}.0", f"{row}.end")
                nueva  = linea.replace(mod, "", 1)
                self.dorks_text.delete(f"{row}.0", f"{row}.end")
                self.dorks_text.insert(f"{row}.0", nueva)

    def aplicar_modificadores_a_todos(self):
        prefijo   = "".join(m for m, var in self.mod_vars.items() if var.get())
        new_lines = [prefijo + orig for orig in self._dorks_originales]
        self.dorks_text.delete("1.0", "end")
        self.dorks_text.insert("1.0", "\n".join(new_lines))

    # ════════════════════════════════════════════════════════════════════════
    # APIS
    # ════════════════════════════════════════════════════════════════════════
    def mostrar_popup_apis(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Configurar API Keys")
        popup.geometry("520x380")
        popup.grab_set()
        ctk.CTkLabel(popup, text="API Keys",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkLabel(popup, text="scrape.do Token:").pack(anchor="w", padx=50)
        self.entry_scrapedo = ctk.CTkEntry(popup, width=420)
        self.entry_scrapedo.pack(pady=8, padx=50)
        if self.scrapedo_token:
            self.entry_scrapedo.insert(0, self.scrapedo_token)
        ctk.CTkLabel(popup, text="ScraperAPI Key:").pack(anchor="w", padx=50, pady=(15, 0))
        self.entry_scraperapi = ctk.CTkEntry(popup, width=420)
        self.entry_scraperapi.pack(pady=8, padx=50)
        if self.scraperapi_key:
            self.entry_scraperapi.insert(0, self.scraperapi_key)
        ctk.CTkButton(popup, text="Guardar y Cerrar",
                      fg_color="#00ff9d", text_color="black", height=40,
                      command=lambda: self.guardar_apis(popup)).pack(pady=30)

    def guardar_apis(self, popup):
        self.scrapedo_token = self.entry_scrapedo.get().strip()
        self.scraperapi_key = self.entry_scraperapi.get().strip()
        messagebox.showinfo("Guardado", "API Keys guardadas correctamente")
        popup.destroy()

    # ════════════════════════════════════════════════════════════════════════
    # BÚSQUEDA
    # ════════════════════════════════════════════════════════════════════════
    def iniciar_busqueda(self, modo):
        texto = self.dorks_text.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Sin dorks", "Agrega al menos un dork")
            return
        dorks = [line.strip() for line in texto.splitlines() if line.strip()]

        if modo == "scrapedo" and not self.scrapedo_token:
            messagebox.showerror("API faltante", "Falta clave de scrape.do")
            return
        if modo == "scraperapi" and not self.scraperapi_key:
            messagebox.showerror("API faltante", "Falta clave de ScraperAPI")
            return

        self.log_result("\n" + "═" * 90, "info")
        self.log_result(
            f"🚀 Iniciando búsqueda — {len(dorks)} dork(s) · "
            f"{self.num_results_var.get()} resultados/dork", "success")

        self._cancel_event.clear()
        threading.Thread(target=self.procesar_api, args=(modo, dorks), daemon=True).start()

    def procesar_api(self, api_name, dorks):
        import time
        num = int(self.num_results_var.get())
        PAGE_SIZE = 10
        paginas   = (num + PAGE_SIZE - 1) // PAGE_SIZE

        for i, dork in enumerate(dorks, 1):
            if self._cancel_event.is_set():
                break
            self.log_result(f"[{i}/{len(dorks)}] {api_name.upper()} → {dork[:72]}", "info")
            urls_vistas = set()
            total_obtenidos = 0

            for pagina in range(paginas):
                if self._cancel_event.is_set() or total_obtenidos >= num:
                    break
                try:
                    if api_name == "scrapedo":
                        start = pagina * PAGE_SIZE
                        url = (
                            f"https://api.scrape.do/plugin/google/search"
                            f"?token={self.scrapedo_token}"
                            f"&q={quote(dork)}&num={PAGE_SIZE}&start={start}&gl=es&hl=es"
                        )
                        r       = requests.get(url, timeout=35)
                        results = r.json().get("organic_results", [])
                    else:
                        params = {
                            "api_key": self.scraperapi_key,
                            "query": dork, "country": "es",
                            "num": PAGE_SIZE, "page": pagina + 1
                        }
                        r       = requests.get(
                            "https://api.scraperapi.com/structured/google/search",
                            params=params, timeout=35)
                        results = r.json().get("organic_results", [])

                    nuevos = 0
                    for item in results:
                        if total_obtenidos >= num:
                            break
                        link  = item.get('link', '')
                        if not link or link in urls_vistas:
                            continue
                        urls_vistas.add(link)
                        title = item.get('title', '(sin título)')[:70]
                        self.resultados.append(ResultadoBusqueda(title, link, api_name, dork))
                        self.log_result_url(f"      • {title}", link)
                        total_obtenidos += 1
                        nuevos += 1

                    if paginas > 1:
                        self.log_result(
                            f"   → Página {pagina+1}/{paginas}: {nuevos} nuevos "
                            f"({total_obtenidos}/{num} total)", "success")

                    if not results or nuevos == 0:
                        break

                except Exception as e:
                    self.log_result(f"   ❌ Error {api_name} p.{pagina+1}: {str(e)[:90]}", "error")
                    break

                if pagina < paginas - 1:
                    if self._cancel_event.is_set():
                        break
                    time.sleep(1.6)

            if paginas == 1:
                self.log_result(f"   → {total_obtenidos} resultados", "success")
            if self._cancel_event.is_set():
                break
            time.sleep(1.6)

        if self._cancel_event.is_set():
            self.log_result("⏹ Búsqueda cancelada por el usuario.", "error")
        else:
            self.log_result(f"✅ Finalizada búsqueda con {api_name.upper()}", "success")

    # ════════════════════════════════════════════════════════════════════════
    # LOG
    # ════════════════════════════════════════════════════════════════════════
    def log_result(self, mensaje, tipo="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        def insertar():
            self.results_text.configure(state="normal")
            self.results_text.insert("end", f"[{ts}] {mensaje}\n", tipo)
            self.results_text.see("end")
            self.results_text.configure(state="disabled")
        self.after(0, insertar)

    def log_result_url(self, titulo_texto: str, url: str):
        ts = datetime.now().strftime("%H:%M:%S")
        def insertar():
            self.results_text.configure(state="normal")
            self.results_text.insert("end", f"[{ts}] ", "info")
            tag_id = f"lnk_{id(url)}_{ts.replace(':','')}"
            self.results_text.tag_config(tag_id, foreground="#5dade2", underline=True)
            self.results_text.tag_bind(tag_id, "<Button-1>",
                                       lambda e, u=url: webbrowser.open(u))
            self.results_text.tag_bind(tag_id, "<Enter>",
                                       lambda e: self.results_text.configure(cursor="hand2"))
            self.results_text.tag_bind(tag_id, "<Leave>",
                                       lambda e: self.results_text.configure(cursor="arrow"))
            self.results_text.insert("end", titulo_texto, (tag_id,))
            self.results_text.insert("end", f"\n             {url[:90]}\n", "api")
            self.results_text.see("end")
            self.results_text.configure(state="disabled")
        self.after(0, insertar)

    # ════════════════════════════════════════════════════════════════════════
    # EXPORTAR / LIMPIAR
    # ════════════════════════════════════════════════════════════════════════
    def cancelar_busqueda(self):
        self._cancel_event.set()

    def exportar_urls(self):
        if not self.resultados:
            messagebox.showinfo("Sin resultados", "No hay URLs para exportar todavía.")
            return
        try:
            ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = os.path.join(BASE_DIR, f"resultados_{ts}.txt")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(f"# Dorky — Exportado: {ts}\n")
                f.write(f"# Total: {len(self.resultados)} URLs\n\n")
                for res in self.resultados:
                    f.write(f"[{res.ts}] [{res.api_name.upper()}] {res.dork}\n")
                    f.write(f"  Título: {res.title}\n  URL:    {res.url}\n\n")
            self.log_result(f"📁 Exportado: {fname}", "success")
            messagebox.showinfo("Exportado", f"✅ {len(self.resultados)} URLs guardadas en:\n{fname}")
        except Exception as e:
            self.log_result(f"❌ Error al exportar: {str(e)}", "error")
            messagebox.showerror("Error al exportar", str(e))

    def limpiar_todo(self):
        self.dorks_text.delete("1.0", "end")
        self._dorks_originales.clear()
        self.resultados.clear()
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.configure(state="disabled")
        for var in self.mod_vars.values():
            var.set(False)
        self.log_result("🧹 Panel limpiado", "success")


if __name__ == "__main__":
    app = Dorky()
    app.mainloop()
