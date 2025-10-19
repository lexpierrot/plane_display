# Flight Display Absolute ✈️🖥️

This project is a PyQt5-based dashboard for displaying live flight and weather data for San Diego International Airport (KSAN). It is designed for a 1920x440 pixel display and shows inbound flight details, weather conditions, and approach status in real time.

## Features 🚀
- **Live Flight Data:** Fetches inbound flights to KSAN using the Flightradar24 API.
- **Live Weather Data:** Retrieves current METAR weather for KSAN.
- **Custom UI:** Modern, full-screen dashboard with airline logos, aircraft info, and approach visualization.
- **Configurable:** All settings are managed in `config.yml` for easy customization.

## Setup Instructions 🛠️

### 1. Clone or Download the Repository 📁
Place all files in a single folder. The structure should look like:
```
plane_display_min/
├── flight_display.py
├── metar.py
├── requirements.txt
├── api_key.txt
├── config.yml
├── airline_logos.yml
├── assets/
│   ├── airports.csv
│   ├── plane_icon.png
│   ├── landing_path_resized.png
│   └── plane.png
├── fonts/
│   └── HelveticaNeueMedium.otf
├── logos/
│   └── [airline logo images]
```

### 2. Install Python & Dependencies 🐍
Create a virtual environment and install dependencies:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add Your API Key 🔑
- Obtain a Flightradar24 API key.
- Create a file named `api_key.txt` in the project root and paste your API key inside (no quotes, one line).

### 4. Configure `config.yml` ⚙️
All main settings are in `config.yml`. Here is a breakdown of each option:

#### Main Flight & Weather Settings 🌦️
- `FPM_LANDING`: Descent rate in feet per minute (default: 800).
- `TDZE`: Touchdown zone elevation in feet (default: 17).
- `AIRPORT_CODE`: IATA code for the airport to monitor (default: KSAN).
- `ALT_MONITOR`: Altitude threshold for monitoring inbound flights (default: 3000).
- `METAR_CODE`: Airport code for METAR weather fetch (default: KSAN).
- `DEFAULT_ARRIVAL_CITY`: Default city name for arrivals (default: 'San Diego, CA').

#### API & Data Source Settings 🌐
- `bounds`: Geographic bounds for flight search (lat/lon, comma-separated).
- `api_url`: Main Flightradar24 API endpoint for live flight positions.
- `flight_summary_url`: API endpoint for detailed flight summary.
- `accept_version`: API version header (default: 'v1').

#### File Paths 📂
- `font_path`: Path to the main UI font file.
- `fallback_font`: Fallback font if the main font fails to load.
- `logo_map_path`: Path to the airline logo mapping YAML file.
- `logo_folder`: Folder containing airline logo images.
- `default_logo`: Filename for the default logo image.
- `airport_csv`: Path to the CSV file mapping airport codes to cities.
- `plane_icon`: Path to the plane icon image.
- `landing_path`: Path to the landing path image.
- `plane_image`: Path to the plane image for approach visualization.

#### UI Layout & Appearance 🎨
- `ui_positions`: Dictionary of all UI element positions and styles. Each entry is a list:
  `[x, y, width, height, font_size, bold, bg_color, font_color, font_name, border_radius]`
  - Example: `logo: [50, 40, 275, 275, 0, False, 'black', '#FFFFFF', 'HelveticaNeueMedium', 25]`
  - You can adjust coordinates, sizes, colors, and fonts for each label or panel.

#### Debug Mode Sample Values 🧪
- `debug_values`: Predefined values for debug mode. Useful for testing UI without live data.
  - Example:
    ```yaml
    debug_values:
      flight_number: 'DAL1234'
      callsign: 'DAL'
      departure_code: 'ATL'
      arrival_code: 'SAN'
      aircraft: 'A350'
      departure_time: '10:00'
      arrival_time: '12:00'
      altitude: '2500 FT'
      calculated_altitude: 2200
      speed: '124 KTS'
      distance: '1250 NM'
    ```

### 5. Run the Application ▶️
```powershell
python flight_display.py
```

## File Overview 📄
- `flight_display.py`: Main application. Handles UI, API calls, and data processing.
- `metar.py`: Contains functions for fetching and parsing METAR weather data.
- `requirements.txt`: List of required Python packages.
- `api_key.txt`: Your Flightradar24 API key (keep this private!).
- `config.yml`: All main configuration settings for the app.
- `airline_logos.yml`: Maps airline codes to logo image filenames.
- `assets/airports.csv`: List of airport codes and cities.
- `fonts/`: Contains custom font for UI.
- `logos/`: Airline logo images.

## Customization 🛠️
- Change any value in `config.yml` to adjust airport, altitude, UI layout, colors, fonts, or debug mode.
- Add new airline logos to the `logos/` folder and update `airline_logos.yml`.
- UI layout and colors can be adjusted in the `ui_positions` section of `config.yml`.

## Troubleshooting 🧰
- If fonts or images do not display, check file paths and ensure all assets are present.
- If you see API errors, verify your API key in `api_key.txt`.
- For Windows PowerShell, you may need to set the execution policy to allow script activation:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## License & Credits 📜
- This project is for educational and personal use only. See LICENSE.txt for details.
- Airline logos and data are property of their respective owners.

## Contact ✉️
For questions or improvements, contact the project author.
