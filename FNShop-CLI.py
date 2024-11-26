import fortniteShop as fs
import requests as web

from io import StringIO

import colorama
import pandas
import tabulate
import typer
import datetime
import inspect
import json
import time

app = typer.Typer()

@app.command()
def print_shop(variants: bool = False, leaving: bool = False, new: bool = False, catagories: bool = False, sections: bool = False, assetType: str = None) -> None:
    argCount = 0
        
    for argument in inspect.getfullargspec(print_shop).args:
        if argument == False or argument is None: 
            argCount += 1
    
    if argCount >= 2: raise ValueError("not able to process more than 1 parameter")    
    assetTypes = ["outfit", "pickaxe", "backbling", "glider", "shoes", "wrap", "emote", "jam tack", "dynamic bundle", "real money pack", "guitar", "keytar", "microphone"]
    if assetType and assetType.lower() not in assetTypes:
        raise ValueError(f"'{assetType}' is not a valid argument {assetTypes}")
            
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
            return [colorama.Fore.YELLOW + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, (str)) else cell for cell in row]
        elif row["inDate"] == today:
            return [colorama.Fore.GREEN + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, (str)) else cell for cell in row]
        elif row["outDate"] == today:
            return [colorama.Fore.RED + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, (str)) else cell for cell in row]
        else:
            return [colorama.Fore.CYAN + str(cell) + colorama.Style.RESET_ALL if isinstance(cell, str) else cell for cell in row]
    
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
    #file = open("data.json", "r", encoding="utf-8")
    #shop.RAWdata = file.read() 
    #shop.parsed
        
    if variants: df = pandas.read_json(StringIO(shop.varaints(True)))
    elif leaving: df = pandas.read_json(StringIO(shop.leaving))
    elif new: df = pandas.read_json(StringIO(shop.new))
    elif catagories: 
        for category in sorted(shop.categories):
            print("\n"+category+": ")
            df = pandas.read_json(StringIO(shop.category(category)))
            dataList = df.apply(color, axis=1).values.tolist()
            print(tabulate.tabulate(dataList, headers=df.columns, tablefmt="grid"))
    elif sections: 
        for section in sorted(shop.sections):
            print("\n"+section+": ")
            df = pandas.read_json(StringIO(shop.section(section)))
            dataList = df.apply(color, axis=1).values.tolist()
            print(tabulate.tabulate(dataList, headers=df.columns, tablefmt="grid"))
    elif assetType: df = pandas.read_json(StringIO(shop.assetType(assetType.lower())))
    else: df = pandas.DataFrame(shop.parsed)
    
    if not sections:
        dataList = df.apply(color, axis=1).values.tolist()
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

if __name__ == "__main__":
    app()