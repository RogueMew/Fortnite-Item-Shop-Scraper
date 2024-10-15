from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import git
import datetime

def getDate() -> str:
    currentDateTime = datetime.datetime.now()
    if int(datetime.datetime.now().strftime("%H")) >= 17 and int(datetime.datetime.now().strftime("%H")) <= 23:
        currentDate = f'{currentDateTime.year}-{currentDateTime.month}-{str(currentDateTime.day+1)}'
    else:
        currentDate = f'{currentDateTime.year}-{currentDateTime.month}-{currentDateTime.day}'
    return currentDate
def updateReadMe() -> str:
    readme = open("README.md", "w", encoding="utf-8")
    readme.write("# Fortnite Item Shop Historical Viewer\n")
    readme.write(f"## [Toadys shop as Markdown](https://github.com/RogueMew/Fortnite-Item-Shop-Historical/blob/main/Output/{getDate()}-ItemShop.md)- {getDate()}")
    readme.close()
    return "README.md"
def markDownItemShop()->None:
    driver = webdriver.Edge()
    driver.get("https://www.fortnite.com/item-shop?lang=en-US&_data=routes%2Fitem-shop._index")
    content = json.loads(driver.find_element(By.CSS_SELECTOR, 'div[hidden="true"]').get_attribute('textContent'))
    driver.close()
    itemshop = []
    for catagory in content['catalog']['categories']:
        for section in catagory['sections']:
            for offer in section['offerGroups']:
                inDate = offer.get('inDate', None)
                outDate = offer.get('outDate', None)
                for item in offer['items']:
                    if not inDate:
                        inDate = item.get('inDate', 'UnkownT')
                    if not outDate:
                        outDate = item.get('outDate', 'UnkownT')
                    item_dict = {
                        "name" : item['title'],
                        'catagory' : catagory['navLabel'],
                        'section' : section['displayName'],
                        'type' : item['assetType'],
                        'price' : str(item['pricing']['finalPrice']) + " vbucks",
                        'inDate' : inDate.split("T")[0],
                        'outDate' : outDate.split("T")[0],
                        'image' : item['image'].get('lg', 'None')
                    }
                    itemshop.append(item_dict)
    filename = f"Markdown/{getDate()}-ItemShop.md"
    MarkDown = open(f"Markdown/{getDate()}-ItemShop.md", "w", encoding="utf-8") 
    catagory = ""
    section = ""
    for item in itemshop:
        if catagory != item["catagory"]:
            catagory = item["catagory"]
            MarkDown.write(f"\n# {item["catagory"]}")
        if section != item["section"]:
            section = item["section"]
            MarkDown.write(f"\n## {item["section"]}")
        if item['inDate'] == getDate():
            MarkDown.write(f"\n### ***NEW*** {item['name']} - {item['price']}\n### Joined {item['inDate']} - Leaving {item['outDate']}\n   ![Image of Skin]({item['image']})")
        elif item['outDate'] == getDate():
            MarkDown.write(f"\n### ***LEAVING*** {item['name']} - {item['price']}\n### Joined {item['inDate']} - Leaving {item['outDate']}\n   ![Image of Skin]({item['image']})")
        else:
            MarkDown.write(f"\n### {item['name']} - {item['price']}\n### Joined {item['inDate']} - Leaving {item['outDate']}\n   ![Image of Skin]({item['image']})")
    MarkDown.close()
    repo = git.Repo('C:/Users/ewklu/OneDrive/Desktop/Github_Repos/Fortnite-Item-Shop-Historical')
    repo.index.add([filename, updateReadMe()])
    print("File Added to Commit")
    
    print("Repo Commited")
    origin = repo.remote(name='origin') 
  
    existing_branch = repo.heads['Testing'] 
    existing_branch.checkout() 
    repo.index.commit(f"{getDate()} Item Shop")
    print('Commited successfully') 
    origin.push() 
    print("Completed Functions")
    print("Closing app")
    exit()

markDownItemShop()