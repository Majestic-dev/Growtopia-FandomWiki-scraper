from time import time

from item_search import parse_data, Parse_ItemInfo as ItemInfo
from growtopia import ItemsData
from asyncio import run
from requests import get

from threading import Thread, Lock

lock = Lock()
item_info: dict[int, ItemInfo] = {}


items_data = ItemsData("") # Path to your items.dat file
run(items_data.parse())

string = ""
threads = []


def get_item_info(item: str, item_id: int) -> None:
    global item_info

    try:
        info = parse_data(
            item_id,
            get(
                f"https://growtopia.fandom.com/wiki/{item}", allow_redirects=True
            ).content,
        )

        with lock:
            item_info[item_id] = info

    except Exception as e:
        print(e)

    print(f"Finished {item}, {item_id}")


start_time = time()

for item in items_data.items:
    if "&" in item.name.lower():
        string += f"{item.id}|None|Blank|Blank|None|\n"
    elif "seed" not in item.name.lower() and "null" not in item.name.lower():
        threads.append(Thread(target=get_item_info, args=(item.name, item.id)))


for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

for item in item_info.values():
    string += f"{item.id}|{item.splicing_seed1}|{item.splicing_seed2}\n"

with open("items.txt", "w") as f:
    f.write(string)

print(f"Finished in {time() - start_time} seconds")
