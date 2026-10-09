import os
import json
import requests
import unicodedata
import re
import urllib.parse
from datetime import datetime, timedelta

# URL del JSON original
JSON_URL = "https://streamx305.sbs/json/agenda550.json"
# Ruta local donde se guardará el JSON procesado
OUTPUT_JSON = "agenda.json"
# Carpeta donde están alojadas las imágenes de los equipos
EQUIPOS_DIR = os.path.join("assets", "equipos_fm")
# Base URL pública en GitHub para servir las imágenes
BASE_IMG_URL = "https://raw.githubusercontent.com/Configuracao/Vix/main/assets/equipos_fm"

MAPEO_EQUIPOS = {
    # --- Liga MX ---
    "puebla": "7847", "club puebla": "7847", "leon": "1841", "club leon": "1841",
    "tigres": "8561", "tigres uanl": "8561", "toluca": "6618", "fc juarez": "649424",
    "juarez": "649424", "tijuana": "162418", "xolos": "162418", "queretaro": "1943",
    "queretaro fc": "1943", "atlante": "1942", "atlas": "6577", "chivas": "7807",
    "chivas guadalajara": "7807", "guadalajara": "7807", "cf america": "6576",
    "america": "6576", "club america": "6576", "monterrey": "7849", "rayados": "7849",
    "atletico de san luis": "6358", "atletico san luis": "6358", "san luis": "6358",
    "santos laguna": "7857", "santos lagunas": "7857", "pachuca": "7848",
    "necaxa": "1842", "pumas": "1946", "pumas unam": "1946", "cruz azul": "6578",

    # --- LaLiga & LaLiga2 (España) ---
    "malaga": "9864", "espanyol": "8558", "rayo vallecano": "8370", "athletic club": "8315",
    "athletic bilbao": "8315", "deportivo alaves": "9866", "alaves": "9866",
    "atletico madrid": "9906", "atletico de madrid": "9906", "barcelona": "8634",
    "fc barcelona": "8634", "getafe": "8305", "real madrid": "8633", "villarreal": "10205",
    "elche": "10268", "celta vigo": "9910", "celta de vigo": "9910", "celta": "9910",
    "real sociedad": "8560", "deportivo a coruna": "9783", "deportivo la coruna": "9783",
    "real betis": "8603", "betis": "8603", "osasuna": "8371", "mallorca": "8661",
    "las palmas": "8306", "sevilla": "8302", "levante": "8581", "racing santander": "8696",
    "ad ceuta fc": "357259", "ceuta": "357259", "sabadell": "4033", "eldense": "8288",
    "cordoba": "7869", "celta fortuna": "161743", "real sociedad b": "161744",
    "fc andorra": "494050", "andorra fc": "494050", "castellon": "10279", "almeria": "9865",
    "leganes": "7854", "cadiz": "8385", "sporting gijon": "9869", "real valladolid": "10281",
    "valladolid": "10281", "albacete": "8393", "burgos cf": "7876", "burgos": "7876",
    "granada": "7878", "real oviedo": "8670", "oviedo": "8670", "eibar": "8372",
    "tenerife": "9867", "girona": "7732",

    # --- Premier League (Inglaterra) ---
    "arsenal": "9825", "leeds united": "8463", "leeds": "8463", "aston villa": "10252",
    "brentford": "9937", "sunderland": "8472", "brighton & hove albion": "10204",
    "brighton": "10204", "chelsea": "8455", "ipswich town": "9902", "ipswich": "9902",
    "fulham": "9879", "manchester united": "10260", "tottenham hotspur": "8586",
    "tottenham": "8586", "crystal palace": "9826", "nottingham forest": "10203",
    "hull city": "8667", "hull": "8667", "everton": "8668", "liverpool": "8650",
    "manchester city": "8456", "afc bournemouth": "8678", "bournemouth": "8678",
    "coventry city": "8669", "coventry": "8669", "newcastle united": "10261", "newcastle": "10261",

    # --- Bundesliga (Alemania) ---
    "borussia dortmund": "9789", "dortmund": "9789", "werder bremen": "8697", "paderborn": "8460",
    "vfb stuttgart": "10269", "stuttgart": "10269", "hoffenheim": "8226", "hamburger sv": "9790",
    "hamburgo": "9790", "augsburg": "8406", "bayern munchen": "9823", "bayern munich": "9823",
    "mainz 05": "9905", "mainz": "9905", "bayer leverkusen": "8178", "leverkusen": "8178",
    "union berlin": "8149", "elversberg": "8232", "rb leipzig": "178475", "leipzig": "178475",
    "eintracht frankfurt": "9810", "frankfurt": "9810", "1. fc koln": "8722", "fc koln": "8722",
    "colonia": "8722", "borussia monchengladbach": "9788", "monchengladbach": "9788",
    "freiburg": "8358", "schalke 04": "10189",

    # --- Ligue 1 (Francia) ---
    "lens": "8588", "lyon": "9748", "olympique lyonnais": "9748", "lille": "8639",
    "le havre": "9746", "lorient": "8689", "paris fc": "6379", "brest": "8521",
    "angers": "8121", "paris saint-germain": "9847", "psg": "9847", "le mans": "8682",
    "monaco": "9829", "toulouse": "9941", "rennes": "9851", "auxerre": "8583",
    "troyes": "10242", "marseille": "8592", "olympique marseille": "8592", "nice": "9831", "strasbourg": "9848",

    # --- Serie A (Italia) ---
    "genoa": "10233", "fiorentina": "8535", "inter": "8636", "inter milan": "8636",
    "parma": "10167", "napoli": "9875", "frosinone": "9891", "como": "10171",
    "roma": "8686", "lecce": "9888", "bologna": "9857", "lazio": "8543",
    "monza": "6504", "cagliari": "8529", "juventus": "9885", "sassuolo": "7943",
    "milan": "8564", "ac milan": "8564", "torino": "9804", "udinese": "8600",
    "atalanta": "8524", "venezia": "7881",

    # --- Brasileirão (Brasil) ---
    "fluminense": "9863", "coritiba": "9767", "athletico paranaense": "10273", "atletico-mg": "10272",
    "atletico mineiro": "10272", "santos": "8514", "flamengo": "9770", "cruzeiro": "9781",
    "sao paulo": "10277", "botafogo": "8517", "vasco da gama": "10276", "vitoria": "7733",
    "chapecoense": "197693", "remo": "1626", "gremio": "9769", "internacional": "8702",
    "corinthians": "9808", "rb bragantino": "109705", "mirassol": "163782",

    # --- Liga 1 (Perú) ---
    "deportivo garcilaso": "920788", "sport huancayo": "165148", "asociacion deportiva tarma": "1104719",
    "adt": "1104719", "fc cajamarca": "1696744", "comerciantes unidos": "536945",
    "adc juan pablo ii": "1573153", "universitario de deportes": "4409", "universitario": "4409",
    "fbc melgar": "4417", "melgar": "4417", "cd ut cajamarca": "425692", "utc": "425692",
    "sporting cristal": "1848", "sport boys": "4412", "alianza atletico": "4410",
    "cusco fc": "305171", "alianza lima": "6398", "atletico grau": "920789",
    "los chankas": "741328", "club deportivo moquegua": "1573140", "cienciano": "1845",

    # --- Competiciones UEFA y Otras Ligas ---
    "sabah fk": "951893", "slavia prague": "7787", "sporting cp": "9768", "viking": "8478",
    "galatasaray": "8637", "Kasımpaşa": "8630", "psv eindhoven": "8640", "psv": "8640",
    "club brugge": "8342", "lask": "9977", "feyenoord": "10235", "fenerbahce": "8695",
    "sparta prague": "10247", "lillestrom": "8476", "nk celje": "4622", "omonia nicosia": "8044",
    "salzburg": "10013", "az alkmaar": "10229", "hapoel beer sheva": "9754", "torreense": "212820",
    "union st.gilloise": "7978", "lech poznan": "2182", "sturm graz": "10014", "ofi crete": "7753",
    "ferencvaros": "8222", "viktoria plzen": "6033", "nec nijmegen": "8464", "levski sofia": "8632",
    "dinamo zagreb": "10156", "anderlecht": "8635", "jagiellonia bialystok": "1957",
    "ararat armenia": "866109", "besiktas": "10188", "olympiacos": "8638", "benfica": "9772",
    "celtic": "9925", "Heerenveen": "9926",

    # --- Selecciones Nacionales ---
    "mexico": "6710", "chile": "9762", "usa": "6713", "canada": "5810", "new zealand": "5820",
    "india": "6329", "turkiye": "6595", "belgium": "8263", "italy": "8204", "france": "6723",
    "england": "8491", "croatia": "10155", "czechia": "8496", "spain": "6720", "qatar": "5902",
    "australia": "6716", "netherlands": "6708", "greece": "6383", "serbia": "8205",
    "germany": "8570", "norway": "8492", "wales": "5790", "portugal": "8361", "denmark": "8238",
    "andorra": "10045", "azerbaijan": "8566", "jordan": "5816",
    
    # --- LIGA SAUDI ---
    "Al Quadisiya": "1013", "Al Kholood": "1014", "Al Nassr": "6001", "Al Draih": "6002",
    
    # --- LIGA ARGENTINA ---
    "Aldosivi": "5001", "Sarmiento": "5002"
}

# Mapeo de nombres locales/completos al nombre simplificado esperado por TheSportsDB
MAPEO_NOMBRES_API = {
    "olympique lyonnais": "lyon",
    "olympique de lyon": "lyon",
    "olympique marseille": "marseille",
    "olympique de marseille": "marseille",
    "paris saint-germain": "psg",
    "paris saint germain": "psg",
    "atletico de madrid": "atletico madrid",
    "athletic bilbao": "athletic club",
    "chivas guadalajara": "chivas",
    "club america": "america",
    "cf america": "america",
    "tigres uanl": "tigres",
    "brighton & hove albion": "brighton",
    "tottenham hotspur": "tottenham",
    "bayern munchen": "bayern munich",
    "bayern munich": "bayern munich",
    "diriyah": "al diriyah",
    "al draih": "al diriyah",
    "al draiah": "al diriyah",
}

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower()

def buscar_imagen(equipo_val):
    if not equipo_val:
        return ""
    if isinstance(equipo_val, dict):
        logo_id = str(equipo_val.get("logo", "")).strip()
        if logo_id and logo_id.isdigit():
            return f"{BASE_IMG_URL}/{logo_id}.png"
        nombre = equipo_val.get("name", "")
        return buscar_imagen(nombre)

    nombre_norm = normalizar_texto(str(equipo_val))
    if nombre_norm in MAPEO_EQUIPOS:
        id_img = MAPEO_EQUIPOS[nombre_norm]
        return f"{BASE_IMG_URL}/{id_img}.png"

    if nombre_norm.isdigit():
        return f"{BASE_IMG_URL}/{nombre_norm}.png"

    filename_slug = nombre_norm.replace(" ", "_")
    if os.path.exists(os.path.join(EQUIPOS_DIR, f"{filename_slug}.png")):
        return f"{BASE_IMG_URL}/{filename_slug}.png"

    return ""

def extraer_equipos(evento):
    if "homeTeam" in evento and "awayTeam" in evento:
        home = evento["homeTeam"]
        away = evento["awayTeam"]
        home_name = home.get("name", "") if isinstance(home, dict) else str(home)
        away_name = away.get("name", "") if isinstance(away, dict) else str(away)
        return home, away, home_name, away_name

    titulo = evento.get("title", "")
    if " vs " in titulo:
        partes = titulo.split(":")
        match_str = partes[-1] if len(partes) > 1 else titulo
        equipos = match_str.split(" vs ")
        home_name = equipos[0].strip() if len(equipos) > 0 else ""
        away_name = equipos[1].strip() if len(equipos) > 1 else ""
        return home_name, away_name, home_name, away_name

    return None, None, "", ""

def obtener_duracion_estimada(titulo):
    """Calcula minutos de duración según la categoría/deporte."""
    txt = titulo.lower()
    if "f1" in txt or "formula 1" in txt or "motogp" in txt:
        return 120  # F1 / Carreras
    elif "ufc" in txt or "mma" in txt or "box" in txt:
        return 180  # Carteleras de peleas
    elif "nba" in txt or "basket" in txt:
        return 150  # Baloncesto
    elif "tenis" in txt or "tennis" in txt:
        return 180  # Tenis
    return 120  # Fútbol y por defecto

def simplificar_nombre_equipo(nombre):
    """Normaliza texto y reemplaza nombres compuestos por su alias para TheSportsDB."""
    norm = normalizar_texto(nombre)
    if norm in MAPEO_NOMBRES_API:
        norm = MAPEO_NOMBRES_API[norm]
    return norm.replace(" ", "_")

def obtener_event_id_por_browse(home_team, away_team, fecha_str=""):
    """
    Realiza una búsqueda web a https://www.thesportsdb.com/browse?s=home+vs+away
    y extrae el ID numérico del partido respetando la localía y la fecha.
    """
    home_clean = normalizar_texto(home_team)
    away_clean = normalizar_texto(away_team)

    if not home_clean or not away_clean:
        return None

    # Normalizar si hay alias
    if home_clean in MAPEO_NOMBRES_API:
        home_clean = MAPEO_NOMBRES_API[home_clean]
    if away_clean in MAPEO_NOMBRES_API:
        away_clean = MAPEO_NOMBRES_API[away_clean]

    fecha_clean = fecha_str[:10] if fecha_str and len(fecha_str) >= 10 else ""

    query_str = f"{home_clean} vs {away_clean}"
    query_encoded = urllib.parse.quote(query_str)
    url_browse = f"https://www.thesportsdb.com/browse?s={query_encoded}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url_browse, headers=headers, timeout=5)
        if res.status_code == 200:
            coincidencias = re.findall(r'/event/(\d+)-([a-z0-9\-]+)', res.text.lower())
            
            home_slug = home_clean.replace(" ", "-")
            away_slug = away_clean.replace(" ", "-")

            for event_id, slug in coincidencias:
                # Comprobar que el slug contenga ambos equipos en el orden correcto
                if slug.startswith(home_slug) or (home_slug in slug and away_slug in slug):
                    if fecha_clean:
                        url_lookup = f"https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id={event_id}"
                        try:
                            data_ev = requests.get(url_lookup, timeout=3).json()
                            if data_ev and data_ev.get("events"):
                                ev_date = data_ev["events"][0].get("dateEvent", "")
                                if ev_date == fecha_clean:
                                    return event_id
                        except Exception:
                            pass
                    
                    return event_id
    except Exception as e:
        print(f"Error al consultar browse en TheSportsDB: {e}")

    return None

def obtener_api_url_evento(home_team, away_team, fecha_str=""):
    """
    Genera la URL de la API probando primero por búsqueda web directa (extrae idEvent)
    y en caso de fallo cae al endpoint searchevents.php.
    """
    home_norm = simplificar_nombre_equipo(home_team)
    away_norm = simplificar_nombre_equipo(away_team)

    if not home_norm or not away_norm:
        return ""

    fecha_clean = fecha_str[:10] if fecha_str and len(fecha_str) >= 10 else ""

    # 1. Intentar resolver el ID real a través del buscador web de TheSportsDB
    event_id_web = obtener_event_id_por_browse(home_team, away_team, fecha_str)
    if event_id_web:
        return f"https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id={event_id_web}"

    # 2. Fallback: Usar la API genérica de búsqueda por texto
    if fecha_clean:
        return f"https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e={home_norm}_vs_{away_norm}&d={fecha_clean}"
    
    return f"https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e={home_norm}_vs_{away_norm}"

def procesar_horarios_y_api(evento):
    """Calcula hora inicio, hora fin estimada y asigna la URL de API en tiempo real."""
    
    event_id = evento.get("id") or evento.get("event_id") or ""
    
    if event_id:
        evento["api_url"] = f"https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id={event_id}"
    else:
        home = evento.get("home_team", "")
        away = evento.get("away_team", "")
        fecha = evento.get("date", "")
        evento["api_url"] = obtener_api_url_evento(home, away, fecha)

    time_str = evento.get("time") or evento.get("hora") or ""
    date_str = evento.get("date") or evento.get("fecha") or ""
    
    if time_str:
        evento["hora_inicio"] = time_str
        try:
            duracion_min = obtener_duracion_estimada(evento.get("title", ""))
            
            if date_str and "T" in date_str:
                dt_inicio = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                ho, mi = map(int, time_str.split(":")[:2])
                dt_inicio = datetime.now().replace(hour=ho, minute=mi, second=0)
                
            dt_fin = dt_inicio + timedelta(minutes=duracion_min)
            evento["hora_fin"] = dt_fin.strftime("%H:%M")
        except Exception:
            evento["hora_fin"] = ""
    else:
        evento["hora_inicio"] = evento.get("hora_inicio", "")
        evento["hora_fin"] = evento.get("hora_fin", "")

def procesar_agenda():
    print("Descargando JSON actualizado desde streamx305.sbs...")
    try:
        response = requests.get(JSON_URL, timeout=10)
        if response.status_code != 200:
            print(f"Error al descargar el JSON: Status {response.status_code}")
            return
        agenda = response.json()
    except Exception as e:
        print(f"Error en la petición: {e}")
        return

    # Eliminar archivo antiguo para garantizar reemplazo total
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)

    for evento in agenda:
        home_val, away_val, home_name, away_name = extraer_equipos(evento)
        
        if home_val and away_val:
            home_img = buscar_imagen(home_val)
            away_img = buscar_imagen(away_val)
            
            evento["home_team"] = home_name
            evento["home_img"] = home_img
            evento["away_team"] = away_name
            evento["away_img"] = away_img
            evento["img"] = home_img
        else:
            evento["home_team"] = ""
            evento["home_img"] = ""
            evento["away_team"] = ""
            evento["away_img"] = ""
            evento["img"] = ""

        procesar_horarios_y_api(evento)

    # Reemplazo total creando el archivo desde cero
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(agenda, f, ensure_ascii=False, indent=4)

    print(f"JSON procesado con éxito y reemplazado completamente en {OUTPUT_JSON}")

if __name__ == "__main__":
    procesar_agenda()