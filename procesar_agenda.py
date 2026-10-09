import os
import json
import requests
import unicodedata

# URL del JSON original
JSON_URL = "https://streamx305.sbs/json/agenda550.json"
# Ruta local donde se guardará el JSON procesado
OUTPUT_JSON = "agenda.json"
# Carpeta donde están alojadas las imágenes de los equipos
EQUIPOS_DIR = os.path.join("assets", "equipos_fm")
# Base URL pública en GitHub para servir las imágenes
BASE_IMG_URL = "https://raw.githubusercontent.com/Configuracao/Vix/main/assets/equipos_fm"

# Mapeo manual únicamente para excepciones conocidas o IDs fijos específicos
MAPEO_EXCEPCIONES = {
    "puebla": "8634",
    "tigres uanl": "8305",
    "tigres": "8305",
    "boca juniors": "8305",
    # Agrega más excepciones si un equipo usa un ID específico que no coincida con su nombre
}

def normalizar_texto(texto):
    """Elimina acentos, caracteres especiales y convierte a minúsculas."""
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.strip().lower()

def buscar_imagen(nombre_equipo):
    """
    Busca la imagen en la carpeta local assets/equipos_fm/
    1. Revisa excepciones manuales.
    2. Revisa si existe un archivo .png numérico o con el nombre normalizado.
    """
    if not nombre_equipo:
        return ""

    nombre_norm = normalizar_texto(nombre_equipo)
    
    # 1. Verificar si existe en excepciones
    if nombre_norm in MAPEO_EXCEPCIONES:
        id_img = MAPEO_EXCEPCIONES[nombre_norm]
        if os.path.exists(os.path.join(EQUIPOS_DIR, f"{id_img}.png")):
            return f"{BASE_IMG_URL}/{id_img}.png"

    # 2. Si el propio nombre ingresado es un ID numérico (ej. "8634")
    if nombre_norm.isdigit():
        if os.path.exists(os.path.join(EQUIPOS_DIR, f"{nombre_norm}.png")):
            return f"{BASE_IMG_URL}/{nombre_norm}.png"

    # 3. Buscar coincidencia directa de archivo por nombre (ej: "puebla.png")
    filename_slug = nombre_norm.replace(" ", "_")
    if os.path.exists(os.path.join(EQUIPOS_DIR, f"{filename_slug}.png")):
        return f"{BASE_IMG_URL}/{filename_slug}.png"

    return ""

def extraer_equipos(titulo):
    """
    Extrae el equipo local (casa) y el visitante (fuera) del título.
    Ejemplo: 'Liga MX: Puebla vs León' -> ('Puebla', 'León')
             'F1 | GP de Singapur...' -> (None, None)
    """
    if " vs " in titulo:
        partes = titulo.split(":")
        match_str = partes[-1] if len(partes) > 1 else titulo
        equipos = match_str.split(" vs ")
        
        home = equipos[0].strip() if len(equipos) > 0 else None
        away = equipos[1].strip() if len(equipos) > 1 else None
        
        return home, away
    return None, None

def procesar_agenda():
    print("Descargando JSON desde streamx305.sbs...")
    try:
        response = requests.get(JSON_URL, timeout=10)
        if response.status_code != 200:
            print(f"Error al descargar el JSON: Status {response.status_code}")
            return
        agenda = response.json()
    except Exception as e:
        print(f"Error en la petición: {e}")
        return

    for evento in agenda:
        titulo = evento.get("title", "")
        home_team, away_team = extraer_equipos(titulo)
        
        if home_team and away_team:
            home_img = buscar_imagen(home_team)
            away_img = buscar_imagen(away_team)
            
            evento["home_team"] = home_team
            evento["home_img"] = home_img
            evento["away_team"] = away_team
            evento["away_img"] = away_img
            
            # Mantener 'img' igual a 'home_img' para no romper compatibilidad previa
            evento["img"] = home_img
        else:
            evento["home_team"] = ""
            evento["home_img"] = ""
            evento["away_team"] = ""
            evento["away_img"] = ""
            evento["img"] = ""

    # Guardar el JSON actualizado
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(agenda, f, ensure_ascii=False, indent=4)

    print(f"JSON procesado con éxito y guardado en {OUTPUT_JSON}")

if __name__ == "__main__":
    procesar_agenda()
