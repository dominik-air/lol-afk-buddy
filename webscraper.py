#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This script ought to be run at least once before the use of the main application."""
import os
import json
import requests
from bs4 import BeautifulSoup

webpage = "https://leagueoflegends.fandom.com/wiki/List_of_champions"  # source website
result = requests.get(webpage)

if result.status_code == 200:
    soup = BeautifulSoup(result.content, "html.parser")
else:
    raise ValueError("The website didn't respond as expected.")

img_divs = soup.find_all("div", class_="floatleft")
img_links = [div.find("img")["data-src"] for div in img_divs]

# gets the current directory and creates a new folder for the images
current_dir = os.getcwd()
folder_name = r"/champion_images/"
folder_path = current_dir + folder_name
if not os.path.exists(folder_path):
    os.mkdir(folder_path)

champion_names = []
for i, img_link in enumerate(img_links):
    img = requests.get(img_link)
    parsed_link = img_link.split("/")
    ending = "_OriginalSquare.png"
    name = f'unknown_champion_{i}'
    for part in parsed_link:
        if part.endswith(ending):
            name = part[:-len(ending)]
            champion_names.append(name.lower())
            break
    with open(folder_path+f"{name}.png", "wb") as image_file:
        image_file.write(img.content)

# saves the champion names (in lowercase) in a JSON file for future usage
with open("data/champions.json", "w+") as save_file:
    json.dump(champion_names, save_file, indent=4)

