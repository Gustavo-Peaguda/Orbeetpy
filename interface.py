import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import base64
import io

try:
    from PIL import Image, ImageTk, ImageFilter, ImageDraw

    PIL_OK = True
except ImportError:
    PIL_OK = False

from orbeet import (
    carregar_dados, salvar_dados,
    autenticar_usuario, criar_usuario,
    criar_fazenda, editar_fazenda, excluir_fazenda,
    fazendas_do_usuario, registrar_recomendacao,
    buscar_previsao_completa, buscar_historico_completo,
    calcular_irrp, irrp_color_hex,
    busca_binaria_recursiva,
    gerar_recomendacao_openai,
)


#  LOGO BASE

LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAYAAAA5ZDbSAAABCGlDQ1BJQ0MgUHJvZmlsZQAAeJxjYGA8wQAELAYMDLl5JUVB7k4KEZFRCuwPGBiBEAwSk4sLGHADoKpv1yBqL+viUYcLcKakFicD6Q9ArFIEtBxopAiQLZIOYWuA2EkQtg2IXV5SUAJkB4DYRSFBzkB2CpCtkY7ETkJiJxcUgdT3ANk2uTmlyQh3M/Ck5oUGA2kOIJZhKGYIYnBncAL5H6IkfxEDg8VXBgbmCQixpJkMDNtbGRgkbiHEVBYwMPC3MDBsO48QQ4RJQWJRIliIBYiZ0tIYGD4tZ2DgjWRgEL7AwMAVDQsIHG5TALvNnSEfCNMZchhSgSKeDHkMyQx6QJYRgwGDIYMZAKbWPz9HbOBQAAAheElEQVR4nO2dd3Qd1bX/v/ucmdvVe7Fk2XIvuOECxNfGxqYTINfvGQIESCgxhPJ4eYT38ruWQ4AEQsgKoQVCKKFISYiBmGrLxrbAvRfcu2VLliVd3TozZ/34I5YkaebOPWdGWmvvvZbmnjNzzpzzm7MFGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbGxsbm2OhfvUDNt8cCgQCciLnAHQ8JzrhebZJOqK1wWDQI4T83O9tTl1o+PDhOgA6//zzo2eeeeZHzAyOCo8A4JprrskaOnTou8OHD58+YsSI2jFjxkxIne9STbbNyJfDy5YtMwB47969a+vr68cTEQPQkGwf8vv9mcuWLXtHSrl25MiR3wXw380NDX+65JJLCgAoSuseSSC0Uo8ACKRnBNIGJIbJAYBisFNkIqmKd5cSSbWz8m3ZolQU7K+JtB5K7E+oT7JNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yTbJNsk2yfJ/c3p6WPGZRWQAAAAASUVORK5CYII="


#  PALETA DE CORES
C = {
    # Fundos
    "bg": "#0D0A00",
    "bg2": "#161000",
    "bg3": "#1E1600",
    "bg4": "#252000",
    "panel": "#1A1400",
    # Bordas e separadores
    "border": "#2E2200",
    "border2": "#3D3000",
    # Âmbar / dourado
    "gold": "#F5A623",
    "gold2": "#FFB83F",
    "amber": "#D4820A",
    "amber_dark": "#8B5A00",
    "honey": "#E8960F",
    # Texto
    "text": "#F5EDD0",
    "text2": "#C8B88A",
    "muted": "#7A6040",
    "muted2": "#554030",
    # Status
    "green": "#3DBA5F",
    "green_dark": "#1A5C2A",
    "yellow": "#F5C542",
    "yellow_dark": "#7A6200",
    "red": "#E84040",
    "red_dark": "#5C1A1A",
    # Entry
    "entry_bg": "#120E00",
    "entry_fg": "#F5EDD0",
    # Faixas IRRP
    "band_alto": "#2A0A00",
    "band_mod": "#1E1A00",
    "band_low": "#0A1200",
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 13, "bold"),
    "section": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 9),
    "body_bold": ("Segoe UI", 9, "bold"),
    "small": ("Segoe UI", 8),
    "mono": ("Consolas", 9),
    "nav": ("Segoe UI", 10),
    "metric": ("Segoe UI", 28, "bold"),
    "metric_sm": ("Segoe UI", 18, "bold"),
    "badge": ("Segoe UI", 7, "bold"),
}



def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t), int(b1 + (b2 - b1) * t)
    )


class HoverButton(tk.Button):
    """Botão com animação de hover suave."""

    def __init__(self, parent, bg_normal, bg_hover, fg_normal=None, fg_hover=None, **kw):
        self._bg_n = bg_normal
        self._bg_h = bg_hover
        self._fg_n = fg_normal or C["text"]
        self._fg_h = fg_hover or C["text"]
        super().__init__(parent,
                         bg=bg_normal, fg=self._fg_n,
                         activebackground=bg_hover,
                         activeforeground=self._fg_h,
                         relief="flat", cursor="hand2", **kw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        self.config(bg=self._bg_h, fg=self._fg_h)

    def _on_leave(self, _):
        self.config(bg=self._bg_n, fg=self._fg_n)


def make_btn_primary(parent, text, command, width=18, **kw):
    return HoverButton(parent, C["gold"], C["gold2"],
                       fg_normal=C["bg"], fg_hover=C["bg"],
                       text=text, command=command,
                       font=FONTS["body_bold"],
                       width=width, pady=7, padx=4, **kw)


def make_btn_secondary(parent, text, command, width=18, **kw):
    return HoverButton(parent, C["bg4"], C["bg3"],
                       fg_normal=C["text2"], fg_hover=C["gold"],
                       text=text, command=command,
                       font=FONTS["body"],
                       width=width, pady=7, padx=4, **kw)


def make_btn_danger(parent, text, command, width=18, **kw):
    return HoverButton(parent, C["red_dark"], C["red"],
                       fg_normal=C["text2"], fg_hover=C["text"],
                       text=text, command=command,
                       font=FONTS["body"],
                       width=width, pady=7, padx=4, **kw)


def make_entry(parent, textvariable, show=None, width=28, **kw):
    e = tk.Entry(parent, textvariable=textvariable,
                 bg=C["entry_bg"], fg=C["entry_fg"],
                 insertbackground=C["gold"],
                 selectbackground=C["amber_dark"],
                 relief="flat", font=FONTS["body"],
                 width=width, show=show or "", **kw)
    # Borda decorativa via Frame
    return e


def make_label(parent, text, font=None, fg=None, bg=None, **kw):
    return tk.Label(parent, text=text,
                    font=font or FONTS["body"],
                    fg=fg or C["text"],
                    bg=bg or C["bg"],
                    **kw)


def section_header(parent, icon, title, bg=None):
    bg = bg or C["bg"]
    row = tk.Frame(parent, bg=bg)
    row.pack(fill="x", pady=(16, 6))
    tk.Label(row, text=icon, font=("Segoe UI Emoji", 12),
             bg=bg, fg=C["gold"]).pack(side="left", padx=(0, 6))
    tk.Label(row, text=title, font=FONTS["section"],
             bg=bg, fg=C["gold"]).pack(side="left")
    tk.Frame(row, bg=C["border2"], height=1).pack(
        side="left", fill="x", expand=True, padx=(10, 0))


def irrp_badge(parent, pct, cat, bg=None):
    """Cria um badge colorido de risco."""
    bg = bg or C["bg2"]
    cor = irrp_color_hex(cat)
    icons = {"BAIXO": "●", "MODERADO": "◆", "ALTO": "▲"}
    icon = icons.get(cat, "●")
    f = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
    inner = tk.Frame(f, bg=bg, padx=8, pady=3)
    inner.pack()
    tk.Label(inner, text=f"{icon}  {pct}%  {cat}",
             font=FONTS["badge"], bg=bg, fg=cor).pack()
    return f


def card(parent, padx=16, pady=12, bg=None, accent=None):
    """Card estilizado com barra superior dourada."""
    bg = bg or C["bg2"]
    accent = accent or C["gold"]
    f = tk.Frame(parent, bg=bg, padx=padx, pady=pady)
    tk.Frame(f, bg=accent, height=2).pack(fill="x", pady=(0, 10))
    return f


def bordered_entry(parent, textvariable, show=None, width=28):
    """Entry com borda decorativa âmbar."""
    outer = tk.Frame(parent, bg=C["border2"], padx=1, pady=1)
    e = tk.Entry(outer, textvariable=textvariable,
                 bg=C["entry_bg"], fg=C["entry_fg"],
                 insertbackground=C["gold"],
                 selectbackground=C["amber_dark"],
                 relief="flat", font=FONTS["body"],
                 width=width, show=show or "")
    e.pack(fill="x", ipady=6, padx=6)
    e.bind("<FocusIn>", lambda _: outer.config(bg=C["gold"]))
    e.bind("<FocusOut>", lambda _: outer.config(bg=C["border2"]))
    return outer, e



class IRRPGauge(tk.Canvas):
    """Gauge semicircular animado para exibição do IRRP."""
    SIZE = 140

    def __init__(self, parent, size=140, **kw):
        self.SIZE = size
        super().__init__(parent, width=size, height=size // 2 + 30,
                         bg=C["bg2"], highlightthickness=0, **kw)
        self._pct = 0
        self._cat = "BAIXO"
        self._target_pct = 0
        self._draw()

    def update_irrp(self, pct, cat):
        self._target_pct = pct
        self._cat = cat
        self._animate()

    def _animate(self):
        diff = self._target_pct - self._pct
        if abs(diff) < 0.5:
            self._pct = self._target_pct
            self._draw()
            return
        self._pct += diff * 0.15
        self._draw()
        self.after(16, self._animate)

    def _draw(self):
        self.delete("all")
        W, H = self.SIZE, self.SIZE // 2 + 30
        cx, cy = W // 2, H - 22
        r = W // 2 - 12

        # Fundo do arco (trilha)
        self._arc(cx, cy, r, 180, 360, C["bg3"], width=14)
        self._arc(cx, cy, r - 18, 180, 360, C["border"], width=2)

        # Arco de valor
        if self._pct > 0:
            cor = irrp_color_hex(self._cat)
            sweep = self._pct / 100.0 * 180
            self._arc(cx, cy, r, 180, 180 + sweep, cor, width=14)
            # Brilho
            self._arc(cx, cy, r, 180, 180 + min(sweep, 15),
                      blend_color(cor, "#FFFFFF", 0.4), width=3)

        # Número central
        cor = irrp_color_hex(self._cat)
        self.create_text(cx, cy - 8,
                         text=f"{int(self._pct)}%",
                         font=("Segoe UI", 16, "bold"),
                         fill=cor)
        self.create_text(cx, cy + 10,
                         text=self._cat,
                         font=FONTS["badge"],
                         fill=cor)
        # Rótulos 0 e 100
        self.create_text(10, cy + 4, text="0",
                         font=FONTS["badge"], fill=C["muted"])
        self.create_text(W - 10, cy + 4, text="100",
                         font=FONTS["badge"], fill=C["muted"])

    def _arc(self, cx, cy, r, start, end, color, width=4):
        x0, y0 = cx - r, cy - r
        x1, y1 = cx + r, cy + r
        self.create_arc(x0, y0, x1, y1,
                        start=-(start - 180),
                        extent=-(end - start),
                        style="arc", outline=color, width=width)

#  GRÁFICO DE BARRAS IRRP

class IRRPBarChart(tk.Canvas):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["bg2"], highlightthickness=0, **kw)
        self._dados = []
        self._hover = None
        self.bind("<Configure>", lambda _: self._draw())
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)

    def set_dados(self, dados):
        self._dados = dados
        self._hover = None
        self._draw()

    def _on_motion(self, e):
        if not self._dados: return
        W = self.winfo_width()
        PAD_L, PAD_R = 44, 16
        n = len(self._dados)
        gw = W - PAD_L - PAD_R
        idx = int((e.x - PAD_L) / (gw / n))
        if 0 <= idx < n and idx != self._hover:
            self._hover = idx
            self._draw()

    def _on_leave(self, _):
        if self._hover is not None:
            self._hover = None
            self._draw()

    def _draw(self):
        self.delete("all")
        dados = self._dados
        W = self.winfo_width()
        H = self.winfo_height()
        if W < 30 or H < 30: return

        if not dados:
            self.create_text(W // 2, H // 2,
                             text="Clique em Atualizar para carregar dados",
                             fill=C["muted"], font=FONTS["small"])
            return

        n = len(dados)
        PAD_L, PAD_R, PAD_T, PAD_B = 44, 16, 14, 46
        gw = W - PAD_L - PAD_R
        gh = H - PAD_T - PAD_B

        # Faixas de fundo
        y_alto = PAD_T + int(gh * (1 - 60 / 100))
        y_mod = PAD_T + int(gh * (1 - 30 / 100))
        y_bot = PAD_T + gh
        self.create_rectangle(PAD_L, PAD_T, PAD_L + gw, y_alto, fill=C["band_alto"], outline="")
        self.create_rectangle(PAD_L, y_alto, PAD_L + gw, y_mod, fill=C["band_mod"], outline="")
        self.create_rectangle(PAD_L, y_mod, PAD_L + gw, y_bot, fill=C["band_low"], outline="")
        self.create_rectangle(PAD_L, PAD_T, PAD_L + gw, y_bot, outline=C["border2"], fill="")

        # Grades
        for pct, cor, lbl in [(100, C["red"], "100"),
                              (60, C["yellow"], " 60"),
                              (30, C["green"], " 30"),
                              (0, C["muted"], "  0")]:
            y = PAD_T + int(gh * (1 - pct / 100))
            self.create_line(PAD_L, y, PAD_L + gw, y,
                             fill=cor, dash=(3, 4), width=1)
            self.create_text(PAD_L - 4, y, text=lbl,
                             fill=cor, anchor="e", font=FONTS["badge"])

        # Barras
        gap = max(1, int(gw / n * 0.15))
        bar_w = max(3, int(gw / n) - gap)
        hoje = datetime.now().strftime('%Y-%m-%d')

        for i, d in enumerate(dados):
            pct = max(0, min(100, d.get('irrp_pct', 0)))
            cat = d.get('irrp_cat', 'BAIXO')
            cor = irrp_color_hex(cat)
            data = d.get('data', '')
            is_hoje = (data == hoje)
            is_hover = (i == self._hover)

            x0 = PAD_L + int(i * gw / n) + gap // 2
            x1 = x0 + bar_w
            bh = max(0, int(gh * pct / 100))
            y0 = PAD_T + gh - bh
            y1 = PAD_T + gh

            if bh > 0:
                fill = blend_color(cor, "#FFFFFF", 0.15) if is_hover else cor
                self.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")
                # Brilho topo
                if bh > 4:
                    self.create_rectangle(x0, y0, x1, y0 + 3,
                                          fill=blend_color(cor, "#FFFFFF", 0.5),
                                          outline="")
                if bh >= 18:
                    self.create_text((x0 + x1) // 2, y0 + 9,
                                     text=str(pct),
                                     fill=C["bg"], font=FONTS["badge"])

            # Linha HOJE
            if is_hoje:
                cx = (x0 + x1) // 2
                self.create_line(cx, PAD_T, cx, y_bot,
                                 fill=C["gold"], dash=(3, 2), width=2)
                self.create_text(cx, PAD_T - 6, text="HOJE",
                                 fill=C["gold"], font=FONTS["badge"])

            # Label data
            if data:
                cx = (x0 + x1) // 2
                fg = C["gold"] if is_hoje else C["muted"]
                self.create_text(cx, y_bot + 10,
                                 text=data[5:],
                                 fill=fg, font=FONTS["badge"],
                                 angle=40 if n > 12 else 0)

            # Tooltip
            if is_hover and data:
                tip = f"  {data}   IRRP {pct}%   {cat}  "
                tx = min(max(PAD_L + 4, x0 - 40), W - 180)
                self.create_rectangle(tx - 4, PAD_T + 2, tx + 178, PAD_T + 16,
                                      fill=C["bg3"], outline=C["border2"])
                self.create_text(tx, PAD_T + 9, text=tip,
                                 fill=cor, font=FONTS["badge"], anchor="w")

        # Rótulos zonas
        rx = PAD_L + gw + 4
        for y, lbl, cor in [
            ((PAD_T + y_alto) // 2, "ALTO", C["red"]),
            ((y_alto + y_mod) // 2, "MOD", C["yellow"]),
            ((y_mod + y_bot) // 2, "OK", C["green"]),
        ]:
            self.create_text(rx, y, text=lbl, fill=cor,
                             font=FONTS["badge"], anchor="w")


# ══════════════════════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class OrbeetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ORBEET — Inteligência Climática Orbital")
        self.geometry("1180x740")
        self.minsize(960, 640)
        self.configure(bg=C["bg"])
        self.resizable(True, True)

        # Centralizar
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"1180x740+{(sw - 1180) // 2}+{(sh - 740) // 2}")

        self.usuarios, self.fazendas = carregar_dados()
        self.usuario_logado = None
        self.openai_api_key = ""
        self._current_page = None
        self._dados_historico = []

        self._load_logo()
        self._setup_styles()
        self._build_layout()
        self._show_login()

    # ── Logo ────────────────────────────────────────────────────────────────
    def _load_logo(self):
        self._logo_img = None
        self._logo_small = None
        if not PIL_OK:
            return
        try:
            raw = base64.b64decode(LOGO_B64)
            img = Image.open(io.BytesIO(raw)).convert("RGBA")
            # Versão login (grande)
            lg = img.resize((90, 90), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(lg)
            # Versão sidebar (pequena)
            sm = img.resize((44, 44), Image.LANCZOS)
            self._logo_small = ImageTk.PhotoImage(sm)
        except Exception:
            pass

    # ── Estilos ttk ─────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style()
        s.configure("TNotebook",
                    background=C["bg"], borderwidth=0)
        s.configure("TNotebook.Tab",
                    background=C["bg2"], foreground=C["muted"],
                    padding=[14, 7], font=FONTS["nav"])
        s.map("TNotebook.Tab",
              background=[("selected", C["bg4"])],
              foreground=[("selected", C["gold"])])

        s.configure("Orb.Treeview",
                    background=C["bg2"], foreground=C["text2"],
                    fieldbackground=C["bg2"], rowheight=28,
                    font=FONTS["body"])
        s.configure("Orb.Treeview.Heading",
                    background=C["bg4"], foreground=C["gold"],
                    font=FONTS["body_bold"], relief="flat")
        s.map("Orb.Treeview",
              background=[("selected", C["bg4"])],
              foreground=[("selected", C["gold"])])

        s.configure("TScrollbar",
                    background=C["bg3"], troughcolor=C["bg"],
                    arrowcolor=C["muted"])

        s.configure("TCombobox",
                    fieldbackground=C["entry_bg"],
                    background=C["bg4"],
                    foreground=C["text"],
                    selectbackground=C["bg4"],
                    arrowcolor=C["gold"])

    # ── Layout base ─────────────────────────────────────────────────────────
    def _build_layout(self):
        # ─ Sidebar ──────────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=C["bg2"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Faixa dourada lateral
        tk.Frame(self.sidebar, bg=C["gold"], width=3).place(
            relx=1.0, rely=0.0, relheight=1.0, anchor="ne")

        # Logo + título
        logo_frame = tk.Frame(self.sidebar, bg=C["bg2"])
        logo_frame.pack(fill="x", pady=(24, 4))
        if self._logo_small:
            tk.Label(logo_frame, image=self._logo_small,
                     bg=C["bg2"]).pack()
        else:
            tk.Label(logo_frame, text="🐝",
                     font=("Segoe UI Emoji", 28), bg=C["bg2"],
                     fg=C["gold"]).pack()

        tk.Label(logo_frame, text="ORBEET",
                 font=("Segoe UI", 15, "bold"),
                 bg=C["bg2"], fg=C["gold"]).pack()
        tk.Label(logo_frame,
                 text="Inteligência Climática Orbital",
                 font=("Segoe UI", 7), bg=C["bg2"],
                 fg=C["muted"], wraplength=180,
                 justify="center").pack(pady=(2, 0))

        tk.Frame(self.sidebar, bg=C["border2"],
                 height=1).pack(fill="x", padx=16, pady=14)

        # Usuário logado
        self.nav_user = tk.Label(
            self.sidebar, text="", font=FONTS["small"],
            bg=C["bg2"], fg=C["gold"],
            wraplength=190, justify="center")
        self.nav_user.pack(pady=(0, 10))

        # Botões de navegação
        self.nav_frame = tk.Frame(self.sidebar, bg=C["bg2"])
        self.nav_frame.pack(fill="x", padx=8)

        self.nav_btns = {}
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("🌾", "Fazendas", "fazendas"),
            ("📡", "Previsões", "previsoes"),
            ("🤖", "Recomendações", "recomendacoes"),
            ("⚙️", "Configurações", "config"),
        ]
        for ico, lbl, key in nav_items:
            f = tk.Frame(self.nav_frame, bg=C["bg2"])
            f.pack(fill="x", pady=2)
            accent = tk.Frame(f, bg=C["bg2"], width=4)
            accent.pack(side="left", fill="y")
            btn = tk.Button(
                f, text=f"  {ico}  {lbl}",
                command=lambda k=key: self._nav(k),
                bg=C["bg2"], fg=C["text2"],
                activebackground=C["bg3"],
                activeforeground=C["gold"],
                font=FONTS["nav"], relief="flat",
                anchor="w", padx=8, pady=10,
                cursor="hand2")
            btn.pack(side="left", fill="x", expand=True)
            btn.bind("<Enter>", lambda e, b=btn, a=accent: (
                b.config(bg=C["bg3"], fg=C["gold"]),
                a.config(bg=C["gold"])))
            btn.bind("<Leave>", lambda e, b=btn, a=accent, k=key: (
                b.config(bg=C["bg3"] if self._current_page == k else C["bg2"],
                         fg=C["gold"] if self._current_page == k else C["text2"]),
                a.config(bg=C["gold"] if self._current_page == k else C["bg2"])))
            self.nav_btns[key] = (btn, accent)

        # Separador e botão sair
        tk.Frame(self.sidebar, bg=C["border2"],
                 height=1).pack(fill="x", padx=16, side="bottom", pady=8)
        self.btn_sair = make_btn_secondary(
            self.sidebar, "  🚪  Sair", self._logout, width=18)
        self.btn_sair.pack(side="bottom", padx=14, pady=(0, 14), fill="x")
        self.btn_sair.pack_forget()

        # ─ Área de conteúdo ──────────────────────────────────────────────
        self.content = tk.Frame(self, bg=C["bg"])
        self.content.pack(side="left", fill="both", expand=True)

    def _nav(self, page):
        self._current_page = page
        for k, (btn, acc) in self.nav_btns.items():
            if k == page:
                btn.config(bg=C["bg3"], fg=C["gold"])
                acc.config(bg=C["gold"])
            else:
                btn.config(bg=C["bg2"], fg=C["text2"])
                acc.config(bg=C["bg2"])
        pages = {
            "dashboard": self._show_dashboard,
            "fazendas": self._show_fazendas,
            "previsoes": self._show_previsoes,
            "recomendacoes": self._show_recomendacoes,
            "config": self._show_config,
        }
        if page in pages:
            pages[page]()

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _page_header(self, icon, title, subtitle=""):
        hdr = tk.Frame(self.content, bg=C["bg"])
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        row = tk.Frame(hdr, bg=C["bg"])
        row.pack(fill="x")
        tk.Label(row, text=icon, font=("Segoe UI Emoji", 16),
                 bg=C["bg"], fg=C["gold"]).pack(side="left", padx=(0, 8))
        tk.Label(row, text=title, font=FONTS["title"],
                 bg=C["bg"], fg=C["gold"]).pack(side="left")
        if subtitle:
            tk.Label(hdr, text=subtitle, font=FONTS["small"],
                     bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(2, 0))
        tk.Frame(self.content, bg=C["border2"],
                 height=1).pack(fill="x", padx=28, pady=(10, 14))

    def _scrollable(self, parent, bg=None):
        bg = bg or C["bg"]
        container = tk.Frame(parent, bg=bg)
        canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical",
                           command=canvas.yview)
        inner = tk.Frame(canvas, bg=bg)
        inner.bind("<Configure>",
                   lambda _: canvas.configure(
                       scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(
                        -1 * (e.delta // 120), "units"))
        return container, inner

    def _make_treeview(self, parent, cols, widths=None):
        frame = tk.Frame(parent, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        sb = ttk.Scrollbar(frame, orient="vertical")
        sb.pack(side="right", fill="y")
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            style="Orb.Treeview",
                            yscrollcommand=sb.set)
        sb.config(command=tree.yview)
        w_list = widths or [80] * len(cols)
        for col, w in zip(cols, w_list):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        tree.tag_configure("baixo", foreground=C["green"])
        tree.tag_configure("moderado", foreground=C["yellow"])
        tree.tag_configure("alto", foreground=C["red"])
        tree.pack(fill="both", expand=True)
        return tree

    def _style_combobox(self, cb):
        cb.configure(font=FONTS["body"])
    # ══════════════════════════════════════════════════════════════════════
    #  LOGIN
    # ══════════════════════════════════════════════════════════════════════
    def _show_login(self):
        self._clear()
        self.nav_frame.pack_forget()
        self.btn_sair.pack_forget()

        # Fundo com hexágonos decorativos via Canvas
        canvas = tk.Canvas(self.content, bg=C["bg"],
                           highlightthickness=0)
        canvas.place(relwidth=1, relheight=1)
        self._draw_hex_bg(canvas)

        # Card central
        outer = tk.Frame(self.content, bg=C["bg2"],
                         padx=3, pady=3)
        outer.place(relx=0.5, rely=0.5, anchor="center")
        tk.Frame(outer, bg=C["gold"], height=3).pack(fill="x")
        inner = tk.Frame(outer, bg=C["bg2"], padx=40, pady=32)
        inner.pack()

        # Logo
        if self._logo_img:
            tk.Label(inner, image=self._logo_img,
                     bg=C["bg2"]).pack(pady=(0, 8))
        else:
            tk.Label(inner, text="🐝",
                     font=("Segoe UI Emoji", 44),
                     bg=C["bg2"], fg=C["gold"]).pack()

        tk.Label(inner, text="ORBEET",
                 font=("Segoe UI", 22, "bold"),
                 bg=C["bg2"], fg=C["gold"]).pack()
        tk.Label(inner,
                 text="Inteligência Climática Orbital",
                 font=FONTS["small"], bg=C["bg2"],
                 fg=C["muted"]).pack(pady=(0, 24))

        # Campos
        v_nome = tk.StringVar()
        v_senha = tk.StringVar()

        for lbl, var, show in [("NOME COMPLETO", v_nome, None),
                               ("SENHA", v_senha, "●")]:
            tk.Label(inner, text=lbl,
                     font=FONTS["badge"], bg=C["bg2"],
                     fg=C["muted"], anchor="w").pack(
                fill="x", pady=(8, 2))
            outer_e, e = bordered_entry(inner, var, show=show, width=30)
            outer_e.pack(fill="x")

        # Erro
        self._lbl_login_err = tk.Label(
            inner, text="", fg=C["red"],
            bg=C["bg2"], font=FONTS["small"])
        self._lbl_login_err.pack(pady=(6, 0))

        def do_login(e=None):
            u = autenticar_usuario(
                self.usuarios, v_nome.get().strip(), v_senha.get().strip())
            if u:
                self.usuario_logado = u
                self.nav_frame.pack(fill="x", padx=8)
                self.btn_sair.pack(side="bottom", padx=14,
                                   pady=(0, 14), fill="x")
                self.nav_user.config(
                    text=f"👤  {u['nome']}\n{u['categoria']}")
                self._nav("dashboard")
            else:
                self._lbl_login_err.config(
                    text="❌ Nome ou senha incorretos.")

        self.bind("<Return>", do_login)

        btns = tk.Frame(inner, bg=C["bg2"])
        btns.pack(fill="x", pady=(16, 0))
        make_btn_primary(btns, "  Entrar  →", do_login,
                         width=20).pack(side="left", padx=(0, 8))
        make_btn_secondary(btns, "Criar conta",
                           self._show_registro,
                           width=13).pack(side="left")

    def _draw_hex_bg(self, canvas):
        """Desenha hexágonos decorativos no fundo."""
        canvas.update_idletasks()
        W = canvas.winfo_width() or 800
        H = canvas.winfo_height() or 600
        size = 38
        h = size * 1.732
        cols = int(W // (size * 1.5)) + 2
        rows = int(H // h) + 2
        for row in range(rows):
            for col in range(cols):
                x = col * size * 1.5
                y = row * h + (h / 2 if col % 2 else 0)
                pts = []
                for i in range(6):
                    import math
                    angle = math.radians(60 * i - 30)
                    pts += [x + size * 0.95 * math.cos(angle),
                            y + size * 0.95 * math.sin(angle)]
                alpha = 0.04 + 0.02 * ((row + col) % 3)
                col_hex = blend_color(C["bg"], C["amber_dark"], alpha)
                canvas.create_polygon(pts, fill=col_hex,
                                      outline=C["border"], width=1)

    # ── REGISTRO ────────────────────────────────────────────────────────────
    def _show_registro(self):
        self._clear()

        canvas = tk.Canvas(self.content, bg=C["bg"], highlightthickness=0)
        canvas.place(relwidth=1, relheight=1)
        self._draw_hex_bg(canvas)

        outer = tk.Frame(self.content, bg=C["bg2"], padx=3, pady=3)
        outer.place(relx=0.5, rely=0.5, anchor="center")
        tk.Frame(outer, bg=C["gold"], height=3).pack(fill="x")
        inner = tk.Frame(outer, bg=C["bg2"], padx=40, pady=28)
        inner.pack()

        tk.Label(inner, text="Criar Conta",
                 font=FONTS["subtitle"], bg=C["bg2"],
                 fg=C["gold"]).pack(pady=(0, 4))
        tk.Label(inner,
                 text="Preencha os dados para se cadastrar no ORBEET",
                 font=FONTS["small"], bg=C["bg2"],
                 fg=C["muted"]).pack(pady=(0, 16))

        v_nome = tk.StringVar()
        v_senha = tk.StringVar()
        v_senha2 = tk.StringVar()
        v_cat = tk.StringVar(value="Fazendeiro")

        for lbl, var, show in [
            ("NOME COMPLETO", v_nome, None),
            ("SENHA", v_senha, "●"),
            ("CONFIRMAR SENHA", v_senha2, "●"),
        ]:
            tk.Label(inner, text=lbl, font=FONTS["badge"],
                     bg=C["bg2"], fg=C["muted"],
                     anchor="w").pack(fill="x", pady=(8, 2))
            out, _ = bordered_entry(inner, var, show=show, width=30)
            out.pack(fill="x")

        # Perfil
        tk.Label(inner, text="PERFIL", font=FONTS["badge"],
                 bg=C["bg2"], fg=C["muted"],
                 anchor="w").pack(fill="x", pady=(10, 4))
        cat_row = tk.Frame(inner, bg=C["bg2"])
        cat_row.pack(anchor="w")
        for opt in ["Fazendeiro", "Apicultor"]:
            tk.Radiobutton(
                cat_row, text=opt, variable=v_cat, value=opt,
                bg=C["bg2"], fg=C["text"],
                selectcolor=C["bg4"],
                activebackground=C["bg2"],
                activeforeground=C["gold"],
                font=FONTS["body"]).pack(side="left", padx=(0, 16))

        lbl_err = tk.Label(inner, text="", fg=C["red"],
                           bg=C["bg2"], font=FONTS["small"])
        lbl_err.pack(pady=(8, 0))

        def do_criar():
            ok, msg = criar_usuario(
                self.usuarios,
                v_nome.get().strip(),
                v_senha.get().strip(),
                v_cat.get())
            if not ok:
                lbl_err.config(text=msg);
                return
            if v_senha.get() != v_senha2.get():
                lbl_err.config(text="⚠  As senhas não coincidem.");
                return
            salvar_dados(self.usuarios, self.fazendas)
            messagebox.showinfo("Sucesso", "Conta criada!\nFaça login para continuar.")
            self._show_login()

        btns = tk.Frame(inner, bg=C["bg2"])
        btns.pack(fill="x", pady=(14, 0))
        make_btn_primary(btns, "Criar conta  →", do_criar,
                         width=20).pack(side="left", padx=(0, 8))
        make_btn_secondary(btns, "← Voltar",
                           self._show_login, width=12).pack(side="left")

    def _logout(self):
        self.unbind("<Return>")
        self.usuario_logado = None
        self.nav_user.config(text="")
        self.nav_frame.pack_forget()
        self.btn_sair.pack_forget()
        self._show_login()

    # ══════════════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════════════════════════════════
    def _show_dashboard(self):
        self._clear()
        u = self.usuario_logado
        self._page_header("🏠", "Dashboard",
                          f"Bem-vindo(a), {u['nome']} — {u['categoria']}")

        minhas = fazendas_do_usuario(self.fazendas, u['nome'])
        total_p = sum(len(f.get('historico_previsoes', [])) for f in minhas)
        total_r = sum(len(f.get('historico_recomendacoes', [])) for f in minhas)

        # ── Métricas ──────────────────────────────────────────────────────
        met_row = tk.Frame(self.content, bg=C["bg"])
        met_row.pack(fill="x", padx=28, pady=(0, 16))
        metrics = [
            ("🌾", str(len(minhas)), "Propriedades"),
            ("📡", str(total_p), "Dias monitorados"),
            ("🤖", str(total_r), "Recomendações"),
        ]
        for ico, val, lbl in metrics:
            mc = tk.Frame(met_row, bg=C["bg2"], padx=20, pady=14)
            mc.pack(side="left", expand=True, fill="x", padx=(0, 12))
            tk.Frame(mc, bg=C["gold"], height=2).pack(fill="x", pady=(0, 10))
            top = tk.Frame(mc, bg=C["bg2"])
            top.pack(fill="x")
            tk.Label(top, text=ico, font=("Segoe UI Emoji", 18),
                     bg=C["bg2"]).pack(side="left", padx=(0, 8))
            tk.Label(top, text=val, font=FONTS["metric"],
                     bg=C["bg2"], fg=C["gold"]).pack(side="left")
            tk.Label(mc, text=lbl, font=FONTS["small"],
                     bg=C["bg2"], fg=C["muted"]).pack(anchor="w")

        section_header(self.content, "🗺", "Status das Propriedades")

        if not minhas:
            tk.Label(self.content,
                     text="Você ainda não possui fazendas.\n"
                          "Acesse Fazendas → Registrar Fazenda para começar.",
                     font=FONTS["body"], bg=C["bg"], fg=C["muted"],
                     justify="center").pack(pady=30)
            return

        cont, inner = self._scrollable(self.content)
        cont.pack(fill="both", expand=True, padx=28)

        for f in minhas:
            hist = f.get('historico_previsoes', [])
            if hist:
                critico = max(hist, key=lambda d: d.get('irrp_pct', 0))
                pct, cat = critico['irrp_pct'], critico['irrp_cat']
            else:
                pct, cat = 0, 'BAIXO'
            cor = irrp_color_hex(cat)
            chave = 'plantios' if u['categoria'] == 'Fazendeiro' else 'abelhas'
            itens = f.get(chave, [])

            row = tk.Frame(inner, bg=C["bg2"], pady=0)
            row.pack(fill="x", pady=5)
            # Faixa lateral de cor
            tk.Frame(row, bg=cor, width=4).pack(side="left", fill="y")
            body = tk.Frame(row, bg=C["bg2"], padx=14, pady=12)
            body.pack(side="left", fill="both", expand=True)

            info = tk.Frame(body, bg=C["bg2"])
            info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=f['nome'],
                     font=FONTS["section"], bg=C["bg2"],
                     fg=C["text"]).pack(anchor="w")
            resumo = (', '.join(itens[:2]) + ('…' if len(itens) > 2 else '')) if itens else '—'
            tk.Label(info,
                     text=f"📍 {f['localizacao']}  ·  {resumo}",
                     font=FONTS["small"], bg=C["bg2"],
                     fg=C["muted"]).pack(anchor="w", pady=(2, 0))

            # Badge IRRP
            right = tk.Frame(body, bg=C["bg2"])
            right.pack(side="right", padx=(0, 8))
            tk.Label(right, text=f"{pct}%",
                     font=FONTS["metric_sm"], bg=C["bg2"],
                     fg=cor).pack()
            tk.Label(right, text=cat, font=FONTS["badge"],
                     bg=C["bg2"], fg=cor).pack()
