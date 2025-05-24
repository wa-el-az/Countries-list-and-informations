import sys
import subprocess
import difflib
import requests
from rich import print

def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Ensure required packages
ensure_package("requests")
ensure_package("rich")

def is_western_sahara(name):
    return name.strip().lower().replace(" ", "") in [
        "westernsahara", "westrensahara", "westren sahara", "western sahara"
    ]

def get_countries():
    try:
        r = requests.get("https://restcountries.com/v3.1/all")
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"[red]Error fetching countries: {e}[/red]")
        sys.exit(1)

def find_country_info(countries, name):
    if is_western_sahara(name):
        return {
            "Name": "Western Sahara (الصحراء المغربية)",
            "Official Stance": "Territory under Moroccan sovereignty",
            "Note": "Morocco considers Western Sahara part of its southern provinces.",
            "Capital": "No capital (part of Morocco)",
            "Region": "Africa",
            "Languages": "Arabic, Amazigh",
            "Currencies": "Moroccan Dirham (MAD)",
            "Flag": "🇲🇦",
            "cca2": "EH",  # ISO code for Western Sahara
        }

    for c in countries:
        if c['name']['common'].lower() == name.lower():
            return {
                "Name": c['name']['common'],
                "Official Name": c['name'].get('official', 'N/A'),
                "Capital": ', '.join(c.get('capital', ['N/A'])),
                "Region": c.get('region', 'N/A'),
                "Subregion": c.get('subregion', 'N/A'),
                "Population": c.get('population', 'N/A'),
                "Area (km²)": c.get('area', 'N/A'),
                "Languages": ', '.join(c.get('languages', {}).values()) if 'languages' in c else 'N/A',
                "Currencies": ', '.join([v['name'] for v in c.get('currencies', {}).values()]) if 'currencies' in c else 'N/A',
                "Timezones": ', '.join(c.get('timezones', [])),
                "Flag": c.get('flag', 'N/A'),
                "cca2": c.get('cca2', None),  # ISO 2-letter country code
            }
    return None

def suggest_country(name, country_names):
    suggestions = difflib.get_close_matches(name, country_names, n=1, cutoff=0.6)
    return suggestions[0] if suggestions else None

def get_city_info(country_code, city_name):
    url = "http://geodb-free-service.wirefreethought.com/v1/geo/cities"
    params = {
        "countryIds": country_code,
        "namePrefix": city_name,
        "limit": 5,
        "sort": "-population"
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        cities = data.get('data', [])
        if not cities:
            return None
        city = cities[0]
        return {
            "Name": city.get('name'),
            "Region": city.get('region'),
            "Country": city.get('country'),
            "Population": city.get('population'),
            "Latitude": city.get('latitude'),
            "Longitude": city.get('longitude'),
        }
    except requests.RequestException:
        return None

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "timezone": "auto"
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        weather = data.get("current_weather")
        if not weather:
            return None
        return {
            "Temperature (°C)": weather.get("temperature"),
            "Wind Speed (km/h)": weather.get("windspeed"),
            "Wind Direction (°)": weather.get("winddirection"),
            "Weather Code": weather.get("weathercode"),
            "Time": weather.get("time"),
        }
    except requests.RequestException:
        return None

def print_country_info(info):
    print("\n[bold green]Country Information:[/bold green]")
    for k, v in info.items():
        if k != "cca2":
            print(f"[bold]{k}[/bold]: {v}")

def print_city_info(city_info):
    print("\n[bold blue]City Information:[/bold blue]")
    for k, v in city_info.items():
        print(f"[bold]{k}[/bold]: {v}")

def print_weather_info(weather):
    if weather is None:
        print("[blue]Weather data not available.[/blue]")
        return
    print("\n[bold magenta]Current Weather:[/bold magenta]")
    for k, v in weather.items():
        print(f"[bold]{k}[/bold]: {v}")

def main():
    print("[bold magenta]Welcome to Country & City Info with Weather![/bold magenta]")
    countries = None
    country_names = []
    last_country_info = None

    while True:
        user_input = input("\nEnter a country name, city name, or command (fetch, list, quit, credits): ").strip()

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd == "quit":
            print("[bold green]Goodbye![/bold green]")
            break

        if cmd == "credits":
            print(r"""
░██╗░░░░░░░██╗░█████╗░███████╗██╗░░░░░
░██║░░██╗░░██║██╔══██╗██╔════╝██║░░░░░
░╚██╗████╗██╔╝███████║█████╗░░██║░░░░░
░░████╔═████║░██╔══██║██╔══╝░░██║░░░░░
░░╚██╔╝░╚██╔╝░██║░░██║███████╗███████╗
░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚══════╝╚══════╝
[bold red]Created by Wael Amrani Zerrifi[/bold red]  
[bold red]GitHub: Wa-el-az[/bold red]
[bold red]Version: 1.3[/bold red]
[bold red]YouTube: @The.Morocco[/bold red]
[bold red]Telegram: @WaelAZultra[/bold red]
[bold green]Latest update: 05/24/2025[/bold green]
""")
            continue

        if cmd in ["fetch", "list", "countries", "fetch countries", "fetch countires"]:
            if countries is None:
                print("[blue]Fetching countries list...[/blue]")
                countries = get_countries()
                country_names = sorted([c['name']['common'] for c in countries])
            print("[bold cyan]Countries list:[/bold cyan]")
            for c_name in country_names:
                print(f"- {c_name}")
            continue

        if countries is None:
            print("[yellow]Please fetch countries list first by typing 'fetch' or 'list'.[/yellow]")
            continue

        # Special messages for Morocco and Palestine
        if cmd == "morocco":
            print("[bold red]The country of Wael![/bold red]")
        elif cmd == "palestine":
            print("[bold green]Free Palestine[/bold green]")

        country_info = find_country_info(countries, user_input)

        if country_info:
            print_country_info(country_info)
            last_country_info = country_info
            continue

        if last_country_info:
            country_code = last_country_info.get("cca2")
            if not country_code:
                print("[red]Country code not found. Cannot query cities.[/red]")
                continue
            city_info = get_city_info(country_code, user_input)
            if city_info:
                print_city_info(city_info)
                weather = get_weather(city_info["Latitude"], city_info["Longitude"])
                print_weather_info(weather)
                continue
            else:
                print(f"[yellow]City '{user_input}' not found in {last_country_info['Name']}.[/yellow]")
                continue

        suggestion = suggest_country(user_input, country_names)
        if suggestion:
            confirm = input(f"[yellow]Country not found. Did you mean '{suggestion}'? (yes/no): [/yellow]").strip().lower()
            if confirm == "yes":
                country_info = find_country_info(countries, suggestion)
                print_country_info(country_info)
                last_country_info = country_info
                continue
            else:
                print("[red]Please enter a valid country name first.[/red]")
                continue
        else:
            print("[red]Country not found and no close match available. Please enter a valid country name first.[/red]")

if __name__ == "__main__":
    main()
