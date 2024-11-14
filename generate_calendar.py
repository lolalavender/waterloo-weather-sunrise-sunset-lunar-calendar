import requests
from datetime import datetime, timedelta
from skyfield.api import load, Topos
from icalendar import Calendar, Event
import pytz

# Constants
LAT, LON = 51.504180457500155, -0.11990022828216651  # Coordinates for Waterloo, London
API_KEY = "14e5747433d8931cd8e9baae8c22428a"
BASE_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,hourly,alerts&appid={API_KEY}&units=metric"
TIMEZONE = pytz.timezone("Europe/London")

# Helper functions
def fetch_weather_data():
    response = requests.get(BASE_URL)
    response.raise_for_status()
    return response.json()

def get_moon_phase(moon_phase_value):
    """Convert moon phase numeric value to an emoji."""
    phases = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    phase_index = int(moon_phase_value * 8)
    return phases[phase_index % 8]

def format_time(timestamp):
    """Format a Unix timestamp as a human-readable time in London."""
    return datetime.fromtimestamp(timestamp, TIMEZONE).strftime("%H:%M")

def create_event(calendar, start_dt, summary, description=""):
    """Create and add an event to an iCalendar calendar."""
    event = Event()
    event.add("summary", summary)
    event.add("dtstart", start_dt)
    event.add("dtend", start_dt + timedelta(minutes=30))
    event.add("description", description)
    calendar.add_component(event)

def create_icalendar(weather_data):
    calendar = Calendar()
    calendar.add("prodid", "-//My Weather Calendar//example.com//")
    calendar.add("version", "2.0")
    
    # Weather for the day
    current_weather = weather_data["current"]
    sunrise_time = format_time(current_weather["sunrise"])
    sunset_time = format_time(current_weather["sunset"])
    description = (
        f"☀️↑{sunrise_time} Sunrise\n"
        f"☀️↓{sunset_time} Sunset\n"
        f"🌡️ Temp: {current_weather['temp']}°C\n"
        f"💧 Humidity: {current_weather['humidity']}%\n"
        f"💨 Wind Speed: {current_weather['wind_speed']} m/s"
    )
    
    # Add weather event
    start_dt = datetime.now(TIMEZONE)
    create_event(calendar, start_dt, f"🌤️ {current_weather['weather'][0]['description'].title()}", description)
    
    # Add sunrise/sunset events
    create_event(calendar, datetime.fromtimestamp(current_weather["sunrise"], TIMEZONE), "☀️ Sunrise")
    create_event(calendar, datetime.fromtimestamp(current_weather["sunset"], TIMEZONE), "☀️ Sunset")

    # Add moon phase event
    moon_phase = weather_data["daily"][0]["moon_phase"]
    moon_phase_emoji = get_moon_phase(moon_phase)
    moon_event_summary = f"{moon_phase_emoji} Moon Phase"
    create_event(calendar, start_dt, moon_event_summary)
    
    return calendar

# Main script to generate calendar and save it
def generate_calendar():
    weather_data = fetch_weather_data()
    calendar = create_icalendar(weather_data)
    
  # Save to .ics file in the root
with open("weather_calendar.ics", "wb") as f:
    f.write(calendar.to_ical())


# Call function to generate calendar file
# Uncomment this if running locally to test
# generate_calendar()
