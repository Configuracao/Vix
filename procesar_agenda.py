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
    "club leon": "1841",
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
    
    # --- LIGA SAUDI ---
    "Al Quadisiya": "1013",
    "Al Kholood": "1014",
    "Al Nassr": "6001",
    "Al Draih": "6002",
    
    # --- LIGA ARGENTINA ---
    "Aldosivi": "5001",
    "Sarmiento": "5002"
}

def normalizar_texto(texto):
    """Elimina acentos, caracteres especiales y convierte a minúsculas."""
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower()

def buscar_imagen(equipo_val, logo_fallback=""):
    """
    Busca la imagen del equipo en el mapeo local o mediante ID/Slug.
    Si no encuentra ninguna, utiliza el 'logo_fallback' proporcionado en el evento original.
    """
    if not equipo_val and not logo_fallback:
        return ""

    nombre_norm = normalizar_texto(equipo_val)

    # 1. Buscar en el mapeo por nombre
    if nombre_norm in MAPEO_EQUIPOS:
        id_img = MAPEO_EQUIPOS[nombre_norm]
        return f"{BASE_IMG_URL}/{id_img}.png"

    # 2. Si es un ID numérico directo
    if nombre_norm.isdigit():
        return f"{BASE_IMG_URL}/{nombre_norm}.png"

    # 3. Fallback por slug en carpeta local
    filename_slug = nombre_norm.replace(" ", "_")
    if os.path.exists(os.path.join(EQUIPOS_DIR, f"{filename_slug}.png")):
        return f"{BASE_IMG_URL}/{filename_slug}.png"

    # 4. Usar la URL que ya traía el evento si no se encontró coincidencia local
    return logo_fallback

def procesar_agenda_estructurada():
    print("Obteniendo JSON de eventos...")
    try:
        response = requests.get(JSON_URL, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return

    # Si la respuesta es una lista directa de eventos o contiene 'sports'
    sports = data.get("sports", []) if isinstance(data, dict) else []

    for sport in sports:
        for league in sport.get("leagues", []):
            for evento in league.get("events", []):
                home_team = evento.get("homeTeam", "")
                away_team = evento.get("awayTeam", "")
                
                # Mapear/procesar imágenes de equipos
                home_img = buscar_imagen(home_team, evento.get("homeLogo", ""))
                away_img = buscar_imagen(away_team, evento.get("awayLogo", ""))
                
                # Asignar propiedades al evento
                evento["home_team"] = home_team
                evento["home_img"] = home_img
                evento["away_team"] = away_team
                evento["away_img"] = away_img
                
                # Mantener compatibilidad de URLs asignadas
                if home_img:
                    evento["homeLogo"] = home_img
                if away_img:
                    evento["awayLogo"] = away_img

    # Guardar resultado
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"JSON procesado con éxito y guardado en {OUTPUT_JSON}")

if __name__ == "__main__":
    procesar_agenda_estructurada()