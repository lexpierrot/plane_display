import requests
import re

def fetch_metar(station="KSAN"):
    url = f"https://aviationweather.gov/api/data/metar?ids={station}&format=raw"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        metar_raw = response.text.strip()
        return metar_raw
    except Exception as e:
        print(f"Failed to fetch METAR: {e}")
        return None

def parse_metar(metar):
    if not metar:
        return {}

    # IFR detection
    ifr = any(code in metar for code in ["BKN", "OVC", "VV", "FG", "BR", "TSRA"])
    ifr_status = "IFR" if ifr else "VFR"
    ifr_msg = "Caution" if ifr else "No Warnings"
    ifr_color = "#B51700" if ifr else "#017100"

    # Temperature
    temp_match = re.search(r' (\d{2})/(\d{2}) ', metar)
    temp = f"{temp_match.group(1)}°C" if temp_match else "N/A"

    # Clouds
    clouds = re.findall(r'(FEW|SCT|BKN|OVC)(\d{3})', metar)
    if clouds:
        main = clouds[-1]  # Assume last layer is ceiling
        ceiling_ft = int(main[1]) * 100
        cloud_status = f"{ceiling_ft:,} FT"
        cloud_msg = {
            "FEW": "Few Clouds",
            "SCT": "Scattered Clouds",
            "BKN": "Broken Ceiling",
            "OVC": "Overcast"
        }.get(main[0], "Ceiling")
        if ceiling_ft < 1000:
            cloud_color = "#B51700"
        elif ceiling_ft < 3000: 
            cloud_color = "#DC582A"
        else:
            cloud_color = "#017100"
    else:
        cloud_status = "N/A"
        cloud_msg = "Clear"
        cloud_color = "#5E5E5E"

    # Wind
    wind_match = re.search(r' (\d{3})(\d{2})KT', metar)
    if wind_match:
        wind_status = f"{int(wind_match.group(2))} KTS"
        wind_msg = f"{wind_match.group(1)}°"
        if int(wind_match.group(2)) < 5:
            wind_color = "#B51700"
        elif int(wind_match.group(2)) < 15: 
            wind_color = "#DC582A"
        else:  
            wind_color = "#017100"
    else:
        wind_status = "CALM"
        wind_msg = "000°"
        wind_color = "#5E5E5E"

    # Visibility
    vis_match = re.search(r' (\d{1,2})SM ', metar)
    vis_status = f"{vis_match.group(1)} SM" if vis_match else "N/A"
    vis_msg = "Visibility"
    if vis_match:
        if int(vis_match.group(1)) < 3:
            vis_color = "#B51700"
        elif int(vis_match.group(1)) < 5: 
            vis_color = "#DC582A"
        else:
            vis_color = "#017100"
    else:
        vis_color = "#5E5E5E"

    # Altimeter
    baro_match = re.search(r' A(\d{4})', metar)
    if baro_match:
        baro_inhg = f"{int(baro_match.group(1)) / 100:.2f} inHg"
    else:
        baro_inhg = "N/A"

    return {
        "ifr_status": ifr_status,
        "ifr_msg": ifr_msg,
        "ifr_color": ifr_color,
        "weather_status": temp,
        "weather_msg": cloud_msg,
        "cloud_color": cloud_color,
        "wind_status": wind_status,
        "wind_msg": wind_msg,
        "wind_color": wind_color,
        "vis_status": vis_status,
        "vis_msg": vis_msg,
        "vis_color": vis_color,
        "cloud_status": cloud_status,
        "cloud_msg": "Ceiling",
        "cloud_color": cloud_color,
        "baro_status": baro_inhg,
    }

# Example usage:
metar = fetch_metar("KSAN")
parsed = parse_metar(metar)
print(parsed)