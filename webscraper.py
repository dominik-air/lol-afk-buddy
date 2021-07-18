import os
import requests
from bs4 import BeautifulSoup

webpage = "https://leagueoflegends.fandom.com/wiki/List_of_champions"
result = requests.get(webpage)

if result.status_code == 200:
    soup = BeautifulSoup(result.content, "html.parser")
else:
    raise ValueError("The website didn't respond as expected.")

img_divs = soup.find_all("div", class_="floatleft")
img_links = [div.find("img")["data-src"] for div in img_divs]

current_dir = os.getcwd()
folder_name = r"/champion_images/"
folder_path = current_dir + folder_name
if not os.path.exists(folder_path):
    os.mkdir(folder_path)

for i, img_link in enumerate(img_links):
    img = requests.get(img_link)
    parsed_link = img_link.split("/")
    ending = "_OriginalSquare.png"
    name = f'unknown_champion_{i}'
    for part in parsed_link:
        if part.endswith(ending):
            name = part[:-len(ending)]
            break
    file = open(folder_path+f"{name}.png", "wb")
    file.write(img.content)
    file.close()
