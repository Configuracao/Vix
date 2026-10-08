import json
import urllib.parse
import requests

# URL correcta de eventos
EVENTS_URL = "https://shplus.240025.xyz/application-webview/eventos.json"
API_BASE_URL = "https://shplus.240025.xyz/application-webview/vixplus/json/api/ver.php?id="

# Encabezados HTTP para evitar bloqueos del servidor PHP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def get_event_id(url):
    if not url:
        return None
    if isinstance(url, int) or url.isdigit():
        return str(url)
    
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    if "id" in query_params:
        return query_params["id"][0]
    
    path_parts = parsed_url.path.strip("/").split("/")
    if path_parts and path_parts[-1].isdigit():
        return path_parts[-1]
        
    return None

def extract_m3u8(event_id):
    if not event_id:
        return None
    
    api_url = f"{API_BASE_URL}{event_id}"
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=12)
        print(f"  [-] Petición API ID {event_id} -> HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                print(f"  [!] La respuesta para el ID {event_id} no es un JSON válido.")
                return None
            
            # Buscar en content -> media
            content = data.get("content", {})
            media_list = content.get("media", []) if isinstance(content, dict) else []
            
            for item in media_list:
                if isinstance(item, dict) and item.get("type") in ["application/x-mpegURL", "hls"]:
                    return item.get("url")
            
            # Búsqueda alternativa en niveles raíz
            if isinstance(data, dict):
                if "url" in data and str(data["url"]).endswith(".m3u8"):
                    return data["url"]
                if "stream" in data:
                    return data["stream"]

    except Exception as e:
        print(f"  [!] Error al obtener M3U8 para ID {event_id}: {e}")
    return None

def main():
    print(f"[+] Obteniendo eventos desde: {EVENTS_URL}")
    try:
        res = requests.get(EVENTS_URL, headers=HEADERS, timeout=12)
        if res.status_code != 200:
            print(f"[!] Error al descargar eventos.json. Código HTTP: {res.status_code}")
            return
        events = res.json()
    except Exception as e:
        print(f"[!] Error al descargar o parsear el JSON de eventos: {e}")
        return

    print(f"[+] Se obtuvieron {len(events)} eventos.")
    m3u_lines = ["#EXTM3U\n"]
    valid_streams = 0

    for idx, event in enumerate(events, start=1):
        title = event.get("title", f"Evento {idx}")
        category = event.get("desc", "Deportes")
        logo = event.get("img", "")
        event_url = event.get("url", "")
        
        event_id = get_event_id(event_url)
        print(f"-> [{idx}/{len(events)}] Procesando '{title}' (ID: {event_id})")
        
        stream_url = extract_m3u8(event_id)
        
        if stream_url:
            valid_streams += 1
            m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}", {title}\n')
            m3u_lines.append(f'{stream_url}\n\n')

    print(f"[+] Total de eventos con enlace .m3u8 válido: {valid_streams}")

    with open("eventos.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("[+] Archivo 'eventos.m3u' generado correctamente.")

if __name__ == "__main__":
    main()