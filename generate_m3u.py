import json
import urllib.parse
import requests

EVENTS_URL = "https://shplus.240025.xyz/application-webview/eventos.json"
API_BASE_URL = "https://shplus.240025.xyz/application-webview/vixplus/json/api/ver.php?id="

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://shplus.240025.xyz/"
}

def extract_id_from_url(raw_url):
    """Extrae el parámetro ?id= de una URL dada."""
    if not raw_url or not isinstance(raw_url, str):
        return None
    
    parsed = urllib.parse.urlparse(raw_url)
    qs = urllib.parse.parse_qs(parsed.query)
    if "id" in qs and len(qs["id"]) > 0:
        return qs["id"][0]
    return None

def fetch_m3u8(event_id):
    """Consulta la API ver.php?id=... y retorna el enlace m3u8."""
    if not event_id:
        return None
    
    api_url = f"{API_BASE_URL}{event_id}"
    try:
        res = requests.get(api_url, headers=HEADERS, timeout=10)
        print(f"  [-] Consultando API con ID '{event_id}' -> HTTP {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            
            # Buscar en content -> media -> url
            content = data.get("content", {})
            if isinstance(content, dict):
                media_list = content.get("media", [])
                for item in media_list:
                    if isinstance(item, dict) and item.get("url"):
                        return item.get("url")
            
            # Fallback directos
            if isinstance(data, dict):
                if "url" in data:
                    return data["url"]
                if "stream" in data:
                    return data["stream"]

    except Exception as e:
        print(f"  [!] Error al obtener M3U8 para ID {event_id}: {e}")
    return None

def main():
    print(f"[+] Descargando eventos.json desde: {EVENTS_URL}")
    try:
        res = requests.get(EVENTS_URL, headers=HEADERS, timeout=12)
        if res.status_code != 200:
            print(f"[!] Error HTTP {res.status_code} al descargar eventos.json")
            return
        events = res.json()
    except Exception as e:
        print(f"[!] Error al procesar JSON: {e}")
        return

    print(f"[+] Se encontraron {len(events)} eventos.")
    m3u_lines = ["#EXTM3U\n"]
    valid_count = 0

    for idx, event in enumerate(events, start=1):
        title = event.get("title", f"Evento {idx}")
        category = event.get("desc", "Deportes")
        logo = event.get("img", "")
        
        # 1. Intentar obtener IDs desde la clave 'opciones' si existe
        urls_to_check = []
        opciones = event.get("opciones")
        if isinstance(opciones, dict):
            for opt_name, opt_url in opciones.items():
                urls_to_check.append((f"{title} ({opt_name})", opt_url))
        
        # 2. Si no hay opciones, usar la propiedad 'url' principal
        if not urls_to_check:
            main_url = event.get("url")
            if main_url:
                urls_to_check.append((title, main_url))

        # Procesar cada URL/Opción del evento
        for item_title, raw_url in urls_to_check:
            event_id = extract_id_from_url(raw_url)
            print(f"-> [{idx}/{len(events)}] Processing: '{item_title}' | ID: {event_id}")
            
            stream_url = fetch_m3u8(event_id)
            if stream_url:
                valid_count += 1
                m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}", {item_title}\n')
                m3u_lines.append(f'{stream_url}\n\n')

    print(f"\n[+] Total de enlaces reproducibles generados: {valid_count}")

    with open("eventos.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("[+] Archivo 'eventos.m3u' guardado con éxito.")

if __name__ == "__main__":
    main()
