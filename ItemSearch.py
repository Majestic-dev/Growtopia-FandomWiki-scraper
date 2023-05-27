import aiohttp
import random
import asyncio
import time
from bs4 import BeautifulSoup
from async_lru import alru_cache

class ItemInfo():
    def __init__(self):
        self.itemlast = None
        self.cleanlink = None
        self.image = None
        self.description = None
        self.properties = None
        self.rarity = None
        self.itemtype = None
        self.chi = None
        self.hardnessfist = None
        self.hardnesspickaxe = None
        self.colour = None
        self.growtime = None
        self.gemdrop = None
        self.texture = None

async def hex_to_rgb(hex: str):
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex[i:i+2], 16)
            rgb.append(decimal)
        return tuple(rgb)

@alru_cache(maxsize=128)
async def find_item(item: str):
        item = item.replace(" ", "_")
        itemlastwordcapital = item.split("_")[-1].capitalize()
        itemfirstwordcapital = item.split("_")[0].capitalize()
        itemlast = item.replace(item.split("_")[-1], itemlastwordcapital)
        itemlast = itemlast.replace(item.split("_")[0], itemfirstwordcapital)
        cleanlink = itemlast.replace("_", " ")
        
        session = aiohttp.ClientSession()
        response = await session.get(
            f"https://growtopia.fandom.com/wiki/{itemlast}"
        )
        data = await response.read()
        await session.close()
        soup = BeautifulSoup(data, "html.parser")
        image = soup.find("span", {"class": "mw-headline"}).find("img").get("src")
        description = soup.find("div", {"class": "card-text"}).text
        properties = soup.find("div", {"class": "card-text"}).find_next("div", {"class": "card-text"}).text
        properties = "\n".join(properties.split("."))
        try:
            rarity = soup.find("span", {"class": "mw-headline"}).find("small").text.replace("(", "").replace(")", "").replace("Rarity: ", "")
        except AttributeError:
            rarity = "None"
        itemtype = soup.find("td").contents[1].text.strip()
        if len((list_of_contents:=soup.find("td").find_next("td").contents)) >= 2:
            list_of_contents = 1
        else:
            list_of_contents = 0
        chi = soup.find("td").find_next("td").contents[list_of_contents].text.strip()
        hardnessfist = soup.find("td").find_next("td").find_next("td").find_next("td").find_next("td").contents[1].text.strip()
        hardnesspickaxe = soup.find("td").find_next("td").find_next("td").find_next("td").find_next("td").contents[4].text.strip()
        colour = soup.find("td", {"class": "seedColor"}).find("div").contents[random.choice([1, 4])].text.replace("#", "").strip()
        colour = await hex_to_rgb(colour)
        growtime = soup.find("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").contents[1].text.strip()
        gemdrop = soup.find("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").contents[1].text.strip()
        try:
            texture = soup.find("a", {"class": "lightbox"}).find("img").get("src")
        except AttributeError:
            return

        item_info = ItemInfo()
        item_info.cleanlink = cleanlink
        item_info.image = image
        item_info.description = description
        item_info.properties = properties
        item_info.rarity = rarity
        item_info.itemtype = itemtype
        item_info.chi = chi
        item_info.hardnessfist = hardnessfist
        item_info.hardnesspickaxe = hardnesspickaxe
        item_info.colour = colour
        item_info.growtime = growtime
        item_info.gemdrop = gemdrop
        item_info.texture = texture
        return item_info

if __name__ == "__main__":
    while True:
        inp = input("Enter item name: ")

        if inp.lower().startswith("quit") or inp.lower().startswith("exit"):
            break

        item_name = inp
        try:
            start_time = time.time()
            rval = asyncio.run(find_item(item_name))
            print("Item Name:", rval.cleanlink)
            print("Item Sprite URL:", rval.image)
            print("Item Description:", rval.description)
            if rval.properties != "None":
                print("Item Properties:", rval.properties)
            else:
                print("Item Properties: This item has no properties!")
            print("Item Rarity:", rval.rarity)
            print("Item Type:", rval.itemtype)
            print("Item Chi:", rval.chi)
            print("Hits To Break With Fist:", rval.hardnessfist)
            print("Hits To Break With Pickaxe:", rval.hardnesspickaxe)
            print("Item Colour (RGB):", rval.colour)
            print("Item Grow Time:", rval.growtime)
            print("Item Gem Drop:", rval.gemdrop)
            print("Item Texture:", rval.texture)
            print("Process completed in", time.time() - start_time, "seconds")
        except AttributeError:
             print("Item not found! Make sure you spelled it correctly!")
  