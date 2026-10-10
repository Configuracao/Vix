import os
import json
import requests
import unicodedata

# URL del JSON original o archivo local
JSON_URL = "https://streamx305.sbs/json/agenda550.json"
OUTPUT_JSON = "agenda.json"
EQUIPOS_DIR = os.path.join("assets", "equipos_fm")
BASE_IMG_URL = "https://raw.githubusercontent.com/Configuracao/Vix/main/assets/equipos_fm"

# Mapeo extraído directamente de matches.json con los IDs reales
MAPEO_EQUIPOS = {
    # --- Liga MX ---
    "puebla": "7847",
    "club puebla": "7847",
    "leon": "1841",
    "club León": "1841",
    "tigres": "8561",
    "tigres uanl": "8561",
    "toluca": "6618",
    "fc juarez": "649424",
    "juarez": "649424",
    "tijuana": "162418",
    "xolos": "162418",
    "queretaro": "1943",
    "queretaro fc": "1943",
    "atlante": "1942",
    "atlas": "6577",
    "chivas": "7807",
    "chivas guadalajara": "7807",
    "guadalajara": "7807",
    "cf america": "6576",
    "america": "6576",
    "club america": "6576",
    "monterrey": "7849",
    "rayados": "7849",
    "atletico de san luis": "6358",
    "atletico san luis": "6358",
    "san luis": "6358",
    "santos laguna": "7857",
    "santos lagunas": "7857",
    "pachuca": "7848",
    "necaxa": "1842",
    "pumas": "1946",
    "pumas unam": "1946",
    "cruz azul": "6578",

    # --- LaLiga & LaLiga2 (España) ---
    "malaga": "9864",
    "espanyol": "8558",
    "rayo vallecano": "8370",
    "athletic club": "8315",
    "athletic bilbao": "8315",
    "deportivo alaves": "9866",
    "alaves": "9866",
    "atletico madrid": "9906",
    "atletico de madrid": "9906",
    "barcelona": "8634",
    "fc barcelona": "8634",
    "getafe": "8305",
    "real madrid": "8633",
    "villarreal": "10205",
    "elche": "10268",
    "celta vigo": "9910",
    "celta de vigo": "9910",
    "celta": "9910",
    "real sociedad": "8560",
    "deportivo a coruna": "9783",
    "deportivo la coruna": "9783",
    "real betis": "8603",
    "betis": "8603",
    "osasuna": "8371",
    "mallorca": "8661",
    "las palmas": "8306",
    "sevilla": "8302",
    "levante": "8581",
    "racing santander": "8696",
    "ad ceuta fc": "357259",
    "ceuta": "357259",
    "sabadell": "4033",
    "eldense": "8288",
    "cordoba": "7869",
    "celta fortuna": "161743",
    "real sociedad b": "161744",
    "fc andorra": "494050",
    "andorra fc": "494050",
    "castellon": "10279",
    "almeria": "9865",
    "leganes": "7854",
    "cadiz": "8385",
    "sporting gijon": "9869",
    "real valladolid": "10281",
    "valladolid": "10281",
    "albacete": "8393",
    "burgos cf": "7876",
    "burgos": "7876",
    "granada": "7878",
    "real oviedo": "8670",
    "oviedo": "8670",
    "eibar": "8372",
    "tenerife": "9867",
    "girona": "7732",

    # --- Premier League (Inglaterra) ---
    "arsenal": "9825",
    "leeds united": "8463",
    "leeds": "8463",
    "aston villa": "10252",
    "brentford": "9937",
    "sunderland": "8472",
    "brighton & hove albion": "10204",
    "brighton": "10204",
    "chelsea": "8455",
    "ipswich town": "9902",
    "ipswich": "9902",
    "fulham": "9879",
    "manchester united": "10260",
    "tottenham hotspur": "8586",
    "tottenham": "8586",
    "crystal palace": "9826",
    "nottingham forest": "10203",
    "hull city": "8667",
    "hull": "8667",
    "everton": "8668",
    "liverpool": "8650",
    "manchester city": "8456",
    "afc bournemouth": "8678",
    "bournemouth": "8678",
    "coventry city": "8669",
    "coventry": "8669",
    "newcastle united": "10261",
    "newcastle": "10261",

    # --- Bundesliga (Alemania) ---
    "borussia dortmund": "9789",
    "dortmund": "9789",
    "werder bremen": "8697",
    "paderborn": "8460",
    "vfb stuttgart": "10269",
    "stuttgart": "10269",
    "hoffenheim": "8226",
    "hamburger sv": "9790",
    "hamburgo": "9790",
    "augsburg": "8406",
    "bayern munchen": "9823",
    "bayern munich": "9823",
    "mainz 05": "9905",
    "mainz": "9905",
    "bayer leverkusen": "8178",
    "leverkusen": "8178",
    "union berlin": "8149",
    "elversberg": "8232",
    "rb leipzig": "178475",
    "leipzig": "178475",
    "eintracht frankfurt": "9810",
    "frankfurt": "9810",
    "1. fc koln": "8722",
    "fc koln": "8722",
    "colonia": "8722",
    "borussia monchengladbach": "9788",
    "monchengladbach": "9788",
    "freiburg": "8358",
    "schalke 04": "10189",

    # --- Ligue 1 (Francia) ---
    "lens": "8588",
    "lyon": "9748",
    "olympique lyonnais": "9748",
    "lille": "8639",
    "le havre": "9746",
    "lorient": "8689",
    "paris fc": "6379",
    "brest": "8521",
    "angers": "8121",
    "paris saint-germain": "9847",
    "psg": "9847",
    "le mans": "8682",
    "monaco": "9829",
    "toulouse": "9941",
    "rennes": "9851",
    "auxerre": "8583",
    "troyes": "10242",
    "marseille": "8592",
    "olympique marseille": "8592",
    "nice": "9831",
    "strasbourg": "9848",

    # --- Serie A (Italia) ---
    "genoa": "10233",
    "fiorentina": "8535",
    "inter": "8636",
    "inter milan": "8636",
    "parma": "10167",
    "napoli": "9875",
    "frosinone": "9891",
    "como": "10171",
    "roma": "8686",
    "lecce": "9888",
    "bologna": "9857",
    "lazio": "8543",
    "monza": "6504",
    "cagliari": "8529",
    "juventus": "9885",
    "sassuolo": "7943",
    "milan": "8564",
    "ac milan": "8564",
    "torino": "9804",
    "udinese": "8600",
    "atalanta": "8524",
    "venezia": "7881",

    # --- Brasileirão (Brasil) ---
    "fluminense": "9863",
    "coritiba": "9767",
    "athletico paranaense": "10273",
    "atletico-mg": "10272",
    "atletico mineiro": "10272",
    "santos": "8514",
    "flamengo": "9770",
    "cruzeiro": "9781",
    "sao paulo": "10277",
    "botafogo": "8517",
    "vasco da gama": "10276",
    "vitoria": "7733",
    "chapecoense": "197693",
    "remo": "1626",
    "gremio": "9769",
    "internacional": "8702",
    "corinthians": "9808",
    "rb bragantino": "109705",
    "mirassol": "163782",

    # --- Liga 1 (Perú) ---
    "deportivo garcilaso": "920788",
    "sport huancayo": "165148",
    "asociacion deportiva tarma": "1104719",
    "adt": "1104719",
    "fc cajamarca": "1696744",
    "comerciantes unidos": "536945",
    "adc juan pablo ii": "1573153",
    "universitario de deportes": "4409",
    "universitario": "4409",
    "fbc melgar": "4417",
    "melgar": "4417",
    "cd ut cajamarca": "425692",
    "utc": "425692",
    "sporting cristal": "1848",
    "sport boys": "4412",
    "alianza atletico": "4410",
    "cusco fc": "305171",
    "alianza lima": "6398",
    "atletico grau": "920789",
    "los chankas": "741328",
    "club deportivo moquegua": "1573140",
    "cienciano": "1845",

    # --- Competiciones UEFA y Otras Ligas ---
    "sabah fk": "951893",
    "slavia prague": "7787",
    "sporting cp": "9768",
    "viking": "8478",
    "galatasaray": "8637",
    "Kasımpaşa": "8630",
    "psv eindhoven": "8640",
    "psv": "8640",
    "club brugge": "8342",
    "lask": "9977",
    "feyenoord": "10235",
    "fenerbahce": "8695",
    "sparta prague": "10247",
    "lillestrom": "8476",
    "nk celje": "4622",
    "omonia nicosia": "8044",
    "salzburg": "10013",
    "az alkmaar": "10229",
    "hapoel beer sheva": "9754",
    "torreense": "212820",
    "union st.gilloise": "7978",
    "lech poznan": "2182",
    "sturm graz": "10014",
    "ofi crete": "7753",
    "ferencvaros": "8222",
    "viktoria plzen": "6033",
    "nec nijmegen": "8464",
    "levski sofia": "8632",
    "dinamo zagreb": "10156",
    "anderlecht": "8635",
    "jagiellonia bialystok": "1957",
    "ararat armenia": "866109",
    "besiktas": "10188",
    "olympiacos": "8638",
    "benfica": "9772",
    "celtic": "9925",
    "Heerenveen": "9926",

    # --- Selecciones Nacionales ---
    "mexico": "6710",
    "chile": "9762",
    "usa": "6713",
    "canada": "5810",
    "new zealand": "5820",
    "india": "6329",
    "turkiye": "6595",
    "belgium": "8263",
    "italy": "8204",
    "france": "6723",
    "england": "8491",
    "croatia": "10155",
    "czechia": "8496",
    "spain": "6720",
    "qatar": "5902",
    "australia": "6716",
    "netherlands": "6708",
    "greece": "6383",
    "serbia": "8205",
    "germany": "8570",
    "norway": "8492",
    "wales": "5790",
    "portugal": "8361",
    "denmark": "8238",
    "andorra": "10045",
    "azerbaijan": "8566",
    "jordan": "5816",
    
    # --- Liga BetPlay (Colombia) ---
    "Alianza": "80002",
    "Rionegro Águilas": "80001",
    "Once Caldas": "80019",
    "Llaneros": "80017",
    "Deportivo Pereira": "80010",
    "Deportivo Cali": "80008",
    "Junior": "80015",
    "Inter Bogotá": "80025",
    
    # --- Liga Profesional (Argentina) ---
    "Aldosivi": "90001",
    "Sarmiento": "90002",
    "Gimnasia La Plata": "90003",
    "Atlético Tucumán": "90004",
    "Instituto": "90005",
    "Boca Juniors": "90006",
    "Unión Santa Fe": "90007",
    "Defensa y Justicia": "90008",
    "Barracas Central": "90009",
    "Huracán": "90010",
    "Central Córdoba SdE": "90011",
    "Estudiantes LP": "90012",
    "Tigre": "90013",
    "Banfield": "90014",
    "River Plate": "90015",
    "Estudiantes Río Cuarto": "90016",
    
    # --- MLS ---
    "Toronto FC": "91001",
    "CF Montréal": "91002",
    "Chicago Fire": "91003",
    "New York City": "91004",
    "Inter Miami": "91005",
    "DC United": "91006",
    "Atlanta United": "91007",
    "Cincinnati": "91008",
    "Orlando City SC": "91009",
    "Columbus Crew": "91010",
    "New York RB": "91011",
    "San Diego": "91012",
    "Charlotte": "91013",
    "Dallas": "91014",
    "Philadelphia Union": "91015",
    "Real Salt Lake": "91016",
    "New England": "91017",
    "Seattle Sounders": "91018",
    "Austin": "91019",
    "Nashville SC": "91020",
    "Minnesota United": "91021",
    "Houston Dynamo": "91022",
    "Sporting KC": "91023",
    "Portland Timbers": "91024",
    "Colorado Rapids": "91025",
    "San Jose Earthquakes": "91026",
    "Los Angeles FC": "91027",
    "Vancouver Whitecaps": "91028",
    
    # --- Championship (Inglaterra) ---
    "West Ham United": "92001",
    "Queens Park Rangers": "92002",
    "West Bromwich": "92003",
    "Birmingham City": "92004",
    "Bolton Wanderers": "92005",
    "Stoke City": "92006",
    "Derby County": "92007",
    "Wrexham": "92008",
    "Watford": "92009",
    "Burnley": "92010",
    
    # --- Primera División (Uruguay) ---
    "Torque": "93001",
    "Danubio": "93002",
    "Deportivo Maldonado": "93003",
    "Liverpool": "8650",
    "Defensor Sporting": "93005",
    "Cerro": "93006",
    "Wanderers": "93007",
    "Boston River": "93008",
    "Peñarol": "93009",
    "Progreso": "93010",

    # --- Primera División (Chile) ---
    "Cobresal": "94001",
    "Universidad de Concepción": "94002",
    "Huachipato": "94003",
    "O'Higgins": "94004",
    "Universidad Católica": "94005",
    "Audax Italiano": "94006",
    
    # --- Süper Lig (Turquía) ---
    "Samsunspor": "95001",
    "Trabzonspor": "95002",
    "Rizespor": "95003",

    # --- Primeira Liga (Portugal) ---
    "Sporting Braga": "95004",
    "Marítimo": "95005",
    "Porto": "95006",

    # --- Bundesliga 2 (Alemania) ---
    "Magdeburg": "95007",
    "Hannover 96": "95008",
    "Nurnberg": "95009",
    "Wolfsburg": "95010",

    # --- Eredivisie (Países Bajos) ---
    "Ajax": "95011",
    "NEC Nijmegen": "8464",
    
    # --- Liga Profesional Saudí ---
    "Al Hilal": "96001",
    "Al Ittihad": "96002",
    "Al Kholood": "1014",
    "Al Quadisiya": "1013",
    "Al Nassr": "6001",
    "Diriyah": "6002"
}

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

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower()

def buscar_imagen(equipo_val):
    if not equipo_val:
        return ""
    nombre_norm = normalizar_texto(equipo_val)
    if nombre_norm in MAPEO_EQUIPOS:
        return f"{BASE_IMG_URL}/{MAPEO_EQUIPOS[nombre_norm]}.png"
    if nombre_norm.isdigit():
        return f"{BASE_IMG_URL}/{nombre_norm}.png"
    filename_slug = nombre_norm.replace(" ", "_")
    if os.path.exists(os.path.join(EQUIPOS_DIR, f"{filename_slug}.png")):
        return f"{BASE_IMG_URL}/{filename_slug}.png"
    return ""

def extraer_liga_y_titulo(titulo_raw):
    """Separa la Liga del Nombre del Partido cuando vienen como 'Liga: Equipo1 vs Equipo2'."""
    if ":" in titulo_raw:
        partes = titulo_raw.split(":", 1)
        liga = partes[0].strip()
        partido = partes[1].strip()
        return liga, partido
    return "Otras Competencias", titulo_raw.strip()

def detectar_deporte(liga, titulo):
    """Determina a qué deporte de la lista pertenece el evento."""
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
    """Extrae el parámetro del canal del link si está presente."""
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

    # Estructura principal agrupada
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

        # Clave única para agrupar servidores/canales del mismo evento
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

        # Agregar servidor/canal correspondiente
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

    # Armar árbol de LigayDeportes según el formato deseado
    for ev in eventos_agrupados.values():
        s_id = ev["sport_id"]
        l_name = ev["league_name"]
        ev_data = ev["event_data"]

        deporte = deportes_dict[s_id]
        
        # Buscar si la liga ya existe dentro del deporte
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

    # Objeto final idéntico a eventos.json
    resultado_final = {
        "sports": list(deportes_dict.values()),
        "updated": f"{fecha} {hora}:00"
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, ensure_ascii=False, indent=4)

    print(f"Agenda generada correctamente con el formato idéntico a eventos.json en {OUTPUT_JSON}")

if __name__ == "__main__":
    procesar_agenda()