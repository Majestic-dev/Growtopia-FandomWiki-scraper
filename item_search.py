import asyncio
import os
import time

import aiohttp
import growtopia
from async_lru import alru_cache
from bs4 import BeautifulSoup


class ItemInfo:
    def __init__(self) -> None:
        self.description = ""
        self.chi = ""
        self.splicing_seed1 = ""
        self.splicing_seed2 = ""
        self.equip_playmod_text = ""
        self.unequip_playmod_text = ""
        self.playmod_name = ""


async def create_item_names():
    items_data = growtopia.ItemsData("")  # Specify the path to your items.dat file here
    await items_data.parse()
    with open("item_names.txt", "w") as f:
        f.write("\n".join([item.name for item in items_data.items]))


def find_formatted_name(item: str, file_content: str):
    for line in file_content.split("\n"):
        if line.lower().startswith(item):
            return line

@alru_cache
async def find_item(item: str):
    session = aiohttp.ClientSession()
    response = await session.get(
        f"https://growtopia.fandom.com/wiki/{item}", max_redirects=100
    )
    data = await response.read()
    await session.close()
    soup = BeautifulSoup(data, "html.parser")

    try:
        description = soup.find("div", {"class": "card-text"}).text

        if "|" in description:
            description = description.replace("|", " ")
    except AttributeError:
        description = "This item has no description!"

    try:
        splicing_seeds = (
        soup.find(attrs={"class": "recipebox", "style": "background: #66cc66; color: #006600;"})
        )

        splicing_seed1 = splicing_seeds.find("tr").find_next("tr").find_next("tr").find("a").text
        splicing_seed2 = splicing_seeds.find("tr").find_next("tr").find_next("tr").find("a").find_next("a").text

        if "seed" not in splicing_seed1.lower():
            splicing_seed1 = "Blank"
        if "seed" not in splicing_seed2.lower():
            splicing_seed2 = "Blank"

    except AttributeError:
        splicing_seed1 = "Blank"
        splicing_seed2 = "Blank"

    try:
        equip_playmod_text = soup.find(
            "td", {"style": "color:#199e24; padding:0px 20px; font-style: italic"}
        ).text

    except AttributeError:
        equip_playmod_text = ""

    try:
        unequip_playmod_text = soup.find(
            "td", {"style": "color:#9e2a18; padding:0px 20px; font-style: italic"}
        ).text
        
    except AttributeError:
        unequip_playmod_text = ""

    try:
        if equip_playmod_text != "" and unequip_playmod_text != "":
            playmod_name = (
                soup.find("div", {"class": "mw-parser-output"})
                .find("p")
                .find_next("p")
                .find("i")
                .text
            )
        else:
            playmod_name = ""
    except AttributeError:
        playmod_name = ""

    try:
        if len((list_of_contents := soup.find("td").find_next("td").contents)) >= 2:
            list_of_contents = 1
        else:
            list_of_contents = 0
        chi = soup.find("td").find_next("td").contents[list_of_contents].text.strip()
    except AttributeError:
        chi = "None"

    item_info = ItemInfo()
    item_info.description = description
    item_info.chi = chi
    item_info.splicing_seed1 = splicing_seed1
    item_info.splicing_seed2 = splicing_seed2
    item_info.equip_playmod_text = equip_playmod_text
    item_info.unequip_playmod_text = unequip_playmod_text
    item_info.playmod_name = playmod_name
    return item_info


if __name__ == "__main__":
    while True:
        try:
            if "item_names.txt" not in os.listdir():
                asyncio.run(create_item_names())

            with open("item_names.txt", "r") as f:
                file_content = f.read()

            inp = input("Enter item name: ")
            start_time = time.time()
            correct_name = find_formatted_name(inp, file_content)
            if correct_name:
                item_info = asyncio.run(find_item(correct_name))
                print(f"Description: {item_info.description}")
                print(f"Chi: {item_info.chi}")
                if (
                    item_info.splicing_seed1 == "Blank"
                    and item_info.splicing_seed2 == "Blank"
                ):
                    print(f"This item can't be spliced")
                else:
                    print(f"Splicing seed 1: {item_info.splicing_seed1}")
                    print(f"Splicing seed 2: {item_info.splicing_seed2}")
                if item_info.equip_playmod_text == "":
                    print(f"This item has no playmod text upon equipping")
                else:
                    print(f"Equip playmod text: {item_info.equip_playmod_text.strip()}")
                if item_info.unequip_playmod_text == "":
                    print(f"This item has no playmod text upon unequipping")
                else:
                    print(f"Unequip playmod text: {item_info.unequip_playmod_text.strip()}")
                if item_info.playmod_name == "":
                    print(f"This item has no playmod")
                else:
                    print(f"Playmod name: {item_info.playmod_name}")
                print(
                    f"Process completed in",
                    int((time.time() - start_time) * 1000),
                    "milliseconds",
                )
        except KeyboardInterrupt:
            break
