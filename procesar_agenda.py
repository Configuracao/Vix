import os
import json
import requests
import unicodedata
import re
import urllib.parse
from datetime import datetime, timedelta

# URL del JSON original con los enlaces de transmisión
JSON_URL = "https://streamx305.sbs/json/agenda550.json"
# Ruta local donde se guardará el JSON procesado
OUTPUT_JSON = "agenda.json"
# Carpeta local de imágenes de respaldo
EQUIPOS_DIR = os.path.join("assets", "equipos_fm")
BASE_IMG_URL = "https://raw.githubusercontent.com/Configuracao/Vix/main/assets/equipos_fm"

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower()

def extraer_equipos(evento):
    """Extrae los nombres del equipo local y visitante del objeto o del título."""
    if "homeTeam" in evento and "awayTeam" in evento:
        home = evento["homeTeam"]
        away = evento["awayTeam"]
        home_name = home.get("name", "") if isinstance(home, dict) else str(home)
        away_name = away.get("name", "") if isinstance(away, dict) else str(away)
        return home_name, away_name

    titulo = evento.get("title", "")
    if " vs " in titulo:
        partes = titulo.split(":")
        match_str = partes[-1] if len(partes) > 1 else titulo
        equipos = match_str.split(" vs ")
        home_name = equipos[0].strip() if len(equipos) > 0 else ""
        away_name = equipos[1].strip() if len(equipos) > 1 else ""
        return home_name, away_name

    return "", ""

def obtener_duracion_estimada(titulo):
    """Calcula minutos de duración según la categoría/deporte."""
    txt = titulo.lower()
    if "f1" in txt or "formula 1" in txt or "motogp" in txt:
        return 120
    elif "ufc" in txt or "mma" in txt or "box" in txt:
        return 180
    elif "nba" in txt or "basket" in txt:
        return 150
    elif "tenis" in txt or "tennis" in txt:
        return 180
    return 120

def buscar_id_evento_web(home_team, away_team, fecha_str=""):
    """
    Busca en TheSportsDB web (browse?s=...) para obtener EXCLUSIVAMENTE la idEvent.
    """
    home_norm = normalizar_texto(home_team)
    away_norm = normalizar_texto(away_team)

    if not home_norm or not away_norm:
        return None

    fecha_clean = fecha_str[:10] if fecha_str and len(fecha_str) >= 10 else ""

    queries = [
        f"{home_norm} vs {away_norm}",
        f"{home_norm}"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for q in queries:
        url_browse = f"https://www.thesportsdb.com/browse?s={urllib.parse.quote(q)}"
        try:
            res = requests.get(url_browse, headers=headers, timeout=5)
            if res.status_code == 200:
                matches = re.findall(r'/event/(\d+)-([a-z0-9\-]+)', res.text.lower())
                
                for event_id, slug in matches:
                    if fecha_clean:
                        try:
                            url_chk = f"https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id={event_id}"
                            data_ev = requests.get(url_chk, timeout=3).json()
                            if data_ev and data_ev.get("events"):
                                ev_date = data_ev["events"][0].get("dateEvent", "")
                                if ev_date == fecha_clean:
                                    return event_id
                        except Exception:
                            pass
                    else:
                        return event_id
        except Exception as e:
            print(f"Error buscando en TheSportsDB para {home_team} vs {away_team}: {e}")

    return None

def obtener_datos_evento_tsdb(event_id):
    """Obtiene los datos oficiales del evento desde TheSportsDB por su ID."""
    url = f"https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id={event_id}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            events = data.get("events")
            if events and len(events) > 0:
                return events[0]
    except Exception:
        pass
    return None

def procesar_agenda():
    print("Descargando eventos con URLs de transmisión desde streamx305.sbs...")
    try:
        response = requests.get(JSON_URL, timeout=10)
        if response.status_code != 200:
            print(f"Error al descargar el JSON: Status {response.status_code}")
            return
        agenda_original = response.json()
    except Exception as e:
        print(f"Error en la petición: {e}")
        return

    agenda_procesada = []

    print(f"Procesando {len(agenda_original)} partidos de la agenda...")

    for evento in agenda_original:
        link_stream = evento.get("link", "").strip()
        
        # Filtro estricto: Solo procesar partidos que tengan URL de transmisión
        if not link_stream:
            continue

        home_team, away_team = extraer_equipos(evento)
        fecha_str = evento.get("date") or evento.get("fecha") or ""
        time_str = evento.get("time") or evento.get("hora") or ""
        
        # 1. Intentar buscar el ID en TheSportsDB
        event_id = evento.get("id") or evento.get("event_id") or ""
        if not event_id and home_team and away_team:
            event_id = buscar_id_evento_web(home_team, away_team, fecha_str)

        # 2. Si se encuentra la ID, consultar la información completa de TheSportsDB
        datos_tsdb = obtener_datos_evento_tsdb(event_id) if event_id else None

        if datos_tsdb:
            # Reemplazar con datos oficiales de TheSportsDB
            nombre_home = datos_tsdb.get("strHomeTeam") or home_team
            nombre_away = datos_tsdb.get("strAwayTeam") or away_team
            img_home = datos_tsdb.get("strHomeTeamBadge") or datos_tsdb.get("strLogo", "")
            img_away = datos_tsdb.get("strAwayTeamBadge", "")
            categoria = datos_tsdb.get("strLeague") or evento.get("category", "Fútbol")
            
            api_url = f"https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id={event_id}"
        else:
            # Si no está en TheSportsDB, usar datos originales pero sin api_url inservible
            nombre_home = home_team
            nombre_away = away_team
            img_home = evento.get("home_img", "")
            img_away = evento.get("away_img", "")
            categoria = evento.get("category", "Fútbol")
            api_url = ""

        # Calcular hora fin estimada
        hora_inicio = time_str
        hora_fin = ""
        if time_str:
            try:
                duracion_min = obtener_duracion_estimada(evento.get("title", ""))
                if fecha_str and "T" in fecha_str:
                    dt_inicio = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                else:
                    ho, mi = map(int, time_str.split(":")[:2])
                    dt_inicio = datetime.now().replace(hour=ho, minute=mi, second=0)
                    
                dt_fin = dt_inicio + timedelta(minutes=duracion_min)
                hora_fin = dt_fin.strftime("%H:%M")
            except Exception:
                hora_fin = ""

        # Construir evento limpio para el JSON final
        evento_final = {
            "category": categoria,
            "link": link_stream,
            "title": evento.get("title", f"{categoria}: {nombre_home} vs {nombre_away}"),
            "time": hora_inicio,
            "status": evento.get("status", "En vivo"),
            "date": fecha_str,
            "home_team": nombre_home,
            "home_img": img_home,
            "away_team": nombre_away,
            "away_img": img_away,
            "img": img_home,
            "api_url": api_url,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin
        }

        agenda_procesada.append(evento_final)

    # Guardar en archivo local reemplazando todo
    if os.path.exists(OUTPUT_JSON):
        os.remove(OUTPUT_JSON)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(agenda_procesada, f, ensure_ascii=False, indent=4)

    print(f"JSON procesado con éxito. Se generó {OUTPUT_JSON} con {len(agenda_procesada)} partidos que contienen URL de transmisión.")

if __name__ == "__main__":
    procesar_agenda()