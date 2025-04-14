import requests
from bs4 import BeautifulSoup
import os
import re

# Base URL for the VfB website
base_url = "https://www.vfb.de"

# Get the main page
response = requests.get("https://www.vfb.de/de/1893/aktuell/neues/")
soup = BeautifulSoup(response.text, "lxml")

# Create a directory to store player profiles if it doesn't exist
if not os.path.exists("player_profiles"):
    os.makedirs("player_profiles")

# Find all links that match the player profile pattern
for link in soup.find_all("a"):
    href = link.get("href")
    if href and href.startswith("/de/vfb/profis/kader"):
        # Extract player name from the URL
        match = re.search(r'/kader/\d+/([^/]+)/spielerprofil/', href)
        if match:
            player_name = match.group(1)
            player_url = base_url + href
            
            # Get the player's profile page
            try:
                player_response = requests.get(player_url)
                player_soup = BeautifulSoup(player_response.text, "lxml")
                
                # Save the content to a file
                file_path = os.path.join("player_profiles", f"{player_name}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(player_soup.get_text())
                print(f"Saved profile for {player_name}")
            except Exception as e:
                print(f"Error processing {player_name}: {str(e)}")

