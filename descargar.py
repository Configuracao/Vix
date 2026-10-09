import os
import json
import concurrent.futures
import requests

JSON_FILE = "matches.json"
OUTPUT_DIR = os.path.join("assets", "equipos_fm")
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def obtener_ids_equipos(json_path):
    ids = set()
    if not os.path.exists(json_path):
        print(f"Error: No se encontró el archivo {json_path}")
        return ids

    with open(json_path, "r", encoding="utf-8") as f:
        matches = json.load(f)
        for match in matches:
            home_logo = match.get("homeTeam", {}).get("logo")
            if home_logo and str(home_logo).isdigit():
                ids.add(str(home_logo))
            
            away_logo = match.get("awayTeam", {}).get("logo")
            if away_logo and str(away_logo).isdigit():
                ids.add(str(away_logo))

    return ids

# Obtener lista de IDs que YA existen localmente en la carpeta del repo
archivos_existentes = {
    f.replace(".png", "") for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")
}

def descargar_imagen(id_equipo):
    # Si ya existe en la carpeta, omitir de inmediato
    if id_equipo in archivos_existentes:
        print(f"[=] Omitida (ya existe): {id_equipo}.png")
        return

    url = f"https://teledeportes.st/assets/img/ligas/fm/dark/{id_equipo}.png"
    filepath = os.path.join(OUTPUT_DIR, f"{id_equipo}.png")

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"[+] Descargada: {id_equipo}.png -> {filepath}")
        else:
            print(f"[-] No encontrada en servidor ({response.status_code}): {id_equipo}.png")
    except Exception as e:
        print(f"[!] Error descargando {id_equipo}.png: {e}")

equipos_ids = obtener_ids_equipos(JSON_FILE)

# Filtrar solo las IDs faltantes
ids_pendientes = equipos_ids - archivos_existentes

print(f"Total en JSON: {len(equipos_ids)}")
print(f"Ya existentes: {len(archivos_existentes)}")
print(f"Pendientes por descargar: {len(ids_pendientes)}")

if ids_pendientes:
    print("Iniciando descarga de imágenes faltantes...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(descargar_imagen, ids_pendientes)
    print("¡Descarga completada!")
else:
    print("No hay imágenes nuevas para descargar.")