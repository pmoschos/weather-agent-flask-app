# 🌤️ Weather Application (Python + Flask)

![Total Views](https://views.whatilearened.today/views/github/pmoschos/weather_app.svg)   ![GitHub last commit](https://img.shields.io/github/last-commit/pmoschos/weather_app)   ![License](https://img.shields.io/badge/license-MIT-green.svg)   ![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)   ![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey.svg)   ![Playwright](https://img.shields.io/badge/Playwright-Chromium-green.svg)  

---

## 🌦️ Overview

This project is an **AI-powered Weather Web Application** built with **Python** and **Flask**.  
It uses an **LLM agent (`browser_use`)** to browse weather websites (like `weather.com` or `openweathermap.org`) and fetch live weather data.  

As a fallback, the app integrates with **Open-Meteo’s free API** (no key required), ensuring you always get results even if the AI agent cannot browse.  

The app features:

- A **modern, responsive UI** with HTML, CSS, and JavaScript.  
- **Search functionality** by city and country.  
- **Recent searches** stored in memory for quick access.  
- **Agent-based web automation** for scraping weather data.  
- **API fallback** to guarantee data availability.  

---

## ✨ Key Features

✅ **AI Weather Agent** – powered by `browser_use` and LLMs (OpenAI, Anthropic, etc.)  
✅ **Fallback API** – Open-Meteo integration for guaranteed results  
✅ **Responsive UI** – Mobile-friendly with clean CSS grid system  
✅ **Recent Searches** – Caches your last 10 searches  
✅ **Error Handling** – Graceful fallbacks for missing/invalid inputs  
✅ **Logging** – Rich structured logging with file + console outputs  
✅ **Environment Configuration** – `.env` file for API keys, host/port, and secrets  

---

## 📸 Screenshots

### 1. **Search Form**
![Search Example](https://github.com/user-attachments/assets/0bce7a20-bc2c-45e7-9a3d-99d85e9cf040)

### 2. **Weather Results**
![Weather Results](https://github.com/user-attachments/assets/e3457ce8-70b2-46ae-871e-9ce95ce7fd0d)

---

## 🏗️ Project Structure

```
weather_app/
├─ app/
│  ├─ __init__.py          # Flask app factory
│  ├─ config.py            # Logging & configuration
│  ├─ models.py            # WeatherData dataclass
│  ├─ utils/
│  │  └─ async_runner.py   # Background event loop
│  ├─ agents/
│  │  └─ weather_agent.py  # AI Agent + API fallback
│  ├─ routes/
│  │  └─ views.py          # Flask endpoints
│  ├─ templates/
│  │  └─ index.html        # UI template
│  └─ static/
│     ├─ css/style.css     # Styles
│     └─ js/script.js      # Frontend logic
├─ run.py                  # Entry point
├─ requirements.txt        # Dependencies
├─ .env.example            # Env variables
└─ README.md               # Project docs
```

---

## 📚 Libraries Used

### 🔹 Backend
- **Flask** – Lightweight web framework  
- **browser_use** – AI agent with Playwright integration  
- **httpx** – Async HTTP client for API calls  
- **python-dotenv** – Environment variables  

### 🔹 Frontend
- **Vanilla JS** – Fetch API for AJAX calls  
- **Responsive CSS** – Clean modern UI  

---

## 🔧 Technical Requirements

- **Python**: 3.11+  
- **Flask**: 3.x  
- **Playwright**: Installed with Chromium runtime  
- **API Keys**:  
  - `OPENAI_API_KEY` (required for AI agent)  
  - (Optional) `USE_AGENT=false` to force Open-Meteo fallback  

---

## 🚀 Setup & Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/pmoschos/weather_app
   cd weather_app
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate     # Linux/macOS
   venv\Scripts\activate        # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OPENAI_API_KEY and settings
   ```

5. **Run the Application**
   ```bash
   python run.py
   ```
   Then open: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🖥️ User Interface

### 🌍 Search Form
- Enter a **city** and **country**  
- Press **Get Weather** to fetch results  

### 🌡️ Weather Results
- Temperature (°C or °F)  
- Wind speed (km/h, m/s, mph)  
- Humidity (%)  

### 🕒 Recent Searches
- Displays your last 5 weather lookups  

---

## 💻 Example Code Snippets

### Fetching Weather Data via Flask Route
```python
@bp.route('/weather', methods=['POST'])
def get_weather():
    data = request.get_json(force=True) or {}
    town, country = data.get("town"), data.get("country")

    async_runner = current_app.extensions['async_runner']
    weather_agent = current_app.extensions['weather_agent']

    # Try AI agent first, fallback to Open-Meteo
    weather_data = async_runner.run(
        weather_agent.get_weather_data(town, country),
        timeout=120
    ) or async_runner.run(
        get_weather_open_meteo(town, country),
        timeout=60
    )

    return jsonify({'success': True, 'data': asdict(weather_data)})
```

### Frontend Fetch Request
```javascript
const response = await fetch('/weather', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ town, country })
});
const data = await response.json();
```

---

## 📈 Future Enhancements

- **7-Day Forecast** – Extended data view  
- **Geolocation Support** – Auto-detect user’s location  
- **Database Integration** – Persist search history  
- **Dark Mode** – Theming toggle for UI  
- **Docker Deployment** – Containerized app for easy hosting  

---

## 📄 License

🔐 Licensed under the [MIT License](https://mit-license.org/).  
Feel free to fork, modify, and share this project!

---

## 📢 Stay Updated

Be sure to ⭐ this repository to stay updated with new examples and enhancements!

## 📄 License
🔐 This project is protected under the [MIT License](https://mit-license.org/).


## Contact 📧
Panagiotis Moschos - pan.moschos86@gmail.com

🔗 *Note: This is a Python script and requires a Python interpreter to run.*

---
<h1 align=center>Happy Coding 👨‍💻 </h1>

<p align="center">
  Made with ❤️ by 
  <a href="https://www.linkedin.com/in/panagiotis-moschos" target="_blank">
  Panagiotis Moschos</a>
</p> 
