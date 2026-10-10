import os
import json
import requests
import unicodedata

# URL del JSON original o archivo local
JSON_URL = "https://streamx305.sbs/json/agenda550.json"
OUTPUT_JSON = "agenda.json"
EQUIPOS_DIR = os.path.join("assets", "equipos_fm")
BASE_IMG_URL = "https://raw.githubusercontent.com/Configuracao/Vix/main/assets/equipos_fm"

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

# Diccionario de equipos (admite cualquier combinación de mayúsculas y minúsculas)
MAPEO_EQUIPOS = CaseInsensitiveDict({
    # --- Liga MX ---
    "puebla": "7847", "club puebla": "7847", "leon": "1841", "club León": "1841",
    "tigres": "8561", "tigres uanl": "8561", "toluca": "6618", "fc juarez": "649424",
    "juarez": "649424", "tijuana": "162418", "xolos": "162418", "queretaro": "1943",
    "queretaro fc": "1943", "atlante": "1942", "atlas": "6577", "chivas": "7807",
    "chivas guadalajara": "7807", "guadalajara": "7807", "cf america": "6576",
    "america": "6576", "club america": "6576", "monterrey": "7849", "rayados": "7849",
    "atletico de san luis": "6358", "atletico san luis": "6358", "san luis": "6358",
    "santos laguna": "7857", "pachuca": "7848", "necaxa": "1842", "pumas": "1946",
    "pumas unam": "1946", "cruz azul": "6578",

    # --- LaLiga & LaLiga2 (España) ---
    "malaga": "9864", "espanyol": "8558", "rayo vallecano": "8370", "athletic club": "8315",
    "athletic bilbao": "8315", "deportivo alaves": "9866", "alaves": "9866",
    "atletico madrid": "9906", "atletico de madrid": "9906", "barcelona": "8634",
    "fc barcelona": "8634", "getafe": "8305", "real madrid": "8633", "villarreal": "10205",
    "elche": "10268", "celta vigo": "9910", "celta de vigo": "9910", "celta": "9910",
    "real sociedad": "8560", "deportivo a coruna": "9783", "real betis": "8603",
    "betis": "8603", "osasuna": "8371", "mallorca": "8661", "las palmas": "8306",
    "sevilla": "8302", "levante": "8581", "racing santander": "8696", "ceuta": "357259",
    "sabadell": "4033", "eldense": "8288", "cordoba": "7869", "celta de vigo ii": "161743",
    "real sociedad ii": "161744", "girona": "7732",

    # --- Premier League (Inglaterra) ---
    "arsenal": "9825", "leeds united": "8463", "aston villa": "10252", "brentford": "9937",
    "sunderland": "8472", "brighton & hove albion": "10204", "chelsea": "8455",
    "ipswich town": "9902", "fulham": "9879", "manchester united": "10260",
    "tottenham hotspur": "8586", "tottenham": "8586", "crystal palace": "9826",
    "nottingham forest": "10203", "hull city": "8667", "everton": "8668",
    "liverpool": "8650", "manchester city": "8456", "afc bournemouth": "8678",
    "bournemouth": "8678", "newcastle united": "10261",

    # --- Bundesliga (Alemania) ---
    "borussia dortmund": "9789", "werder bremen": "8697", "paderborn": "8460",
    "stuttgart": "10269", "hoffenheim": "8226", "hamburger sv": "9790",
    "augsburg": "8406", "bayern munchen": "9823", "mainz 05": "9905",
    "bayer leverkusen": "8178", "union berlin": "8149", "elversberg": "8232",
    "rb leipzig": "178475", "eintracht frankfurt": "9810",

    # --- Ligue 1 (Francia) ---
    "lens": "8588", "olympique lyonnais": "9748", "lille": "8639", "le havre": "9746",
    "lorient": "8689", "paris": "6379", "brest": "8521", "angers sco": "8121",
    "psg": "9847", "le mans": "8682", "monaco": "9829", "toulouse": "9941",

    # --- Serie A (Italia) ---
    "genoa": "10233", "fiorentina": "8535", "inter": "8636", "parma": "10167",
    "napoli": "9875", "frosinone": "9891",

    # --- Brasileirão (Brasil) ---
    "vasco da gama": "10276", "remo": "1626", "são paulo": "10277", "vitória": "7733",

    # --- Liga 1 (Perú) ---
    "deportivo garcilaso": "920788", "sport huancayo": "165148", "adt": "1104719",
    "fc cajamarca": "1696744", "comerciantes unidos": "536945", "juan pablo ii college": "1573153",
    "universitario": "4409", "melgar": "4417",

    # --- MLS (Estados Unidos / Canadá) ---
    "toronto fc": "91001", "cf montreal": "91002", "chicago fire": "91003",
    "new york city": "91004", "inter miami": "91005", "dc united": "91006",
    "atlanta united": "91007", "cincinnati": "91008", "orlando city sc": "91009",
    "columbus crew": "91010", "new york rb": "91011", "san diego": "91012",
    "charlotte": "91013", "dallas": "91014", "philadelphia union": "91015",
    "real salt lake": "91016", "new england": "91017", "seattle sounders fc": "91018",
    "austin": "91019", "nashville sc": "91020", "minnesota united": "91021",
    "houston dynamo": "91022", "sporting kc": "91023", "portland timbers": "91024",
    "colorado rapids": "91025", "sj earthquakes": "91026", "los angeles fc": "91027",
    "vancouver whitecaps": "91028",

    # --- Liga BetPlay (Colombia) ---
    "alianza": "80002", "rionegro águilas": "80001", "once caldas": "80019",
    "llaneros": "80017", "deportivo pereira": "80010", "deportivo cali": "80008",
    "junior": "80015", "inter bogotá": "80025",

    # --- Liga Profesional (Argentina) ---
    "aldosivi": "90001", "sarmiento": "90002", "gimnasia la plata": "90003",
    "atletico tucumán": "90004", "instituto": "90005", "boca juniors": "90006",
    "unión santa fe": "90007", "defensa y justicia": "90008", "barracas central": "90009",
    "huracán": "90010", "central córdoba sde": "90011", "estudiantes lp": "90012",
    "tigre": "90013", "banfield": "90014", "river plate": "90015", "estudiantes río cuarto": "90016",

    # --- Championship (Inglaterra) ---
    "west ham united": "92001", "queens park rangers": "92002", "west bromwich albion": "92003",
    "birmingham city": "92004", "bolton wanderers": "92005", "stoke city": "92006",
    "derby county": "92007", "wrexham": "92008", "watford": "92009", "burnley": "92010",

    # --- Primera División (Uruguay) ---
    "torque": "93001", "danubio": "93002", "deportivo maldonado": "93003",
    "liverpool": "8650", "defensor sporting": "93005", "cerro": "93006",
    "wanderers": "93007", "boston river": "93008", "peñarol": "93009", "progreso": "93010",

    # --- Primera División (Chile) ---
    "cobresal": "94001", "univ. concepción": "94002", "huachipato": "94003",
    "o'higgins": "94004", "universidad católica": "94005", "audax italiano": "94006",

    # --- Süper Lig (Turquía) ---
    "samsunspor": "95001", "trabzonspor": "95002", "Rizespor": "95003",
    "galatasaray": "8637", "Kasımpaşa": "8630", "fenerbahçe": "8695",

    # --- Primeira Liga (Portugal) ---
    "sporting braga": "95004", "marítimo": "95005", "porto": "95006", "sporting cp": "9768",

    # --- Bundesliga 2 (Alemania) ---
    "magdeburg": "95007", "hannover 96": "95008", "nürnberg": "95009", "wolfsburg": "95010",

    # --- Eredivisie (Países Bajos) ---
    "ajax": "95011", "nec nijmegen": "8464", "psv": "8640", "heerenveen": "9926", "feyenoord": "10235", "az": "10229",

    # --- Liga Profesional Saudí ---
    "al hilal": "96001", "al ittihad": "96002", "al kholood": "1014",
    "al quadisiya": "1013", "al nassr": "6001", "diriyah": "6002",
})

# Estructura base de deportes
SPORTS_BASE = [
    {"id": "automovilismo", "name": "Automovilismo", "icon": "🏎️", "leagues": []},
    {"id": "futbol", "name": "Fútbol", "icon": "⚽", "leagues": []},
    {"id": "tenis", "name": "Tenis", "icon": "🎾", "leagues": []},
    {"id": "beisbol", "name": "Béisbol", "icon": "⚾", "leagues": []},
    {"id": "motor", "name": "Motor", "icon": "🏎️", "leagues": []},
    {"id": "tennis", "name": "Tennis", "icon": "🎾", "leagues": []},
    {"id": "football", "name": "Football", "icon": "⚽", "leagues": []},
    {"id": "boxing", "name": "Boxing", "icon": "🥊", "leagues": []},
    {"id": "mma", "name": "MMA / UFC", "icon": "🥋", "leagues": []},
    {"id": "baseball", "name": "Baseball", "icon": "⚾", "leagues": []},
    {"id": "nfl", "name": "American Football", "icon": "🏈", "leagues": []},
    {"id": "basketball", "name": "Basketball", "icon": "🏀", "leagues": []},
    {"id": "hockey", "name": "Hockey", "icon": "🏒", "leagues": []}
]

def buscar_imagen(equipo_val):
    if not equipo_val:
        return ""
    if equipo_val in MAPEO_EQUIPOS:
        return f"{BASE_IMG_URL}/{MAPEO_EQUIPOS[equipo_val]}.png"
    return ""

def extraer_liga_y_titulo(titulo_raw):
    if ":" in titulo_raw:
        partes = titulo_raw.split(":", 1)
        return partes[0].strip(), partes[1].strip()
    return "Otras Competencias", titulo_raw.strip()

def detectar_deporte(liga, titulo):
    texto = f"{liga} {titulo}".lower()
    if any(k in texto for k in ["f1", "gp", "formula 1", "motogp"]):
        return "motor"
    if any(k in texto for k in ["nba", "wnba", "baloncesto"]):
        return "basketball"
    if any(k in texto for k in ["ufc", "boxing", "boxe", "mma"]):
        return "boxing" if "boxing" in texto else "mma"
    if any(k in texto for k in ["nhl", "hockey"]):
        return "hockey"
    return "football"

def obtener_nombre_canal(url):
    if "channel=" in url:
        return url.split("channel=")[-1].upper()
    return "Server TV"

def procesar_agenda():
    print("Descargando JSON desde streamx305.sbs...")
    try:
        response = requests.get(JSON_URL, timeout=10)
        if response.status_code != 200:
            print(f"Error al descargar: Status {response.status_code}")
            return
        agenda_raw = response.json()
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return

    deportes_dict = {sport["id"]: sport for sport in SPORTS_BASE}
    eventos_agrupados = {}

    order_index = 1
    for item in agenda_raw:
        raw_title = item.get("title", "")
        link = item.get("link", "")
        fecha = item.get("date", "")
        hora = item.get("time", "")

        liga_nombre, partido_titulo = extraer_liga_y_titulo(raw_title)
        sport_id = detectar_deporte(liga_nombre, partido_titulo)

        event_key = f"{fecha}_{hora}_{partido_titulo}"

        if event_key not in eventos_agrupados:
            home_team, away_team = "", ""
            if " vs " in partido_titulo:
                equipos = partido_titulo.split(" vs ")
                home_team = equipos[0].strip()
                away_team = equipos[1].strip()
            else:
                home_team = partido_titulo

            home_logo = buscar_imagen(home_team)
            away_logo = buscar_imagen(away_team)

            eventos_agrupados[event_key] = {
                "sport_id": sport_id,
                "league_name": liga_nombre,
                "event_data": {
                    "title": partido_titulo,
                    "league": liga_nombre,
                    "code": "",
                    "time": f"{fecha} {hora}",
                    "timezone": "America/Lima",
                    "agendaOrder": order_index,
                    "image": "",
                    "logo": "",
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "homeLogo": home_logo,
                    "awayLogo": away_logo,
                    "imageMode": "teams" if home_logo or away_logo else "",
                    "duration": 130,
                    "extraTime": 0,
                    "status": item.get("status", ""),
                    "note": "",
                    "servers": [],
                    "flagCode": "",
                    "flagUrl": "",
                    "homeCountryCode": "",
                    "awayCountryCode": ""
                }
            }
            order_index += 1

        canal_nombre = obtener_nombre_canal(link)
        eventos_agrupados[event_key]["event_data"]["servers"].append({
            "name": canal_nombre,
            "url": link,
            "type": "iframe",
            "quality": "",
            "active": True,
            "languages": [],
            "customLanguages": "",
            "channelLogo": ""
        })

    for ev in eventos_agrupados.values():
        s_id = ev["sport_id"]
        l_name = ev["league_name"]
        ev_data = ev["event_data"]

        deporte = deportes_dict[s_id]
        
        liga_obj = next((l for l in deporte["leagues"] if l["name"] == l_name), None)
        if not liga_obj:
            liga_obj = {
                "name": l_name,
                "logo": "",
                "image": "",
                "background": "",
                "events": [],
                "flagCode": "",
                "flagUrl": ""
            }
            deporte["leagues"].append(liga_obj)

        liga_obj["events"].append(ev_data)

    resultado_final = {
        "sports": list(deportes_dict.values()),
        "updated": f"{fecha} {hora}:00"
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, ensure_ascii=False, indent=4)

    print(f"Agenda generada correctamente en {OUTPUT_JSON}")

if __name__ == "__main__":
    procesar_agenda()