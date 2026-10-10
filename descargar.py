import os
import concurrent.futures
import requests

OUTPUT_DIR = os.path.join("assets", "equipos_fm")
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Tu diccionario: "Nombre del Equipo": "ID_Inventado"
EQUIPOS_MAPEO = {
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

def buscar_y_descargar_por_nombre(nombre_equipo, id_inventado):
    filepath = os.path.join(OUTPUT_DIR, f"{id_inventado}.png")

    # Realizar búsqueda por el nombre real del equipo en TheSportsDB
    url_api = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={requests.utils.quote(nombre_equipo)}"
    
    try:
        resp = requests.get(url_api, headers=headers, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            teams = data.get("teams")
            if teams and len(teams) > 0:
                # Extraer la URL del escudo oficial
                logo_url = teams[0].get("strBadge") or teams[0].get("strLogo")
                if logo_url:
                    img_data = requests.get(logo_url, headers=headers, timeout=10).content
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    print(f"[+] Éxito: '{nombre_equipo}' descargado y guardado como {id_inventado}.png")
                    return
    except Exception as e:
        print(f"[!] Error procesando '{nombre_equipo}': {e}")

    print(f"[-] No se encontró logo para: '{nombre_equipo}' (ID asignado: {id_inventado})")

def ejecutar():
    # Revisar qué IDs ya están creados en la carpeta local para no descargarlos doble vez
    archivos_existentes = {
        f.replace(".png", "") for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")
    }

    # Filtrar únicamente los equipos que todavía no tienen su archivo físico
    pendientes = {nom: id_eq for nom, id_eq in EQUIPOS_MAPEO.items() if id_eq not in archivos_existentes}

    print(f"Total en lista: {len(EQUIPOS_MAPEO)} equipos")
    print(f"Ya existentes localmente: {len(archivos_existentes)}")
    print(f"Pendientes por descargar: {len(pendientes)}")

    if pendientes:
        print("\nIniciando descargas concurrentes por nombre...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(buscar_y_descargar_por_nombre, nom, id_eq)
                for nom, id_eq in pendientes.items()
            ]
            concurrent.futures.wait(futures)
        print("\n¡Proceso de descarga terminado!")
    else:
        print("\nTodas las imágenes ya se encuentran descargadas en la carpeta.")

if __name__ == "__main__":
    ejecutar()