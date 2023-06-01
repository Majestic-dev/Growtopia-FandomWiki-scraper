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
        self.website = None
        self.image = None
        self.description = None
        self.properties = None
        self.rarity = None
        self.itemtype = None
        self.chi = None
        self.hardnessfist = None
        self.hardnesspickaxe = None
        self.firstcolour = None
        self.secondcolour = None
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

        if "thread" not in item.lower() and "vest" not in item.lower():
            itemlastwordcapital = item.split("_")[-1].capitalize()
            itemfirstwordcapital = item.split("_")[0].capitalize()
            itemlast = item.replace(item.split("_")[-1], itemlastwordcapital)
            itemlast = itemlast.replace(item.split("_")[0], itemfirstwordcapital)
            cleanlink = itemlast.replace("_", " ")
        
        if ("thread") in item.lower():
            item = item.replace(" ", "_").lower()
            itemlastwordcapital = item.split("_")[-1].capitalize().split("_")[0].capitalize()
            itemfirstwordcapital = item.split("_")[0].capitalize()
            itemlast = item.replace(item.split("_")[-1], itemlastwordcapital)
            itemlast = itemlast.replace(item.split("_")[0], itemfirstwordcapital)
            itemlast = itemlast.replace("thread", "Thread")
            itemlast = itemlast.replace("_-_", "#")
            cleanlink = itemlast.replace("_", " ")
            cleanlink = cleanlink.replace("#", " - ")

        item = item.replace(" ", "_").lower()
        if ("vest") in item:
            item = item.replace("vest", "Vest")
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
        website = f"https://growtopia.fandom.com/wiki/{itemlast}"
        image = soup.find("span", {"class": "mw-headline"}).find("img").get("src")
        description = soup.find("div", {"class": "card-text"}).text
        properties = soup.find("div", {"class": "card-text"}).find_next("div", {"class": "card-text"}).text
        properties = "\n".join(properties.split("."))
        if properties == "None":
            properties = "This item has no properties!"
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
        firstcolour = soup.find("td", {"class": "seedColor"}).find("div").contents[1].text.replace("#", "").strip()
        secondcolour = soup.find("td", {"class": "seedColor"}).find("div").contents[4].text.replace("#", "").strip()
        firstcolour = await hex_to_rgb(firstcolour)
        secondcolour = await hex_to_rgb(secondcolour)
        growtime = soup.find("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").contents[1].text.strip()
        gemdrop = soup.find("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").contents[1].text.strip()
        try:
            texture = soup.find("a", {"class": "lightbox"}).find("img").get("src")
        except AttributeError:
            texture = "This item has no texture!"

        item_info = ItemInfo()
        item_info.cleanlink = cleanlink
        item_info.website = website
        item_info.image = image
        item_info.description = description
        item_info.properties = properties
        item_info.rarity = rarity
        item_info.itemtype = itemtype
        item_info.chi = chi
        item_info.hardnessfist = hardnessfist
        item_info.hardnesspickaxe = hardnesspickaxe
        item_info.firstcolour = firstcolour
        item_info.secondcolour = secondcolour
        item_info.growtime = growtime
        item_info.gemdrop = gemdrop
        item_info.texture = texture
        return item_info

if __name__ == "__main__":
    while True:
        inp = input("Enter item name: ")

        if inp.lower().startswith("silk thread"):
            print("Due to Fandom's stupidity, you can not search for the Silk Threads")
            continue

        if inp.lower().startswith("quit") or inp.lower().startswith("exit"):
            break

        item_name = inp
        start_time = time.time()
        try:
            rval = asyncio.run(find_item(item_name))
        except AttributeError:
            print("Item not found! Make sure you spelled it correctly!")
            continue
        
        print("Item Name:", rval.cleanlink)
        print("Fandom Website", rval.website)
        print("Item Sprite URL:", rval.image)
        print("Item Description:", rval.description)
        print("Item Properties:", rval.properties)
        print("Item Rarity:", rval.rarity)
        print("Item Type:", rval.itemtype)
        print("Item Chi:", rval.chi)
        print("Hits To Break With Fist:", rval.hardnessfist)
        print("Hits To Break With Pickaxe:", rval.hardnesspickaxe)
        print("Item 1st RGB Colour:", rval.firstcolour)
        print("Item 2nd RGB Colour:", rval.secondcolour)
        print("Item Grow Time:", rval.growtime)
        print("Item Gem Drop:", rval.gemdrop)
        print("Item Texture:", rval.texture)
        print("Process completed in", int(((time.time() - start_time)*1000)), "ms")