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

#  APIs OPEN-METEO

def obter_coordenadas(localizacao):
    """Geolocaliza uma cidade. Retorna (lat, lon, nome) ou (None, None, None)."""
    try:
        url = (f"https://geocoding-api.open-meteo.com/v1/search"
               f"?name={requests.utils.quote(localizacao)}&count=1&language=pt")
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        d = r.json()
        if 'results' not in d or not d['results']:
            return None, None, None
        res = d['results'][0]
        return res['latitude'], res['longitude'], res.get('name', localizacao)
    except Exception:
        return None, None, None


def obter_dados_climaticos(lat, lon):
    """
    Busca dados climáticos diários (passados + futuros) da Open-Meteo.
    Retorna lista de dicts com: data, temp_max, chuva, umidade, vento.
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,precipitation_sum,"
            f"relative_humidity_2m_max,wind_speed_10m_max"
            f"&timezone=America%2FSao_Paulo&past_days=15&forecast_days=15"
        )
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        d = r.json()
        if 'daily' not in d:
            return []
        dd = d['daily']
        datas, temps, chuvas, umids, ventos = (
            dd.get(k, []) for k in [
                'time', 'temperature_2m_max', 'precipitation_sum',
                'relative_humidity_2m_max', 'wind_speed_10m_max'
            ]
        )
        return [
            {
                'data':     datas[i],
                'temp_max': temps[i]  if i < len(temps)  else None,
                'chuva':    chuvas[i] if i < len(chuvas) else None,
                'umidade':  umids[i]  if i < len(umids)  else None,
                'vento':    ventos[i] if i < len(ventos) else None,
            }
            for i in range(len(datas))
        ]
    except Exception:
        return []

#  OPENAI — API de Recomendação

def gerar_recomendacao_openai(temp_max, chuva, umidade, vento, fator,
                               fazenda, usuario, api_key):
    """
    Gera recomendação personalizada via OpenAI.
    Cai no fallback se a chave não estiver disponível ou ocorrer erro.
    """
    chave_valida = (
        OPENAI_LIB_DISPONIVEL
        and api_key
        and api_key.strip() not in ("", "SUA_CHAVE_AQUI")
    )
    if not chave_valida:
        return _fallback_recomendacao(fator, temp_max, chuva, umidade, vento)

    try:
        if usuario['categoria'] == 'Fazendeiro':
            itens = fazenda.get('plantios', [])
            label = "Culturas plantadas"
        else:
            itens = fazenda.get('abelhas', [])
            label = "Espécies de abelha criadas"
        itens_str = ', '.join(itens) if itens else 'Não informado'

        prompt = (
            f"Você é especialista em apicultura e agricultura de precisão no Brasil.\n"
            f"Propriedade \"{fazenda.get('nome','?')}\" — {label}: {itens_str}\n"
            f"Dados climáticos: Temperatura máxima {temp_max}°C | Chuva {chuva} mm | "
            f"Umidade {umidade}% | Vento {vento} km/h\n"
            f"Fator de risco principal: {fator}\n\n"
            f"Gere um guia preventivo prático (máx 220 palavras) específico para os "
            f"itens desta propriedade, com ações concretas para proteger os "
            f"polinizadores. Linguagem simples e direta."
        )

        client = OpenAI(api_key=api_key.strip())
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        return response.output_text.strip()

    except Exception as e:
        return (
            _fallback_recomendacao(fator, temp_max, chuva, umidade, vento)
            + f"\n\n⚠ [Erro ao chamar OpenAI: {e}]"
        )


def _fallback_recomendacao(fator, temp_max, chuva, umidade, vento):
    fp = fator.lower()
    if "precipitação" in fp or "chuva" in fp:
        return (
            f"🌧  ALERTA DE TEMPORAL\n\nPrecipitação de {chuva:.1f} mm detectada.\n\n"
            "• Incline as colmeias para frente para escoar água\n"
            "• Instale lonas impermeáveis sobre as caixas\n"
            "• Adicione xarope de açúcar (1:1) dentro das colmeias\n"
            "• Evite abrir colmeias durante chuvas intensas\n"
            "• Inspecione infiltrações e umidade interna pós-chuva\n"
            "• Mantenha reservas alimentares para 5+ dias"
        )
    if "térmico" in fp or "temperatura" in fp:
        return (
            f"🌡  ALERTA DE ONDA DE CALOR\n\nTemperatura de {temp_max:.1f}°C.\n\n"
            "• Instale sombra artificial (sombrite 50%) sobre as colmeias\n"
            "• Posicione entradas voltadas para leste\n"
            "• Disponibilize água fresca a até 30 m do apiário\n"
            "• Realize manejos antes das 9h ou ao entardecer\n"
            "• Adicione melgueiras para ampliar ventilação\n"
            "• Monitore 'bearding' (cachos externos de abelhas)"
        )
    if "umidade" in fp or "seca" in fp:
        return (
            f"🏜  ALERTA DE SECA EXTREMA\n\nUmidade de {umidade:.0f}%.\n\n"
            "• Instale bebedouros próximos a todas as colmeias\n"
            "• Ofereça alimentação proteica (pólen artificial) e xarope\n"
            "• Irrigue as culturas florais para manter as flores abertas\n"
            "• Plante girassol, catingueira e jurema (resistentes à seca)\n"
            "• Reduza frequência de inspeções para minimizar estresse\n"
            "• Monitore estoques internos de mel e pólen semanalmente"
        )
    if "vento" in fp:
        return (
            f"💨  ALERTA DE VENTO FORTE\n\nVento de {vento:.1f} km/h.\n\n"
            "• Instale quebra-ventos naturais (bananeiras, cercas vivas)\n"
            "• Oriente entradas das colmeias contra o vento predominante\n"
            "• Ancore as caixas com cintas ou pesos superiores\n"
            "• Evite manejos durante rajadas intensas\n"
            "• Monitore temperatura interna (vento frio mata crias)\n"
            "• Reduza parcialmente a entrada das colmeias"
        )
    return (
        "⚠  ALERTA COMPOSTO\n\nMúltiplos fatores de risco detectados.\n\n"
        "• Monitoramento diário visual de todas as colmeias\n"
        "• Verifique estoques de mel e pólen\n"
        "• Garanta água fresca disponível\n"
        "• Reduza manejos invasivos\n"
        "• Acione técnico apícola regional\n"
        "• Registre observações diárias"
    )

#  JSON

def salvar_dados(usuarios, fazendas):
    """Persiste usuários e fazendas em JSON."""
    try:
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
            json.dump(
                {'usuarios': usuarios, 'fazendas': fazendas},
                f, ensure_ascii=False, indent=2
            )
        return True
    except Exception as e:
        return False


def carregar_dados():
    """Carrega dados do JSON. Retorna ([], []) se não existir."""
    if not os.path.exists(ARQUIVO_DADOS):
        return [], []
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            d = json.load(f)
        return d.get('usuarios', []), d.get('fazendas', [])
    except Exception:
        return [], []



#  HELPERS DE NEGÓCIO

def fazendas_do_usuario(fazendas, nome_usuario):
    """Filtra fazendas pertencentes ao usuário logado."""
    return [f for f in fazendas if f['usuario'] == nome_usuario]


def buscar_previsao_completa(fazenda, callback_progresso=None, callback_fim=None):
    """
    Busca dados futuros (próximos 15 dias) em thread separada.
    callback_progresso(msg, cor) — atualiza status
    callback_fim(registros, nome_local) — chamado ao terminar
    """
    def tarefa():
        if callback_progresso:
            callback_progresso("⏳ Consultando satélites...", "yellow")

        lat, lon, nome_local = obter_coordenadas(fazenda['localizacao'])
        if lat is None:
            if callback_progresso:
                callback_progresso("❌ Não foi possível geolocalizar.", "red")
            return

        dados  = obter_dados_climaticos(lat, lon)
        hoje   = datetime.now().strftime('%Y-%m-%d')
        futuro = sorted(
            [d for d in dados if d['data'] >= hoje],
            key=lambda x: x['data']
        )[:15]

        fila = FilaPrevisoes()
        for reg in futuro:
            pct, cat, fator = calcular_irrp(
                reg['temp_max'], reg['chuva'], reg['umidade'], reg['vento']
            )
            reg.update({'irrp_pct': pct, 'irrp_cat': cat, 'fator_principal': fator})
            fila.enqueue(reg)

        registros = []
        while not fila.esta_vazia():
            registros.append(fila.dequeue())

        fazenda['historico_previsoes'] = registros

        if callback_fim:
            callback_fim(registros, nome_local)

    threading.Thread(target=tarefa, daemon=True).start()


def buscar_historico_completo(fazenda, callback_progresso=None, callback_fim=None):
    """
    Busca dados históricos (últimos 15 dias) em thread separada.
    """
    def tarefa():
        if callback_progresso:
            callback_progresso("⏳ Buscando histórico...", "yellow")

        lat, lon, _ = obter_coordenadas(fazenda['localizacao'])
        if lat is None:
            if callback_progresso:
                callback_progresso("❌ Geolocalização falhou.", "red")
            return

        dados    = obter_dados_climaticos(lat, lon)
        hoje     = datetime.now().strftime('%Y-%m-%d')
        historico = sorted(
            [d for d in dados if d['data'] < hoje],
            key=lambda x: x['data']
        )
        for reg in historico:
            pct, cat, fator = calcular_irrp(
                reg['temp_max'], reg['chuva'], reg['umidade'], reg['vento']
            )
            reg.update({'irrp_pct': pct, 'irrp_cat': cat, 'fator_principal': fator})

        if callback_fim:
            callback_fim(historico)

    threading.Thread(target=tarefa, daemon=True).start()


def criar_usuario(usuarios, nome, senha, categoria):
    """Valida e cria um novo usuário. Retorna (True, '') ou (False, msg_erro)."""
    if len(nome.split()) < 2:
        return False, "⚠  Informe nome e sobrenome."
    if not senha:
        return False, "⚠  A senha não pode ser vazia."
    if any(u['nome'].lower() == nome.lower() for u in usuarios):
        return False, f"⚠  Usuário '{nome}' já existe."
    usuarios.append({'nome': nome, 'senha': senha, 'categoria': categoria})
    return True, ""


def autenticar_usuario(usuarios, nome, senha):
    """Retorna o dict do usuário se autenticado, ou None."""
    for u in usuarios:
        if u['nome'].lower() == nome.lower() and u['senha'] == senha:
            return u
    return None


def criar_fazenda(fazendas, nome_fazenda, localizacao, categoria_usuario, itens, nome_usuario):
    """Cria e registra uma nova fazenda."""
    chave = 'plantios' if categoria_usuario == 'Fazendeiro' else 'abelhas'
    nova = {
        'nome':        nome_fazenda,
        'localizacao': localizacao,
        'usuario':     nome_usuario,
        chave:         itens,
        'historico_previsoes':     [],
        'historico_recomendacoes': [],
    }
    fazendas.append(nova)
    return nova


def editar_fazenda(fazenda, novo_nome, nova_localizacao, novos_itens, categoria_usuario):
    """Atualiza os dados de uma fazenda existente in-place."""
    chave = 'plantios' if categoria_usuario == 'Fazendeiro' else 'abelhas'
    fazenda['nome']        = novo_nome
    fazenda['localizacao'] = nova_localizacao
    fazenda[chave]         = novos_itens


def excluir_fazenda(fazendas, fazenda):
    """Remove a fazenda da lista."""
    if fazenda in fazendas:
        fazendas.remove(fazenda)
        return True
    return False


def registrar_recomendacao(fazenda, critico, texto):
    """Salva uma recomendação no histórico da fazenda."""
    fazenda.setdefault('historico_recomendacoes', []).append({
        'gerado_em': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'dia_ref':   critico['data'],
        'irrp_pct':  critico['irrp_pct'],
        'irrp_cat':  critico['irrp_cat'],
        'fator':     critico['fator_principal'],
        'texto':     texto,
    })