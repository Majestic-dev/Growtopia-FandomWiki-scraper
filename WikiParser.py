import asyncio

import growtopia

from ItemSearch import find_item2


async def main():
    items_data = growtopia.ItemsData("")  # Specify the path to your items.dat file here
    await items_data.parse()
    i = -1

    with open("itemNames.txt", "w") as f:
        f.write("\n".join([item.name for item in items_data.items]))

    with open("items.txt", "w") as f:
        for item in items_data.items:
            i += 1
            if "&" in item.name.lower():
                f.write(f"{i}|None|Blank|Blank|None|\n")
            elif "seed" not in item.name.lower() and "null" not in item.name.lower():
                item_info = await find_item2(item.name)
                f.write(
                    f"{i}|{item_info.description}|{item_info.splicing_seed1}|{item_info.splicing_seed2}|{item_info.chi}|{item_info.playmod_name}\n"
                )
                print(item.name)

    await playmods()
    await remove_duplicates()
    await merge_lines()


async def find_name_by_number(line: int):
    with open("itemNames.txt", "r") as f:
        item_names = f.readlines()

    item_name = item_names[line].strip()
    return item_name


async def remove_duplicates():
    lines_seen = set()
    updated_lines = []

    with open("playmods.txt", "r") as f:
        lines = f.readlines()

        for line in lines:
            if line not in lines_seen:
                lines_seen.add(line)
                updated_lines.append(line)

    with open("playmods.txt", "w") as f:
        f.writelines(updated_lines)


async def merge_lines():
    merged_lines = []

    with open("playmods.txt", "r") as f:
        lines = f.readlines()

        for line in lines:
            if line.startswith("|") and merged_lines:
                merged_lines[-1] = merged_lines[-1].rstrip() + line
            else:
                merged_lines.append(line)

    with open("playmods.txt", "w") as f:
        f.writelines(merged_lines)


async def playmods():
    with open("items.txt", "r") as f:
        lines = f.readlines()

    res = ""

    for line in lines:
        components = line.strip().split("|")
        playmod_name = components[-1]

        if playmod_name != "":
            try:
                itemname = await find_name_by_number(int(components[0]))
                item = await find_item2(itemname)

                res += f"{item.playmod_name}|{item.equip_playmod_text}|{item.unequip_playmod_text}\n"
                print(f"Found {item.playmod_name} for {itemname}")
            except ValueError as e:
                print(e)

    with open("playmods.txt", "w") as f:
        f.write(res)


asyncio.run(merge_lines())
