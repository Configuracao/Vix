import json
import urllib.parse
from curl_cffi import requests

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
    """Consulta la API impersonando Chrome para evitar bloqueos TLS/JA3."""
    if not event_id:
        return None
    
    api_url = f"{API_BASE_URL}{event_id}"
    try:
        # impersonate="chrome" simula la huella digital TLS real de un navegador
        res = requests.get(api_url, headers=HEADERS, impersonate="chrome", timeout=12)
        print(f"  [-] Consultando API ID '{event_id}' -> HTTP {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            
            # 1. Buscar dentro de content -> media
            content = data.get("content", {})
            if isinstance(content, dict):
                media_list = content.get("media", [])
                for item in media_list:
                    if isinstance(item, dict) and item.get("url"):
                        return item.get("url")
            
            # 2. Búsqueda directa en la raíz del JSON
            if isinstance(data, dict):
                if "url" in data:
                    return data["url"]
                if "stream" in data:
                    return data["stream"]

    except Exception as e:
        print(f"  [!] Error consultando ID {event_id}: {e}")
    return None

def main():
    print(f"[+] Descargando eventos desde: {EVENTS_URL}")
    try:
        res = requests.get(EVENTS_URL, headers=HEADERS, impersonate="chrome", timeout=15)
        if res.status_code != 200:
            print(f"[!] Error HTTP {res.status_code} al descargar eventos.json")
            return
        events = res.json()
    except Exception as e:
        print(f"[!] Error al obtener el JSON principal: {e}")
        return

    print(f"[+] Se encontraron {len(events)} eventos.")
    m3u_lines = ["#EXTM3U\n"]
    valid_count = 0

    for idx, event in enumerate(events, start=1):
        title = event.get("title", f"Evento {idx}")
        category = event.get("desc", "Deportes")
        logo = event.get("img", "")
        
        # Evaluar múltiples opciones si existen
        urls_to_check = []
        opciones = event.get("opciones")
        
        if isinstance(opciones, dict):
            for opt_name, opt_url in opciones.items():
                urls_to_check.append((f"{title} ({opt_name})", opt_url))
        
        if not urls_to_check:
            main_url = event.get("url")
            if main_url:
                urls_to_check.append((title, main_url))

        # Procesar cada entrada
        for item_title, raw_url in urls_to_check:
            event_id = extract_id_from_url(raw_url)
            print(f"-> [{idx}/{len(events)}] Procesando: '{item_title}' | ID: {event_id}")
            
            stream_url = fetch_m3u8(event_id)
            
            if stream_url:
                valid_count += 1
                m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}", {item_title}\n')
                m3u_lines.append(f'{stream_url}\n\n')

    print(f"\n[+] Total de enlaces generados con éxito: {valid_count}")

    with open("eventos.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("[+] Archivo 'eventos.m3u' generado correctamente.")

if __name__ == "__main__":
    main()
