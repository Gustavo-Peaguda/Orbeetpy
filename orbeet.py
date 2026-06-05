"""
Enzo Fernandes Ramos RM: 563705
Felipe Henrique de Souza Cerazi RM: 562746
Gustavo Peaguda de Castro RM: 562923
Lorenzo Coque RM: 563385
"""

import os
import json
import threading
import requests
from datetime import datetime

# ── OpenAI ───────────────────────────────────────────────────────────────────
try:
    from openai import OpenAI
    OPENAI_LIB_DISPONIVEL = True
except ImportError:
    OPENAI_LIB_DISPONIVEL = False


#  ARQUIVO DE PERSISTÊNCIA

ARQUIVO_DADOS = "orbeet_dados.json"

#  [DP-1] FILA MANUAL

class FilaPrevisoes:
    def __init__(self):       self._dados = []
    def enqueue(self, item):  self._dados.append(item)
    def dequeue(self):        return None if self.esta_vazia() else self._dados.pop(0)
    def esta_vazia(self):     return len(self._dados) == 0
    def todos(self):          return list(self._dados)



#  FUNÇÕES AVULSAS DE FILA — estilo visto em aula

def enqueue(queue, item):
    """Insere um item no final da fila."""
    queue.append(item)

def dequeue(queue):
    """Remove e retorna o primeiro item da fila."""
    if not is_empty_queue(queue):
        return queue.pop(0)

def first(queue):
    """Retorna o primeiro item da fila sem removê-lo."""
    if not is_empty_queue(queue):
        return queue[0]

def is_empty_queue(queue):
    """Retorna True se a fila estiver vazia."""
    return len(queue) == 0

def size_queue(queue):
    """Retorna o tamanho da fila."""
    return len(queue)

#  BUSCA BINÁRIA RECURSIVA

def busca_binaria_recursiva(lista, alvo, inicio, fim):
    if inicio > fim:
        return -1
    meio = (inicio + fim) // 2
    if lista[meio]['data'] == alvo:
        return meio
    elif lista[meio]['data'] < alvo:
        return busca_binaria_recursiva(lista, alvo, meio + 1, fim)
    else:
        return busca_binaria_recursiva(lista, alvo, inicio, meio - 1)


#  CÁLCULO DO IRRP

_MAX_SCORES = {'temp': 35.0, 'chuva': 30.0, 'umidade': 20.0, 'vento': 15.0}


def _score_temp(t):
    if t is None: return 0.0
    if t < 12:             return 35.0
    if 12 <= t < 16:       return 35.0 - ((t - 12) / 4.0) * 35.0
    if 16 <= t <= 27:      return 0.0
    if 27 < t <= 34:       return ((t - 27) / 7.0) * 35.0
    return 35.0


def _score_chuva(c):
    if c is None: return 0.0
    if c <= 0:    return 0.0
    if c <= 10:   return 7.5 * c / 10.0
    if c <= 30:   return 7.5 + 12.5 * (c - 10) / 20.0
    if c <= 50:   return 20.0 + 10.0 * (c - 30) / 20.0
    return 30.0


def _score_umidade(u):
    if u is None: return 0.0
    if u >= 80:   return 0.0
    if u >= 60:   return 5.0 * (80 - u) / 20.0
    if u >= 40:   return 5.0 + 7.5 * (60 - u) / 20.0
    if u >= 20:   return 12.5 + 7.5 * (40 - u) / 20.0
    return 20.0


def _score_vento(v):
    if v is None: return 0.0
    if v <= 5:    return 0.0
    if v <= 15:   return 5.0 * (v - 5) / 10.0
    if v <= 25:   return 5.0 + 5.0 * (v - 15) / 10.0
    if v <= 40:   return 10.0 + 5.0 * (v - 25) / 15.0
    return 15.0


def calcular_irrp(temp_max, chuva, umidade, vento):
    """
    IRRP = pior fator normalizado (0-100).
    Retorna: (irrp_pct, categoria, fator_dominante_str)
    """
    scores = {
        'temp':    _score_temp(temp_max),
        'chuva':   _score_chuva(chuva),
        'umidade': _score_umidade(umidade),
        'vento':   _score_vento(vento),
    }
    normalized = {
        k: min(100.0, (scores[k] / _MAX_SCORES[k]) * 100.0)
        for k in scores
    }
    irrp_pct = round(max(normalized.values()))
    cat = (
        "BAIXO"    if irrp_pct <= 30 else
        "MODERADO" if irrp_pct <= 60 else
        "ALTO"
    )
    fator_key = max(normalized, key=normalized.get)
    fatores = {
        'temp':    f"Temperatura crítica ({temp_max:.1f}°C)"  if temp_max is not None else "Temperatura",
        'chuva':   f"Precipitação intensa ({chuva:.1f} mm)"   if chuva    is not None else "Chuva",
        'umidade': f"Baixa umidade ({umidade:.0f}%)"          if umidade  is not None else "Seca",
        'vento':   f"Vento forte ({vento:.1f} km/h)"          if vento    is not None else "Vento",
    }
    fator = (
        "Condições favoráveis à polinização"
        if max(scores.values()) < 2.0
        else fatores[fator_key]
    )
    return irrp_pct, cat, fator


def irrp_color_hex(cat):
    """Retorna a cor hex para a categoria de risco."""
    return {"BAIXO": "#4CAF50", "MODERADO": "#FFC107", "ALTO": "#F44336"}.get(cat, "#A08050")