from bs4 import BeautifulSoup
import aiohttp
import time
import asyncio
import glob
import os
import growtopia

class ItemInfo:
    def __init__(self, attrs: dict[str]) -> None:
        self.description = attrs["description"].strip()
        self.type = attrs["item_type"].strip()
        self.chi = attrs["chi"].strip()
        self.texture_type = attrs["texture_type"].strip()
        self.collision_type = attrs["collision_type"].strip()
        self.hardness = attrs["hardness"].strip()
        self.seed_colours = attrs["seed_colours"].strip()
        self.grow_time = attrs["grow_time"].strip()
        self.default_gem_drop = attrs["default_gem_drop"].strip()
        self.splicing_seed1 = attrs["splicing_seed1"].strip()
        self.splicing_seed2 = attrs["splicing_seed2"].strip()
        self.equip_playmod_text = attrs["equip_playmod_text"].strip()
        self.unequip_playmod_text = attrs["unequip_playmod_text"].strip()
        self.playmod_name = attrs["playmod_name"].strip()
        self.crafting_recipe = attrs["crafting_recipe"]
        self.yield_value = attrs["yield_value"]

class Parse_ItemInfo:
    def __init__(self, id: int, attrs: dict[str]) -> None:
        self.id: int = id
        self.description = attrs["description"].strip()
        self.type = attrs["item_type"].strip()
        self.chi = attrs["chi"].strip()
        self.texture_type = attrs["texture_type"].strip()
        self.collision_type = attrs["collision_type"].strip()
        self.hardness = attrs["hardness"].strip()
        self.seed_colours = attrs["seed_colours"].strip()
        self.grow_time = attrs["grow_time"].strip()
        self.default_gem_drop = attrs["default_gem_drop"].strip()
        self.splicing_seed1 = attrs["splicing_seed1"].strip()
        self.splicing_seed2 = attrs["splicing_seed2"].strip()
        self.equip_playmod_text = attrs["equip_playmod_text"].strip()
        self.unequip_playmod_text = attrs["unequip_playmod_text"].strip()
        self.playmod_name = attrs["playmod_name"].strip()
        self.crafting_recipe = attrs["crafting_recipe"]
        self.yield_value = attrs["yield_value"]

async def create_item_names():
    dat_files = glob.glob("**/*.dat", recursive=True)
    items_data = growtopia.ItemsData(dat_files[0])
    await items_data.parse()
    with open("data/item_names.txt", "w") as f:
        f.write("\n".join([item.name for item in items_data.items]))

def find_formatted_name(item: str, file_content: str):
    for line in file_content.split("\n"):
        if line.lower().startswith(item):
            return line

async def find_item(item: str):
    session = aiohttp.ClientSession()
    response = await session.get(
        f"https://growtopia.fandom.com/wiki/{item}", max_redirects=100
    )
    data = await response.read()
    await session.close()
    soup = BeautifulSoup(data, "html.parser")

    attributes = [
        "item_type",
        "chi",
        "texture_type",
        "collision_type",
        "hardness",
        "seed_colours",
        "grow_time",
        "default_gem_drop",
    ]
    results = {}

    try:
        results["description"] = soup.find("div", {"class": "card-text"}).text

        if "|" in results["description"]:
            results["description"] = results["description"].replace("|", " ")
    except AttributeError:
        results["description"] = "This item has no description!"

    try:
        data_field = soup.find(attrs={"class": "card-field"})
    except Exception as e:
        print(e)
        return

    # Finding each of the attributes in the card-field class (type, chi, hardness, etc)
    for i, attr in enumerate(attributes):
        try:
            node = data_field.find("tbody").find("tr")
            for _ in range(i):
                node = node.find_next("tr")
            results[attr] = node.find("td").text
        except AttributeError:
            results[attr] = "None"

    # Some stupid space missing from webscraping the hardness
    if "hardness" in results:
        results["hardness"] = results["hardness"].replace(
            "HitsRestores", "Hits. Restores"
        )

    # Finding the crafting recipe
    try:
        crafting_recipe = []

        items = (
            soup.find("table", {"class": "content"})
            .find_all("tr")
        )

        first_item = items[2].find("td").find("a").text + f" {items[2].find('td').find('b').text}"
        second_item = items[3].find("td").find("a").text + f" {items[3].find('td').find('b').text}"
        third_item = items[4].find("td").find("a").text + f" {items[4].find('td').find('b').text}"
        yield_value = int(items[5].find("td").find("b").text)

        crafting_recipe.append(first_item)
        crafting_recipe.append(second_item)
        crafting_recipe.append(third_item)

        results["crafting_recipe"] = crafting_recipe
        results["yield_value"] = yield_value
    except AttributeError:
        results["crafting_recipe"] = ""
        results["yield_value"] = ""

    # Finding the splicing seeds
    try:
        splicing_seeds = soup.find(
            attrs={
                "class": "recipebox",
                "style": "background: #66cc66; color: #006600;",
            }
        )

        all_recipe_boxes = soup.find_all(attrs={"class": "recipebox"})

        obtainable_from_consumable = soup.find(
            attrs={
                "class": "recipebox",
                "style": "background: #00CCCC; color: #004c4d;"
            }
        )
        
        results["splicing_seed1"] = (
            splicing_seeds.find("tr").find_next("tr").find_next("tr").find("a").text
        )
        results["splicing_seed2"] = (
            splicing_seeds.find("tr")
            .find_next("tr")
            .find_next("tr")
            .find("a")
            .find_next("a")
            .text
        )
        
        if splicing_seeds is not None:
            if results["crafting_recipe"] != "" and obtainable_from_consumable is not None and len(all_recipe_boxes) > 3:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"
            
            elif results["crafting_recipe"] != "" and obtainable_from_consumable is None and len(all_recipe_boxes) > 2:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"

            elif results["crafting_recipe"] == "" and obtainable_from_consumable is not None and len(all_recipe_boxes) > 2:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"
            
            elif results["crafting_recipe"] == "" and obtainable_from_consumable is None and len(all_recipe_boxes) > 1:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"
        

    except AttributeError:
        results["splicing_seed1"] = "Blank"
        results["splicing_seed2"] = "Blank"

    # Finding the equip playmod text
    try:
        results["equip_playmod_text"] = soup.find(
            "td", {"style": "color:#199e24; padding:0px 20px; font-style: italic"}
        ).text
    except AttributeError:
        results["equip_playmod_text"] = ""

    # Finding the unequip playmod text
    try:
        results["unequip_playmod_text"] = soup.find(
            "td", {"style": "color:#9e2a18; padding:0px 20px; font-style: italic"}
        ).text
    except AttributeError:
        results["unequip_playmod_text"] = ""

    # Finding the playmod name
    try:
        if (
            results["equip_playmod_text"] != ""
            and results["unequip_playmod_text"] != ""
        ):
            results["playmod_name"] = (
                soup.find("div", {"class": "mw-parser-output"})
                .find("p")
                .find_next("p")
                .find("i")
                .text
            )
        else:
            results["playmod_name"] = ""
    except AttributeError:
        results["playmod_name"] = ""

    return(ItemInfo(results))


def parse_data(id: int, data: bytes) -> ItemInfo:
    soup = BeautifulSoup(data, "html.parser")

    attributes = [
        "item_type",
        "chi",
        "texture_type",
        "collision_type",
        "hardness",
        "seed_colours",
        "grow_time",
        "default_gem_drop",
    ]
    results = {}

    try:
        results["description"] = soup.find("div", {"class": "card-text"}).text

        if "|" in results["description"]:
            results["description"] = results["description"].replace("|", " ")
    except AttributeError:
        results["description"] = "This item has no description!"

    try:
        data_field = soup.find(attrs={"class": "card-field"})
    except Exception as e:
        print(e)
        return

    # Finding each of the attributes in the card-field class (type, chi, hardness, etc)
    for i, attr in enumerate(attributes):
        try:
            node = data_field.find("tbody").find("tr")
            for _ in range(i):
                node = node.find_next("tr")
            results[attr] = node.find("td").text
        except AttributeError:
            results[attr] = "None"

    # Some stupid space missing from webscraping the hardness
    if "hardness" in results:
        results["hardness"] = results["hardness"].replace(
            "HitsRestores", "Hits. Restores"
        )

    # Finding the crafting recipe
    try:
        crafting_recipe = []

        items = (
            soup.find("table", {"class": "content"})
            .find_all("tr")
        )

        first_item = items[2].find("td").find("a").text + f" {items[2].find('td').find('b').text}"
        second_item = items[3].find("td").find("a").text + f" {items[3].find('td').find('b').text}"
        third_item = items[4].find("td").find("a").text + f" {items[4].find('td').find('b').text}"
        yield_value = int(items[5].find("td").find("b").text)

        crafting_recipe.append(first_item)
        crafting_recipe.append(second_item)
        crafting_recipe.append(third_item)

        results["crafting_recipe"] = crafting_recipe
        results["yield_value"] = yield_value
    except AttributeError:
        results["crafting_recipe"] = ""
        results["yield_value"] = ""

    # Finding the splicing seeds
    try:
        splicing_seeds = soup.find(
            attrs={
                "class": "recipebox",
                "style": "background: #66cc66; color: #006600;",
            }
        )

        all_recipe_boxes = soup.find_all(attrs={"class": "recipebox"})

        obtainable_from_consumable = soup.find(
            attrs={
                "class": "recipebox",
                "style": "background: #00CCCC; color: #004c4d;"
            }
        )
        
        results["splicing_seed1"] = (
            splicing_seeds.find("tr").find_next("tr").find_next("tr").find("a").text
        )
        results["splicing_seed2"] = (
            splicing_seeds.find("tr")
            .find_next("tr")
            .find_next("tr")
            .find("a")
            .find_next("a")
            .text
        )

        if splicing_seeds is not None:
            if results["crafting_recipe"] != "" and obtainable_from_consumable is not None and len(all_recipe_boxes) > 3:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"
            
            elif results["crafting_recipe"] != "" and obtainable_from_consumable is None and len(all_recipe_boxes) > 2:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"

            elif results["crafting_recipe"] == "" and obtainable_from_consumable is not None and len(all_recipe_boxes) > 2:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"
            
            elif results["crafting_recipe"] == "" and obtainable_from_consumable is None and len(all_recipe_boxes) > 1:
                results["splicing_seed1"] = "Blank"
                results["splicing_seed2"] = "Blank"

    except AttributeError:
        results["splicing_seed1"] = "Blank"
        results["splicing_seed2"] = "Blank"

    # Finding the equip playmod text
    try:
        results["equip_playmod_text"] = soup.find(
            "td", {"style": "color:#199e24; padding:0px 20px; font-style: italic"}
        ).text
    except AttributeError:
        results["equip_playmod_text"] = ""

    # Finding the unequip playmod text
    try:
        results["unequip_playmod_text"] = soup.find(
            "td", {"style": "color:#9e2a18; padding:0px 20px; font-style: italic"}
        ).text
    except AttributeError:
        results["unequip_playmod_text"] = ""

    # Finding the playmod name
    try:
        if (
            results["equip_playmod_text"] != ""
            and results["unequip_playmod_text"] != ""
        ):
            results["playmod_name"] = (
                soup.find("div", {"class": "mw-parser-output"})
                .find("p")
                .find_next("p")
                .find("i")
                .text
            )
        else:
            results["playmod_name"] = ""
    except AttributeError:
        results["playmod_name"] = ""

    return Parse_ItemInfo(id, results)

if __name__ == "__main__":
    while True:
        try:
            if "data/item_names.txt" not in os.listdir():
                asyncio.run(create_item_names())

            with open("data/item_names.txt", "r") as f:
                file_content = f.read()

            with open("data/item_names.txt", "r") as f:
                file_content = f.read()

            inp = input("Enter item name: ")
            start_time = time.time()
            correct_name = find_formatted_name(inp, file_content)
            if correct_name:
                item_info = asyncio.run(find_item(correct_name))
                print(f"Description: {item_info.description}")
                print(f"Type: {item_info.type}")
                print(f"Chi: {item_info.chi}")
                print(f"Texture type: {item_info.texture_type}")
                print(f"Collision type: {item_info.collision_type}")
                print(f"Item hardness: {item_info.hardness}")
                print(f"Seed colours: {item_info.seed_colours}")
                print(f"Grow time: {item_info.grow_time}")
                print(f"Default gem drop: {item_info.default_gem_drop}")
                if (
                    item_info.splicing_seed1 == "Blank"
                    and item_info.splicing_seed2 == "Blank"
                ):
                    print(f"This item cannot be spliced")
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
                    print(
                        f"Unequip playmod text: {item_info.unequip_playmod_text.strip()}"
                    )
                if item_info.playmod_name == "":
                    print(f"This item has no playmod")
                else:
                    print(f"Playmod name: {item_info.playmod_name}")
                if item_info.crafting_recipe == "":
                    print(f"This item has no crafting recipe")
                else:
                    print(f"Mix together {item_info.crafting_recipe[0]}, {item_info.crafting_recipe[1]}, and {item_info.crafting_recipe[2]} to get {item_info.yield_value} of this item")
                print(
                    f"Process completed in",
                    int((time.time() - start_time) * 1000),
                    "milliseconds\n\n\n",
                )
        except KeyboardInterrupt:
            break