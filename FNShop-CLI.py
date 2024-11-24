import fortniteShop as fs

from io import StringIO

import colorama
import pandas
import tabulate
import typer
import datetime
import inspect
import json

app = typer.Typer()

@app.command()
def print_shop(variants: bool = False, leaving: bool = False, new: bool = False, catagories: bool = False, sections: bool = False) -> None:
    argCount = 0

    for argument in inspect.getfullargspec(print_shop).args:
        if argument == False: 
            argCount += 1
    
    if argCount >= 2: raise ValueError("not able to process more than 1 parameter")    
    
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
        today = datetime.datetime.now()
        today = f"{today.year}-{today.month}-{today.day + 1}" if today.hour >= 17 and today.hour <= 23 else f"{today.year}-{today.month}-{today.day}"
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
        exit()
    elif sections: 
        for section in sorted(shop.sections):
            print("\n"+section+": ")
            df = pandas.read_json(StringIO(shop.section(section)))
            dataList = df.apply(color, axis=1).values.tolist()
            print(tabulate.tabulate(dataList, headers=df.columns, tablefmt="grid"))
    else: df = pandas.DataFrame(shop.parsed)
    
    if not sections:
        dataList = df.apply(color, axis=1).values.tolist()
        print(tabulate.tabulate(dataList, headers=df.columns, tablefmt="grid"))
    
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
    
    for category in json.loads(shop.RAW)["catalog"]["categories"]:
        for section in category["sections"]:
            for offer in section["offerGroups"]:
                for item in offer["items"]:
                    if item["assetType"] != "staticbundle" and item["assetType"] != "dynamicbundle":
                        continue
                    itemsInBundle = []
                    
                    for bundlePiece in item["ownershipCalculationData"]["itemGrantTemplateIds"]:
                        itemsInBundle.append(bundlePiece.split(":")[1])
                    
                    bundles[item["title"]] = itemsInBundle     
                    
    for bundle in list(bundles.keys()):
        print("\n", bundle)
        
        for item in bundles[bundle]:
            print("   |")            
            print(f"   └──[{item}" if bundles[bundle].index(item) == len(bundles[bundle]) - 1 else f"   ├──[{item}")            
   
    
if __name__ == "__main__":
    app()