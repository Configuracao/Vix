import json
import re
import urllib.parse
import requests

# URL del JSON original de eventos
EVENTS_URL = "https://shplus.240025.xyz/application-config/json/config.json"
API_BASE_URL = "https://shplus.240025.xyz/application-webview/vixplus/json/api/ver.php?id="

def get_event_id(url):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params.get("id", [None])[0]

def extract_m3u8(event_id):
    if not event_id:
        return None
    
    api_url = f"{API_BASE_URL}{event_id}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            media_list = data.get("content", {}).get("media", [])
            for item in media_list:
                if item.get("type") == "application/x-mpegURL":
                    return item.get("url")
    except Exception as e:
        print(f"Error procesando ID {event_id}: {e}")
    return None

def main():
    try:
        res = requests.get(EVENTS_URL, timeout=10)
        events = res.json()
    except Exception as e:
        print(f"Error descargando el JSON de eventos: {e}")
        return

    m3u_lines = ["#EXTM3U\n"]

    for event in events:
        title = event.get("title", "Evento")
        category = event.get("desc", "Deportes")
        logo = event.get("img", "")
        event_url = event.get("url", "")
        
        event_id = get_event_id(event_url)
        stream_url = extract_m3u8(event_id)
        
        if stream_url:
            m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{category}", {title}\n')
            m3u_lines.append(f'{stream_url}\n\n')

    with open("eventos.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("Archivo eventos.m3u generado con éxito.")

if __name__ == "__main__":
    main()