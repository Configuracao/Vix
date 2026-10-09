import os
import concurrent.futures
import requests

# Guardar dentro de la carpeta assets/equipos_fm
OUTPUT_DIR = os.path.join("assets", "equipos_fm")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define el rango de IDs que deseas probar/descargar
INICIO = 1
FIN = 10000

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def descargar_imagen(id_equipo):
    url = f"https://teledeportes.st/assets/img/equipos/fm/{id_equipo}.png"
    filepath = os.path.join(OUTPUT_DIR, f"{id_equipo}.png")
    
    if os.path.exists(filepath):
        return

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"[+] Descargada: {id_equipo}.png -> {filepath}")
    except Exception:
        pass

print("Iniciando descarga masiva...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(descargar_imagen, range(INICIO, FIN + 1))

print("¡Descarga completada!")