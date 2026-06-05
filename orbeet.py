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