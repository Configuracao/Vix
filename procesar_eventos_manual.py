import os
import json
import re
import urllib.parse
import requests
import unicodedata
from datetime import datetime

# Configuración de URLs y archivos locales
AGENDA_URL = "https://streamxhd.com/eventos.json?"
LOCAL_CHANNELS_JSON = "04.json"
OUTPUT_JSON = "agenda.json"
BASE_IMG_URL = "https://raw.githubusercontent.com/Configuracao/Vix/main/assets/equipos_fm"
BASE_LEAGUE_IMG_URL = "https://raw.githubusercontent.com/Configuracao/Vix/main/assets/ligas_fm"  # Cambia esto si usas otra ruta para fondos de ligas

# Clase para hacer un diccionario insensible a mayúsculas, minúsculas y acentos
class CaseInsensitiveDict(dict):
    def __init__(self, data=None, **kwargs):
        super().__init__()
        if data:
            self.update(data)
        if kwargs:
            self.update(kwargs)

    def _normalize(self, key):
        if not isinstance(key, str):
            return key
        texto = unicodedata.normalize('NFD', key)
        texto = texto.encode('ascii', 'ignore').decode('utf-8')
        return texto.strip().lower()

    def __setitem__(self, key, value):
        super().__setitem__(self._normalize(key), value)

    def __getitem__(self, key):
        return super().__getitem__(self._normalize(key))

    def __contains__(self, key):
        return super().__contains__(self._normalize(key))

    def get(self, key, default=None):
        return super().get(self._normalize(key), default)
        
    def update(self, E=None, **F):
        if E is not None:
            if hasattr(E, 'keys'):
                for k in E:
                    super().__setitem__(self._normalize(k), E[k])
            else:
                for k, v in E:
                    super().__setitem__(self._normalize(k), v)
            for k in F:
                super().__setitem__(self._normalize(k), F[k])

# Diccionario de equipos (para escudos locales)
MAPEO_EQUIPOS = CaseInsensitiveDict({
    "puebla": "7847", "club puebla": "7847", "leon": "1841", "club León": "1841",
    "tigres": "8561", "tigres uanl": "8561", "toluca": "6618", "fc juarez": "649424",
    "juarez": "649424", "tijuana": "162418", "xolos": "162418", "queretaro": "1943",
    "queretaro fc": "1943", "atlante": "1942", "atlas": "6577", "chivas": "7807",
    "chivas guadalajara": "7807", "guadalajara": "7807", "cf america": "6576",
    "america": "6576", "club america": "6576", "monterrey": "7849", "rayados": "7849",
    "atletico de san luis": "6358", "atletico san luis": "6358", "san luis": "6358",
    "santos laguna": "7857", "pachuca": "7848", "necaxa": "1842", "pumas": "1946",
    "pumas unam": "1946", "cruz azul": "6578",
    "malaga": "9864", "espanyol": "8558", "rayo vallecano": "8370", "athletic club": "8315",
    "athletic bilbao": "8315", "deportivo alaves": "9866", "alaves": "9866",
    "atletico madrid": "9906", "atletico de madrid": "9906", "barcelona": "8634",
    "fc barcelona": "8634", "getafe": "8305", "real madrid": "8633", "villarreal": "10205",
    "elche": "10268", "celta vigo": "9910", "celta de vigo": "9910", "celta": "9910",
    "real sociedad": "8560", "deportivo a coruna": "9783", "real betis": "8603",
    "betis": "8603", "osasuna": "8371", "mallorca": "8661", "las palmas": "8306",
    "sevilla": "8302", "levante": "8581", "racing santander": "8696", "ceuta": "357259",
    "sabadell": "4033", "eldense": "8288", "cordoba": "7869", "girona": "7732",
    "arsenal": "9825", "leeds united": "8463", "aston villa": "10252", "brentford": "9937",
    "sunderland": "8472", "brighton & hove albion": "10204", "chelsea": "8455",
    "ipswich town": "9902", "fulham": "9879", "manchester united": "10260",
    "tottenham hotspur": "8586", "tottenham": "8586", "crystal palace": "9826",
    "nottingham forest": "10203", "hull city": "8667", "everton": "8668",
    "liverpool": "8650", "manchester city": "8456", "afc bournemouth": "8678",
    "bournemouth": "8678", "newcastle united": "10261",
    "borussia dortmund": "9789", "werder bremen": "8697", "paderborn": "8460",
    "stuttgart": "10269", "hoffenheim": "8226", "hamburger sv": "9790",
    "augsburg": "8406", "bayern munchen": "9823", "mainz 05": "9905",
    "bayer leverkusen": "8178", "union berlin": "8149", "elversberg": "8232",
    "rb leipzig": "178475", "eintracht frankfurt": "9810",
    "lens": "8588", "olympique lyonnais": "9748", "lille": "8639", "le havre": "9746",
    "lorient": "8689", "paris": "6379", "brest": "8521", "angers sco": "8121",
    "psg": "9847", "le mans": "8682", "monaco": "9829", "toulouse": "9941",
    "genoa": "10233", "fiorentina": "8535", "inter": "8636", "inter de milan": "8636", "parma": "10167",
    "napoli": "9875", "frosinone": "9891",
    "vasco da gama": "10276", "remo": "1626", "são paulo": "10277", "vitória": "7733",
    "boca juniors": "90006", "river plate": "90015",
})

# Diccionario para asociar ligas con un ID específico (para fondos y estilos)
MAPEO_LIGAS = CaseInsensitiveDict({
    "LaLiga": "laliga",
    "Premier League": "premier",
    "Serie A": "seriea",
    "Bundesliga": "bundesliga",
    "Ligue 1": "ligue1",
    "UEFA Champions League": "ucl",
    "Copa Libertadores": "libertadores",
    "Championship": "championship",
    "Liga 1": "Liga1",
    "LaLiga SmartBank": "smartbank",
    "Liga Ecuador": "ligaecuador",
    "Liga Profesional": "ligaprofesional",
    "Liga Uruguay": "ligauruguay",
    "MLB": "mlb",
    "Liga Paraguay": "ligaparaguay",
    "Brasileirão": "brasileirão",
    "NBA Pretemporada": "nba",
    "Copa de la Liga": "copadelaliga",
    "Copa Libertadores Femenina": "libertadores",
    "Liga MX": "ligamx",
    "Liga de Expansión MX": "expamx",
    "Bundesliga 2": "bundesliga2",
    "demo": "deml",
    "demo": "deml",
    "demo": "deml",
    "demo": "deml",
    "demo": "deml",
    "demo": "deml",
    "demo": "deml",
    # Agrega más ligas según necesites...
})

def limpiar_nombre_equipo(nombre, liga_nombre=""):
    if not nombre:
        return ""
    nombre_limpio = nombre.strip()
    if nombre_limpio.lower() == "everton":
        liga_lower = liga_nombre.lower()
        if any(k in liga_lower for k in ["primera división", "chile", "tntsports"]):
            return "Everton de Viña del Mar"
        return "Everton"
    return nombre_limpio

def buscar_imagen(equipo_val):
    if not equipo_val:
        return ""
    if equipo_val in MAPEO_EQUIPOS:
        return f"{BASE_IMG_URL}/{MAPEO_EQUIPOS[equipo_val]}.png"
    return ""

def obtener_info_liga(liga_nombre):
    if not liga_nombre:
        return "", ""
    league_id = MAPEO_LIGAS.get(liga_nombre, "")
    league_bg = f"{BASE_LEAGUE_IMG_URL}/{league_id}.jpg" if league_id else ""
    return league_id, league_bg

def procesar_agenda():
    canales_04_dict = {}
    if os.path.exists(LOCAL_CHANNELS_JSON):
        try:
            with open(LOCAL_CHANNELS_JSON, "r", encoding="utf-8") as f:
                contenido_04 = json.load(f)
                if isinstance(contenido_04, list) and len(contenido_04) > 0:
                    for c in contenido_04:
                        ch_key = c.get("channel", "").strip().lower()
                        if ch_key:
                            canales_04_dict[ch_key] = c
                    print(f"Se cargaron e indexaron {len(canales_04_dict)} canales desde {LOCAL_CHANNELS_JSON}.")
        except Exception as e:
            print(f"Error al leer {LOCAL_CHANNELS_JSON}: {e}")

    print(f"Descargando JSON manual desde {AGENDA_URL}...")
    try:
        response = requests.get(AGENDA_URL, timeout=10)
        if response.status_code != 200:
            print(f"Error al descargar la agenda manual: Status {response.status_code}")
            return
        agenda_data = response.json()
    except Exception as e:
        print(f"Error al obtener datos de la agenda manual: {e}")
        return

    print("Procesando eventos, aplicando imágenes locales y IDs de ligas...")

    if "sports" in agenda_data:
        for sport in agenda_data["sports"]:
            for league in sport.get("leagues", []):
                league_name = league.get("name", "")
                league_id, league_bg = obtener_info_liga(league_name)

                for event in league.get("events", []):
                    home_raw = event.get("homeTeam", "")
                    away_raw = event.get("awayTeam", "")
                    
                    home_team = limpiar_nombre_equipo(home_raw, league_name)
                    away_team = limpiar_nombre_equipo(away_raw, league_name)

                    event["homeTeam"] = home_team
                    event["awayTeam"] = away_team

                    if away_team:
                        event["title"] = f"{home_team} vs {away_team}"
                    else:
                        event["title"] = home_team

                    # Asignar ID de liga y fondo de liga al evento
                    event["leagueId"] = league_id
                    event["leagueBackground"] = league_bg

                    # Obtener logos exclusivamente del repositorio local usando MAPEO_EQUIPOS
                    home_logo = event.get("homeLogo") or buscar_imagen(home_team)
                    away_logo = event.get("awayLogo") or buscar_imagen(away_team)
                    event_thumb = event.get("image", "")

                    event["homeLogo"] = home_logo
                    event["awayLogo"] = away_logo
                    event["image"] = event_thumb

                    if event_thumb:
                        event["imageMode"] = "banner"
                    elif home_logo or away_logo:
                        event["imageMode"] = "teams"

                    # Procesar servidores y buscar coincidencias en 04.json
                    nuevos_servidores = []
                    for server in event.get("servers", []):
                        server_url = server.get("url", "")
                        parsed_url = urllib.parse.urlparse(server_url)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        
                        channel_param = query_params.get("channel", [""])[0].strip().lower()
                        if not channel_param:
                            channel_param = query_params.get("stream", [""])[0].strip().lower()

                        if channel_param and channel_param in canales_04_dict:
                            canal_info = canales_04_dict[channel_param]
                            nuevos_servidores.append({
                                "name": canal_info.get("canal", server.get("name", channel_param.upper())),
                                "url": canal_info.get("url", ""),
                                "type": canal_info.get("tipo", "clearkey"),
                                "quality": server.get("quality", ""),
                                "active": True,
                                "languages": server.get("languages", []),
                                "customLanguages": server.get("customLanguages", ""),
                                "channelLogo": canal_info.get("logo", server.get("channelLogo", "")),
                                "clearkey": canal_info.get("clearkey", None),
                                "referer": canal_info.get("referer", ""),
                                "origin": canal_info.get("origin", "")
                            })
                        else:
                            iframe_url = f"https://pruevon.blogspot.com/2026/04/embedc.html?r={urllib.parse.quote(server_url, safe='')}"
                            server_copy = dict(server)
                            server_copy["url"] = iframe_url
                            server_copy["type"] = "iframe"
                            nuevos_servidores.append(server_copy)

                    event["servers"] = nuevos_servidores

    if "updated" not in agenda_data or not agenda_data["updated"]:
        agenda_data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(agenda_data, f, ensure_ascii=False, indent=4)

    print(f"Agenda manual procesada y guardada correctamente en {OUTPUT_JSON}.")

if __name__ == "__main__":
    procesar_agenda()