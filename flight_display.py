# flight_display.py
# ---------------------------------------------
# Flight Display Application
# ---------------------------------------------
# This script displays live flight and weather data for KSAN airport using PyQt5.
# It fetches flight info from Flightradar24 and weather info from METAR.
# The UI is designed for a 1920x440 display, showing flight, weather, and approach info.
#
# Setup:
# - Place your API key in 'api_key.txt' in the project root.
# - Ensure assets (CSV, images, fonts) are present in the correct folders.
# - See README.md for full instructions.
# ---------------------------------------------

import sys
import requests
import yaml
import json
import time
import csv

from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QFont, QPainter, QBrush, QColor, QPainterPath, QFontDatabase, QGuiApplication
from PyQt5.QtCore import Qt, QTimer, QDateTime, QRectF
from datetime import datetime, timedelta
from metar import fetch_metar, parse_metar

# -------------------
# Global Variables
# -------------------
last_metar_fetch = 0
last_flight_fetch = 0
cached_parsed_metar = {}
cached_flight_info = {}
flight_captured = False
flight_captured_time = 0
flight_captured_info = {}
debug = False

# -------------------
# Configuration
# -------------------
# Read API key from file
with open("api_key.txt", "r") as f:
    API_TOKEN = f.read().strip()

# Read main config from YAML file
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

FPM_LANDING = config["FPM_LANDING"]
TDZE = config["TDZE"]
AIRPORT_CODE = config["AIRPORT_CODE"]
ALT_MONITOR = config["ALT_MONITOR"]
METAR_CODE = config["METAR_CODE"]
DEFAULT_ARRIVAL_CITY = config["DEFAULT_ARRIVAL_CITY"]
font_path = config["font_path"]
fallback_font = config["fallback_font"]
logo_map_path = config["logo_map_path"]
logo_folder = config["logo_folder"]
default_logo = config["default_logo"]
airport_csv = config["airport_csv"]
plane_icon = config["plane_icon"]
landing_path = config["landing_path"]
plane_image = config["plane_image"]
ui_positions = config["ui_positions"]
debug_values = config["debug_values"]

# -------------------
# Load airport names from CSV
# -------------------
airport_names = {}
with open(airport_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        airport_names[row["key"]] = row["city"]

# -------------------
# API Endpoints
# -------------------
url = config["api_url"]
params = {
    'bounds': config["bounds"],
    'airports': f'inbound:{AIRPORT_CODE}',
    'altitude_ranges': f'0-{ALT_MONITOR}',
}
headers = {
    'Accept': 'application/json',
    'Accept-Version': config["accept_version"],
    'Authorization': f'Bearer {API_TOKEN}'
}

# -------------------
# Airline Logo Mapping
# -------------------
with open(logo_map_path, "r") as f:
    logo_map = yaml.safe_load(f)

# -------------------
# Utility Functions
# -------------------
def time_diff(t1, t2):
    """Calculate time difference between two HH:MM strings."""
    fmt = "%H:%M"
    dt1 = datetime.strptime(t1, fmt)
    dt2 = datetime.strptime(t2, fmt)
    diff = abs(dt2 - dt1)
    return f"{diff.seconds // 3600:02}:{(diff.seconds % 3600) // 60:02}"

def get_display_data():
    global last_metar_fetch, cached_parsed_metar, last_flight_fetch, cached_flight_info
    global flight_captured, flight_captured_time, flight_captured_info


    display_data = {
        "flight_number": "MONITORING",
        "callsign": "---",
        "departure_code": "---",
        "departure_city": " ",
        "arrival_code": "SAN",
        "arrival_city": "San Diego, CA",
        "aircraft": "",
        "departure_time": "--:--",
        "arrival_time": "--:--",
        "delay": "",
        "status": "",
        "status_color": "green",
        "altitude": "---- FT",
        "calculated_altitude": 0,
        "calculated_distance": 0,
        "speed": "--- KTS",
        "distance": "--- NM",
        "duration": "--:--XX",
        "clock": QDateTime.currentDateTimeUtc().toString("HH:mm:ss"),
        "ifr_status": "---",
        "ifr_msg": "",
        "weather_status": "--.-°C",
        "weather_msg": "",
        "wind_status": "-- KTS",
        "wind_msg": "",
        "vis_status": "-- SM",
        "vis_msg": "Visibility",
        "cloud_status": "---- FT",
        "cloud__msg": "Ceiling",
        "baro_status": "--.-- inHg",
    }

    now = time.time()
    if now - last_metar_fetch > 300:  # 300 seconds = 5 minutes
        metar = fetch_metar(METAR_CODE)
        cached_parsed_metar = parse_metar(metar)
        print("METAR fetched: ", cached_parsed_metar)
        last_metar_fetch = now
    
    display_data.update(cached_parsed_metar)
    display_data["arrival_city"] = DEFAULT_ARRIVAL_CITY

    if flight_captured:
        now = time.time()
        time_elapsed = now - flight_captured_time
        display_data = flight_captured_info.copy()
        display_data["calculated_altitude"] = flight_captured_info['calculated_altitude'] - FPM_LANDING*time_elapsed/60
        alt_disp = int(display_data["calculated_altitude"])
        alt_disp = max(TDZE, alt_disp) 
        display_data["altitude"]= str(alt_disp)+ " FT"
        display_data["calculated_distance"] = display_data["calculated_altitude"] * 5.0 / 2000

        if display_data["calculated_altitude"]>2000:
            display_data["status"] = "APPROACH"
            display_data["status_color"] = "#004D80"
        elif display_data["calculated_altitude"]>TDZE:
            display_data["status"] = "FINAL"
            display_data["status_color"] = "#E57301"
        else:
            display_data["status"] = "LANDED"
            display_data["status_color"] = "#017100"
        #print(f"Altitude: {display_data['calculated_altitude']}, Distance: {display_data['calculated_distance']}")
    else:
        if not debug and now - last_flight_fetch > 15:  # 300 seconds = 5 minutes
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                print(json.dumps(data, indent=4))
                
                last_flight_fetch = now
                if data and data.get("data"):
                    cached_flight_info = data["data"][0]
                
                    url2 = "https://fr24api.flightradar24.com/api/flight-summary/full"
                    params2 = {
                    'flight_ids': cached_flight_info["fr24_id"]
                    }
                    headers2 = {
                    'Accept': 'application/json',
                    'Accept-Version': 'v1',
                    'Authorization': f'Bearer {API_TOKEN}'
                    }
                    response = requests.get(url2, headers=headers2, params=params2)
                    response.raise_for_status()
                    data = response.json()
                    cached_flight_info.update({
                        k: v for k, v in data["data"][0].items() if k not in cached_flight_info
                    })
                    #last_flight_fetch = now + 120
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except Exception as err:
                print(f"An error occurred: {err}")

        if cached_flight_info:
            info = cached_flight_info
            display_data["flight_number"]=info["callsign"]

            display_data["callsign"]=info["painted_as"]
            display_data["departure_code"]=info["orig_iata"]
            display_data["departure_city"]=airport_names[display_data["departure_code"]]
            display_data["arrival_code"]=info["dest_iata"]
            display_data["arrival_city"]=airport_names[display_data["arrival_code"]]
            display_data["aircraft"]=info["type"]
            display_data["departure_time"]=info['datetime_takeoff'][11:16]
            display_data["arrival_time"]=info['eta'][11:16]
            display_data["delay"]="N/A"
            display_data["status_color"]="N/A"
            display_data["altitude"]=str(info["alt"]) + " FT"
            display_data["calculated_altitude"] = info["alt"]
            display_data["calculated_distance"] = 0
            display_data["speed"]=str(info["gspeed"]) + " KTS"
            display_data["distance"]=str(int(info["actual_distance"]/1.852)) + " NM"
            display_data["duration"]=time_diff(display_data["departure_time"], display_data["arrival_time"])
            flight_captured = True
            flight_captured_time = time.time()
            flight_captured_info = display_data.copy()

        if debug:
            for k, v in debug_values.items():
                display_data[k] = v
            display_data["departure_city"] = airport_names[display_data["departure_code"]]
            display_data["arrival_city"] = airport_names[display_data["arrival_code"]]
            flight_captured = True
            flight_captured_time = time.time()
            flight_captured_info = display_data.copy()
    return display_data

def rounded_pixmap(pixmap, radius):
    size = pixmap.size()
    rounded = QPixmap(size)
    rounded.fill(Qt.transparent)
    
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size.width(), size.height()), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return rounded

class FlightDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flight Display Absolute")
        self.setStyleSheet("background-color: black; color: white;")
        self.setFixedSize(1920, 440)

        # Find screen with resolution 1920x440
        target_screen = None
        for screen in QGuiApplication.screens():
            geometry = screen.geometry()
            if geometry.width() == 1920 and geometry.height() == 440:
                target_screen = screen
                break

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.setFont(QFont(family, 18))  # adjust size as needed
        else:
            print("Failed to load font, using default.")

        self.widgets = {}
        self.setup_ui()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_ui)

        if target_screen:
            self.setGeometry(target_screen.geometry())
            self.showFullScreen()
        else:
            print("Target screen with resolution 1920x440 not found. Using primary screen.")
            self.showFullScreen()

            
        self.refresh_timer.start(100)
        self.refresh_ui()
    

    def add_label(self, name, x, y, w, h, font_size=20, bold=False, bg_color="#333", font_color="#D5D5D5", font_name="HelveticaNeueMedium", border_radius=25):
        label = QLabel(self)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            family = fallback_font
        font = QFont(family, font_size)
        font.setBold(bold)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        label.move(x, y)
        label.resize(w, h)
        label.setStyleSheet(f"border-radius: {border_radius}px; background-color: {bg_color}; color: {font_color}; padding: 5px;")
        self.widgets[name] = label
        return label

    def setup_ui(self):
        for name, values in ui_positions.items():
            self.add_label(name, *values)
        # Add plane icon image
        icon = QLabel(self)
        icon.setPixmap(QPixmap(plane_icon).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.move(800, 40)
        icon.resize(100, 120)
        self.widgets["plane_icon"] = icon

        # Add landing path
        icon = QLabel(self)
        icon.setPixmap(QPixmap(landing_path))
        icon.move(1360, 220)
        self.widgets["landing_path"] = icon

        # Add landing plane
        icon = QLabel(self)
        icon.setPixmap(QPixmap(plane_image))
        icon.move(1803, 263)
        icon.setAttribute(Qt.WA_TranslucentBackground, True)
        icon.setStyleSheet("background: transparent;")
        self.widgets["landing_plane"] = icon

    def refresh_ui(self):
        global flight_captured, flight_captured_time, flight_captured_info
        global last_flight_fetch, cached_flight_info

        data = get_display_data()
        if data['calculated_altitude'] <-250:
            flight_captured = False
            flight_captured_time = 0
            flight_captured_info = {}
            last_flight_fetch = 0
            cached_flight_info = {}
        elif data['calculated_altitude'] <2000:
            plane_x = int(1470+data['calculated_altitude']*356/2000)-23
            plane_y = min(381,int(390-data['calculated_altitude']*110/2000))-17
            self.widgets['landing_plane'].move(plane_x, plane_y)
        else:
            plane_x = int(1470+2000*356/2000)-23
            plane_y = min(381,int(390-2000*110/2000))-17
            self.widgets['landing_plane'].move(plane_x, plane_y)

        for key, value in data.items():
            if key == "callsign":
                logo_name = logo_map.get(value, default_logo)
                logo_path = f"{logo_folder}{logo_name}"
                raw_pixmap = QPixmap(logo_path).scaled(275, 275, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self.widgets["logo"].setPixmap(rounded_pixmap(raw_pixmap, 40))
            elif key in self.widgets and key != "plane_icon":
                #print(key, value)
                self.widgets[key].setText(value)
                if key == "status":
                    self.widgets[key].setStyleSheet(f"background-color: {data['status_color']}; color: #FFFFFF; border-radius: 25px; padding: 5px;")
                elif key == "ifr_status":
                    self.widgets[key].setStyleSheet(f"background-color: {data['ifr_color']}; color: #FFFFFF; border-radius: 10px; padding: 5px;")
                elif key == "cloud_status":
                    self.widgets[key].setStyleSheet(f"background-color: {data['cloud_color']}; color: #FFFFFF; border-radius: 10px; padding: 5px;")
                elif key == "wind_status":
                    self.widgets[key].setStyleSheet(f"background-color: {data['wind_color']}; color: #FFFFFF; border-radius: 10px; padding: 5px;")
                elif key == "vis_status":
                    self.widgets[key].setStyleSheet(f"background-color: {data['vis_color']}; color: #FFFFFF; border-radius: 10px; padding: 5px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FlightDisplay()
    win.show()
    sys.exit(app.exec_())
