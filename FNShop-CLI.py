import fortniteShop as fs
import requests as web

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from io import StringIO

import colorama
import pandas
import tabulate
import typer
import datetime
import json
import string
import os
import pyautogui
import time

app = typer.Typer()

@app.command()
def print_shop(
    variants: bool = False, 
    new: bool = False, 
    leaving: bool = False, 
    dropin: bool = False, 
    categories: bool = False, 
    sections: bool = False, 
    assetType: str = None,
    sort: str = None,
    sortType: str = "ascending"
    ) -> None:
    localVars = locals()
    
    argCount = 0
    for argument, value in localVars.items():
        if value and argument not in ["sort", "sortType"]:
            argCount += 1
            
    if argCount >= 2: raise ValueError(f"not able to process more than 1 parameter")    
    
    assetTypes = ["Outfit", "Pickaxe", "Backbling", "Glider", "Shoes", "Wrap", "Emote", "Jam Track", "Dynamic Bundle", "Real Money Pack", "Guitar", "Keytar", "Microphone", "Drums"]
    if assetType and assetType.lower() == "--help":
        print(f"Valid arguments: " + colorama.Fore.GREEN + ", ".join(assetTypes) + colorama.Style.RESET_ALL) 
        exit()
    if assetType and assetType.lower() not in [item.lower() for item in assetType]:
        raise ValueError(f"'{assetType}' is not a valid argument {assetTypes}")
    assetType = assetTypes[[item.lower() for item in assetTypes].index(assetType.lower())] if assetType else assetType
    
    sortTypes = ["section", "category", "name", "inDate", "outDate", "hasVariants", "assetType"]
    if sort and sort.lower() == "--help":
        print(f"Valid Arguments: " + colorama.Fore.GREEN + ", ".join(sortTypes) + colorama.Style.RESET_ALL)
        exit()
    if sort and sort.lower() not in [item.lower() for item in sortTypes]:
        raise ValueError(f"'{sort}' is not a Valid Argument {sortTypes}")
    sort = sortTypes[[item.lower() for item in sortTypes].index(sort.lower())] if sort else sort
    
    sortAttributes = ["ascending", "descending"]
    if sortType.lower() not in [item.lower() for item in sortAttributes]:
        raise ValueError(f"'{sortType}' is not a Valid Argument {sortAttributes}")
    sortType = sortAttributes[[item.lower() for item in sortAttributes].index(sortType.lower())] if sortType else sortType
    
    todayDate = datetime.datetime.now()
    today = f"{todayDate.year}-{todayDate.month}-{todayDate.day + 1}" if todayDate.hour >= 17 and todayDate.hour <= 23 else f"{todayDate.year}-{todayDate.month}-{todayDate.day}"

    
    def legendcolor(row):
        match row["Color"]:
            case "Green":
                return [colorama.Fore.GREEN + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, str) else cell for cell in row]
            case "Yellow": 
                return [colorama.Fore.YELLOW + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, str) else cell for cell in row] 
            case "Red":
                return [colorama.Fore.RED + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, str) else cell for cell in row] 
            case "Cyan":
                return [colorama.Fore.CYAN + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, str) else cell for cell in row]
    
    def color(row):
        if row["inDate"] == today and row["outDate"] == today:
            return [colorama.Fore.YELLOW + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, (str, bool)) else cell for cell in row]
        elif row["inDate"] == today:
            return [colorama.Fore.GREEN + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, (str, bool)) else cell for cell in row]
        elif row["outDate"] == today:
            return [colorama.Fore.RED + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, (str, bool)) else cell for cell in row]
        else:
            return [colorama.Fore.CYAN + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, (str, bool)) else cell for cell in row]
    
    legend = [
        {"Color" : "Green", "Meaning" : "New"},
        {"Color" : "Yellow", "Meaning" : "New and Leaving Next Rotation"},
        {"Color" : "Red", "Meaning" : "Leaving Next Rotation"},
        {"Color" : "Cyan", "Meaning" : "Same as last Rotation"}
        ]
    
        
    
    legendDF = pandas.DataFrame(legend)                        
    legendlist = legendDF.apply(legendcolor, axis=1).to_list()
    
    table = tabulate.tabulate(legendlist, headers=legendDF.columns, tablefmt="grid")
    
    print("Legend:\n" + table)
    
    shop = fs.shop()
    
    #Offline Running
    #shop = fs.shop(True)
    #file = open("data.json", "r", encoding="utf-8")
    #shop.RAWdata = file.read() 
    #shop.parsed
        
    if variants: df = pandas.read_json(StringIO(shop.varaints(True)))
    elif new: df = pandas.read_json(StringIO(shop.new))
    elif leaving: df = pandas.read_json(StringIO(shop.leaving))
    elif dropin: df = pandas.read_json(StringIO(shop.dropin))
    elif categories: categoryList = [shop.category(category) for category in sorted(shop.categories)] 
    elif sections: sectionsList = [shop.section(section) for section in sorted(shop.sections)]
    elif assetType: df = pandas.read_json(StringIO(shop.assetType(assetType.lower())))
    else: df = pandas.DataFrame(shop.parsed)
    
    if  sections or categories:
        for data in sectionsList if sections else categoryList:
            df = pandas.read_json(StringIO(data))
            print(f"\n{df["section"].loc[df.index[0]]}:")
            if sort is not None: df = df.sort_values(by = f"{sort}", ascending= True if sortType == "ascending" else False) 
            df["assetType"] = df["assetType"].apply(lambda x: string.capwords(x))
            dataList = df.apply(color, axis = 1).values.tolist()
            print(tabulate.tabulate(dataList, headers=df.columns, tablefmt="grid"))
    else:
        if sort is not None: df = df.sort_values(by = f"{sort}", ascending= True if sortType == "ascending" else False) 
        df["assetType"] = df["assetType"].apply(lambda x: string.capwords(x))
        dataList = df.apply(color, axis = 1).values.tolist()
        print(tabulate.tabulate(dataList, headers=df.columns, tablefmt="grid"))
    
    print(f"\nNext Shop Rotation in: {17 - todayDate.hour if todayDate.hour < 17 else 17 + (23 - todayDate.hour)} hours")

@app.command()
def expand_bundles():
    shop = fs.shop()
    #Offline Running
    #file = open("data.json", "r", encoding="utf-8")
    #shop.RAWdata = file.read() 
    #shop.parsed
    
    if not json.loads(shop.RAW).get("catalog", None):
        raise KeyError("Missing 'catalog' Key")
    
    if not json.loads(shop.RAW)["catalog"].get("categories", None):
        raise KeyError("Missing 'categories' Key")
    
    bundles = {}
    request = web.get("https://fortnite-api.com/v2/cosmetics")
    
    if request.status_code != 200:
        raise ConnectionError("API is not Responding")
    
    allItems = {
        "br" : request.json()["data"]["br"],
        "tracks" : request.json()["data"]["tracks"],
        "instruments" : request.json()["data"]["instruments"],
        "cars" : request.json()["data"]["cars"],
        "lego" : request.json()["data"]["lego"],
        "legokits" : request.json()["data"]["legoKits"],
        "beans" : request.json()["data"]["beans"]
    }
    for item in (
        item
        for category in json.loads(shop.RAW)["catalog"]["categories"]
        for section in category["sections"]
        for offer in section["offerGroups"]
        for item in offer["items"]
    ):
                    
        if item["assetType"] != "staticbundle" and item["assetType"] != "dynamicbundle":
            continue
        
        itemsInBundle = []
        
                
        for bundlePiece in item["ownershipCalculationData"]["itemGrantTemplateIds"]:
            for catagory in allItems:
                itemIds = list(map(lambda x: x["id"].lower(), allItems[catagory]))
                if bundlePiece.split(":")[1] in itemIds:
                    itemsInBundle.append(f"{allItems[catagory][itemIds.index(bundlePiece.split(":")[1])]["name"] if catagory != "tracks" else allItems[catagory][itemIds.index(bundlePiece.split(":")[1])]["title"]} ({allItems[catagory][itemIds.index(bundlePiece.split(":")[1])]["type"]["displayValue"] if catagory != "tracks" else "Jam Track"})")
                    break    
                elif list(allItems.keys()).index(catagory) == len(allItems) -1:
                    itemsInBundle.append(f"{bundlePiece.split(":")[1]} ({bundlePiece.split(":")[0].replace("Token", "").replace("Cosmetic","")})")
                
                    
        
        bundles[item["title"]] = itemsInBundle     
                    
    for bundle in sorted(list(bundles)):
        print("\n", bundle)
        
        for item in bundles[bundle]:
            print("   |")            
            print(f"   └──[ {item}" if bundles[bundle].index(item) == len(bundles[bundle]) - 1 else f"   ├──[ {item}")            

@app.command()
def archive_wip(fileName: str = "Output", outputFolder: str = None, images: bool = False, force: bool = False):
    
    #Offline Use
    #shop = fs.shop(True)
    #file = open("data.json", "r")
    #shop.RAWdata = file.read()
    #shop.parsed
    outputFolder = outputFolder.replace("/", "\\") if outputFolder else outputFolder
    
    filepath = os.path.join(outputFolder if outputFolder else ".", f"{fileName}.json")
    
    if outputFolder:
        if not os.path.exists(os.path.abspath(outputFolder)):
            os.makedirs(os.path.abspath(outputFolder))
    if os.path.exists(filepath) and not force:
        raise FileExistsError(f"'{filepath}' already exists use --force to replace")
    
    shop = fs.shop()
    if not images:
        try:
            with open(filepath, "w") as file:
                data = shop.parsed
                for item in data:
                    item["dateExtracted"] = datetime.datetime.now().strftime("%d-%m-%YT%H:%M")
                data = json.dumps(data, indent=4)
                file.write(data)
            print(f"Data Archived at: {filepath}")
            exit()
        except Exception as e:
            print(f"Failed to Save File: {e}")
            exit()
    
    data = json.loads(shop.RAW)
    if not data.get("catalog", None):
        raise KeyError("Missing 'catalog' Key")
    if not data["catalog"].get("categories", None):
        raise KeyError("Missing 'categories' Key")

    data = data["catalog"]["categories"]
    itemShop = []
    
    for category in data:
        for section in category["sections"]:
            for offer in section["offerGroups"]:
                for item in offer["items"]:
                    
                    inDate = item.get("inDate", None)
                    outDate = item.get("outDate", None)
                    
                    item_dict = {
                        "name" : item.get("title", None).replace("&amp;", "&"),
                        "category" : category["navLabel"].replace("&amp;", "&"),
                        "section" : section["displayName"].replace("&amp;", "&"),
                        "assetType" : item["assetType"].replace("dynamicbundle", "dynamic bundle").replace("jamtrack", "jam track").replace("rmtpack", "real money pack").replace("staticbundle", "static bundle"),
                        "price" : (str(item["pricing"]["finalPrice"]) + " V-Bucks") if item["assetType"] != "rmtpack" else "$" + "".join([x for x in str(item["pricing"]["finalPrice"])[:len(str(item["pricing"]["finalPrice"]))-2]]) + "." + str(item["pricing"]["finalPrice"])[-2:],
                        "inDate" : inDate if inDate == None else inDate.split("T")[0] if "T" in inDate else inDate,
                        "outDate" : outDate if outDate == None else outDate.split("T")[0] if "T" in outDate else outDate,
                        "hasVariants" : item.get("hasVariants", None),
                        "image" : item["image"].get("lg").replace("&amp;", "&") if item.get("image", None) and item["image"].get("lg", None) else None 
                        
                    }
                    itemShop.append(item_dict)
                    del item_dict
                
    
    with open(filepath, "w") as file:
        file.write(json.dumps(itemShop, indent=4))
    
    if not os.path.exists(os.path.abspath(os.path.join(outputFolder, "images"))):
        os.makedirs(os.path.abspath(os.path.join(outputFolder, "images")), exist_ok=True)
    
    driver = webdriver.Edge()
    for item in itemShop:
        imagePath = os.path.join(outputFolder if outputFolder else ".", "images", f"{"".join(char if char not in ["<", ">", ":", "\"", "/", "\\", "|", "?","*"] else "" for char in item["name"]).replace(" ", "-") }.png")
        if item["image"]: 
            if os.path.exists(imagePath):
                imagePath = os.path.join(outputFolder if outputFolder else ".", "images", f"{"".join(char if char not in ["<", ">", ":", "\"", "/", "\\", "|", "?","*"] else "" for char in item["name"]).replace(" ", "-") }-{item["assetType"].replace(" ", "-")}.png")
            driver.get(item["image"]) 
            img = driver.find_element(By.TAG_NAME, "img")
            #action = ActionChains(driver)
            #action.move_to_element(img).context_click().perform()
            pyautogui.hotkey("ctrl", "s")
            time.sleep(2)
            pyautogui.write(os.path.abspath(imagePath), interval=0.05)
            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(2)



if __name__ == "__main__":
    app()