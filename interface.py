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
