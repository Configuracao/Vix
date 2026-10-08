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

# Encabezados de transmisión
REFERER = "https://vix.com/"
ORIGIN = "https://vix.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def extract_id_from_url(raw_url):
    """Extrae el parámetro ?id= de una URL dada."""
    if not raw_url or not isinstance(raw_url, str):
        return None
    
    parsed = urllib.parse.urlparse(raw_url)
    qs = urllib.parse.parse_qs(parsed.query)
    if "id" in qs and len(qs["id"]) > 0:
        return qs["id"][0]
    return None

def fetch_event_data(event_id):
    """Consulta la API ver.php?id=..."""
    if not event_id:
        return None
    
    api_url = f"{API_BASE_URL}{event_id}"
    try:
        res = requests.get(api_url, headers=HEADERS, impersonate="chrome", timeout=12)
        print(f"  [-] Consultando API ID '{event_id}' -> HTTP {res.status_code}")
        if res.status_code == 200:
            return res.json()
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
        
        urls_to_check = []
        opciones = event.get("opciones")
        
        if isinstance(opciones, dict):
            for opt_name, opt_url in opciones.items():
                urls_to_check.append((f"{title} ({opt_name})", opt_url))
        
        if not urls_to_check:
            main_url = event.get("url")
            if main_url:
                urls_to_check.append((title, main_url))

        for item_title, raw_url in urls_to_check:
            event_id = extract_id_from_url(raw_url)
            print(f"-> [{idx}/{len(events)}] Procesando: '{item_title}' | ID: {event_id}")
            
            data = fetch_event_data(event_id)
            if not data or not isinstance(data, dict):
                continue

            stream_url = None
            license_url = None

            # Buscar dentro de content -> media (Estructura de Lura Player / ViX)
            content = data.get("content", {})
            if isinstance(content, dict):
                media_list = content.get("media", [])
                
                # Prioridad 1: Buscar DASH (.mpd) con DRM Widevine
                for item in media_list:
                    if isinstance(item, dict) and item.get("type") == "application/dash+xml":
                        stream_url = item.get("url")
                        license_url = item.get("licenseUrl")
                        break
                
                # Prioridad 2: Si no hay DASH, buscar HLS (.m3u8)
                if not stream_url:
                    for item in media_list:
                        if isinstance(item, dict) and item.get("type") == "application/x-mpegURL":
                            stream_url = item.get("url")
                            license_url = item.get("licenseUrl")
                            break

            if stream_url:
                valid_count += 1
                
                # Formatear stream_url con cabeceras
                full_stream_url = f"{stream_url}|Referer={REFERER}|Origin={ORIGIN}|User-Agent={USER_AGENT}"
                
                # Formatear license_key con cabeceras
                if license_url:
                    full_license_key = f"{license_url}|Referer={REFERER}|Origin={ORIGIN}|User-Agent={USER_AGENT}"
                else:
                    full_license_key = ""

                # Escribir la estructura M3U exacta
                m3u_lines.append(f'#EXTINF:-1 tvg-id="" tvg-name="{item_title}" tvg-logo="{logo}" group-title="{category}",{item_title}\n')
                
                if full_license_key:
                    m3u_lines.append('#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha\n')
                    m3u_lines.append(f'#KODIPROP:inputstream.adaptive.license_key={full_license_key}\n')
                
                m3u_lines.append(f'#KODIPROP:inputstream.adaptive.stream_headers=Referer={REFERER}&Origin={ORIGIN}\n')
                m3u_lines.append(f'#EXTVLCOPT:http-referrer={REFERER}\n')
                m3u_lines.append(f'#EXTVLCOPT:http-origin={ORIGIN}\n')
                m3u_lines.append(f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n')
                m3u_lines.append(f'{full_stream_url}\n\n')

    print(f"\n[+] Total de canales procesados con éxito: {valid_count}")

    with open("eventos.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)

    print("[+] Archivo 'eventos.m3u' generado correctamente.")

if __name__ == "__main__":
    main()
