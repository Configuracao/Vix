import json
import urllib.parse
import requests

EVENTS_URL = "https://shplus.240025.xyz/application-config/json/config.json"
API_BASE_URL = "https://shplus.240025.xyz/application-webview/vixplus/json/api/ver.php?id="

# Encabezados para evitar bloqueos por parte del servidor PHP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def get_event_id(url):
    if not url:
        return None
    # Si la URL es simplemente el ID
    if url.isdigit():
        return url
    
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    if "id" in query_params:
        return query_params["id"][0]
    
    # En caso de que la URL termine en /id_del_evento
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
        print(f"[-] Peticion ID {event_id} - HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                print(f"[!] La respuesta de ID {event_id} no es un JSON válido.")
                return None
            
            # 1. Intentar buscar en content -> media
            content = data.get("content", {})
            media_list = content.get("media", []) if isinstance(content, dict) else []
            
            for item in media_list:
                if isinstance(item, dict) and item.get("type") in ["application/x-mpegURL", "hls"]:
                    return item.get("url")
            
            # 2. Si no esta en content.media, buscar directamente en el nivel raiz o en 'stream' / 'url'
            if isinstance(data, dict):
                if "url" in data and str(data["url"]).endswith(".m3u8"):
                    return data["url"]
                if "stream" in data:
                    return data["stream"]

    except Exception as e:
        print(f"[!] Error procesando ID {event_id}: {e}")
    return None

def main():
    print("[+] Obteniendo eventos...")
    try:
        res = requests.get(EVENTS_URL, headers=HEADERS, timeout=12)
        if res.status_code != 200:
            print(f"[!] Error al descargar config.json. Status HTTP: {res.status_code}")
            return
        events = res.json()
    except Exception as e:
        print(f"[!] Error descargando o parseando el JSON de eventos: {e}")
        return

    print(f"[+] Se encontraron {len(events)} eventos en el JSON.")
    m3u_lines = ["#EXTM3U\n"]
    valid_streams = 0

    for idx, event in enumerate(events, start=1):
        title = event.get("title", f"Evento {idx}")
        category = event.get("desc", "Deportes")
        logo = event.get("img", "")
        event_url = event.get("url", "")
        
        event_id = get_event_id(event_url)
        print(f"-> Procesando [{idx}/{len(events)}]: '{title}' (ID: {event_id})")
        
        stream_url = extract_m3u8(event_id)
        
        if stream_url:
            valid_streams += 1
            m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}", {title}\n')
            m3u_lines.append(f'{stream_url}\n\n')

    print(f"[+] Total de transmisiones extraídas: {valid_streams}")

    # Guardar el archivo eventos.m3u
    with open("eventos.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("[+] Archivo 'eventos.m3u' generado exitosamente.")

if __name__ == "__main__":
    main()