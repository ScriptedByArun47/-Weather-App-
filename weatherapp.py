from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.metrics import dp
import requests
import logging

API_KEY = "9004b2a6daa4818401f901ee65eae86a"  # Replace with your API key

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Register the Emoji font
LabelBase.register(name="Emoji", fn_regular="C:/Windows/Fonts/seguiemj.ttf")  # Ensure it's properly registered
logging.info(f"Available fonts: {LabelBase._fonts}")  # Debugging font list

KV = """
Screen:
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                source: "D:/projectA/lackground.jpg"  # Replace with your background image path
                size: self.size
                pos: self.pos

        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(20)
            
            MDTextField:
                id: city_input
                hint_text: "Enter city name"
                size_hint_x: 0.5
                pos_hint: {"center_x": 0.5}

            MDRaisedButton:
                text: "Get Weather"
                size_hint_x: 0.5
                pos_hint: {"center_x": 0.5}
                on_release: app.fetch_weather()

        # Glassmorphism Effect for Current Weather
        MDBoxLayout:
            orientation: "vertical"
            size_hint: 0.5, None
            height: dp(250)
            pos_hint: {"center_x": 0.5}
            padding: dp(15)
            radius: [25]
            md_bg_color: 1, 1, 1, 0.32
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.3
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [25]

            MDLabel:
                id: location_label
                text: "Location: -"
                theme_text_color: "Primary"
                halign: "center"
                font_style: "H6"

            MDLabel:
                id: temp_label
                text: "Temperature: -"
                theme_text_color: "Primary"
                halign: "center"
                font_style: "H5"

            MDLabel:
                id: desc_label
                text: "Weather: -"
                theme_text_color: "Primary"
                halign: "center"
                font_style: "H6"

        # Spacer
        Widget:
            size_hint_y: None
            height: dp(20)

        # Glassmorphism Effect for Forecast
        MDBoxLayout:
            id: forecast_box
            orientation: "vertical"
            size_hint_x: 0.5
            pos_hint: {"center_x": 0.5}
            height: 0
            opacity: 0
            padding: dp(15)
            radius: [25]
            md_bg_color: 1, 1, 1, 0.32
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.5
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [25]
"""

class WeatherApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def fetch_weather(self):
        city = self.root.ids.city_input.text.strip()
        if not city:
            return

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        url_forecast = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

        try:
            response = requests.get(url)
            response_forecast = requests.get(url_forecast)

            if response.status_code == 200 and response_forecast.status_code == 200:
                data = response.json()
                data_forecast = response_forecast.json()

                location = f"{data['name']}, {data['sys']['country']}"
                temp = f"{data['main']['temp']}°C"
                desc = data['weather'][0]['description'].capitalize()

                weather_emojis = {
                    "Clear sky": "☀️",
                    "Few clouds": "🌤️",
                    "Scattered clouds": "🌥️",
                    "Broken clouds": "☁️",
                    "Overcast clouds": "☁️",
                    "Shower rain": "🌧️",
                    "Rain": "🌧️",
                    "Thunderstorm": "⛈️",
                    "Snow": "❄️",
                    "Mist": "🌫️",
                    "Haze": "🌫️",
                    "Fog": "🌫️"
                }

                emoji = weather_emojis.get(desc, "☁️")

                self.root.ids.location_label.text = f"📍 Location: {location}"
                self.root.ids.temp_label.text = f"🌡️ Temperature: {temp}"
                self.root.ids.desc_label.text = f"{emoji} Weather: {desc}"

                # Ensure labels use the correct font for emojis
                self.root.ids.location_label.font_name = "Emoji"
                self.root.ids.temp_label.font_name = "Emoji"
                self.root.ids.desc_label.font_name = "Emoji"

                # Clear old forecast data
                self.root.ids.forecast_box.clear_widgets()

                forecast_box = self.root.ids.forecast_box
                forecast_box.height = 0
                forecast_box.opacity = 0

                for i in range(0, 40, 8):
                    day = data_forecast["list"][i]
                    date = day["dt_txt"].split()[0]
                    temp = f"{day['main']['temp']}°C"
                    desc = day["weather"][0]["description"].capitalize()

                    emoji_forecast = weather_emojis.get(desc, "☁️")  # Fixed default emoji

                    forecast_label = MDLabel(
                        text=f"{emoji_forecast} {date}: {temp}, {desc}",
                        theme_text_color="Primary",
                        halign="center"
                    )
                    forecast_label.font_name = "Emoji"  # Explicitly set font

                    forecast_box.add_widget(forecast_label)

                # Animate the forecast box
                animation = Animation(height=dp(250), opacity=1, t='in_out_quad', duration=1)
                animation.start(forecast_box)

            else:
                self.root.ids.location_label.text = "City not found"
                logging.error(f"Failed to fetch weather data for {city}. Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            self.root.ids.location_label.text = "Network error"
            logging.error(f"Error fetching weather data: {e}")

        except Exception as e:
            self.root.ids.location_label.text = "An error occurred"
            logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    WeatherApp().run()
