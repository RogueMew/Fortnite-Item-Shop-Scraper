from selenium import webdriver
from selenium.webdriver.common.by import By
import requests as web
import json
import git
import datetime
import os

def getDate() -> str:
    currentDateTime = datetime.datetime.now()
    if int(datetime.datetime.now().strftime("%H")) >= 17 and int(datetime.datetime.now().strftime("%H")) <= 23:
        currentDate = f'{currentDateTime.year}-{currentDateTime.month}-{str(currentDateTime.day+1)}'
    else:
        currentDate = f'{currentDateTime.year}-{currentDateTime.month}-{currentDateTime.day}'
    return currentDate

def checkSameDate(date) -> bool:
    return date == getDate()

def capFirst(string) ->str:
    return string[0].upper() + string[1:]

def imageDownload(url, name):
    if os.path.isdir(f'./images/{getDate()}') == False:
        os.mkdir(f'./images/{getDate()}')
    with open('images/' + f'{getDate()}/' + name.replace(' ', '-').replace('|', '-') + '.png', "wb") as f:
        f.write(web.get(url).content)

def updateReadMe() -> str:
    readme = open("README.md", "w", encoding="utf-8")
    readme.write("# Fortnite Item Shop Historical Viewer\n")
    readme.write(f"## [Toadys Shop as Markdown](https://github.com/RogueMew/Fortnite-Item-Shop-Historical/blob/main/Markdown/{getDate()}-ItemShop.md)- {getDate()}\n## [Todays Item Shop Images](https://github.com/RogueMew/Fortnite-Item-Shop-Historical/tree/main/images/{getDate()})")
    readme.close()
    return "README.md"

def scraping()->None:
    driver = webdriver.Edge()
    driver.get("https://www.fortnite.com/item-shop?lang=en-US&_data=routes%2Fitem-shop._index")
    content = json.loads(driver.find_element(By.CSS_SELECTOR, 'div[hidden="true"]').get_attribute('textContent'))
    driver.close()
    print("Scraped Site, Compiling into Markdown and Downloading images")
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
                        'image' : item['image'].get('lg', None),
                        'urlExstension' : item.get('urlName', None),
                        'imageLocal' : item['title'].replace(' ', '-').replace('|', '-') + '.png'
                    }
                    if item_dict['type'] == 'dynamicbundle':item_dict['type'] = 'bundle'
                    if item_dict['type'] == 'vmtpack':item_dict['type'] = 'pack'
                    if item_dict['type'] == 'jamtrack':item_dict['type'] = 'jam-Track'
                    if item_dict['type'] == 'legokits': item_dict['type'] = 'lego-Kit'
                    itemshop.append(item_dict)
    MarkDown = open(f"Markdown/{getDate()}-ItemShop.md", "w", encoding="utf-8") 
    filename = f"Markdown/{getDate()}-ItemShop.md"
    catagory = ""
    section = ""
    for item in itemshop:
        
        if catagory != item["catagory"]:
            catagory = item["catagory"]
            MarkDown.write(f"\n# {item["catagory"]}")
        
        if section != item["section"]:
            section = item["section"]
            MarkDown.write(f"\n## {item["section"]}")
        
                
        if item['image'] != None:
            imageDownload(item['image'], item['name'])
        
        if item['type'] == 'Rmtpack':
            MarkDown.write(f'\n### {item['name']} - Costs Real Money\n[Link to {item['name']} in the Epic Games Stor]({item['urlExstension']})')

        elif item['image'] != None and item['urlExstension'] != None:
            if checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **LEAVING NEXT ROTATION** {item['name']} - {capFirst(item['type'])} - {item['price']} -  Leaving: {item['outDate']}\n[![Image of {item['name']}](../images/{getDate()}/{item['imageLocal']})](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
            elif checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **NEW** {item['name']} - {capFirst(item['type'])} - {item['price']} -  Leaving: {item['outDate']}\n[![Image of {item['name']}](../images/{getDate()}/{item['imageLocal']})](https://www.fortnite.com/item-shop/{item['type'] +'s'}/{item['urlExstension']}?lang=en-US)')
            else:
                MarkDown.write(f'\n### {item['name']} - {capFirst(item['type'])} - {item['price']} -  Leaving: {item['outDate']}\n[![Image of {item['name']}](../images/{getDate()}/{item['imageLocal']})](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
        
        elif item['image'] == None and item['urlExstension'] != None:
            if checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **LEAVING NEXT ROTATION** {item['name']} - {capFirst(item['type'])} - {item['price']} -  Leaving: {item['outDate']}\n[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
            elif checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **NEW** {item['name']} - {capFirst(item['type'])} - {item['price']} -  Leaving: {item['outDate']}\n[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
            else:
                MarkDown.write(f'\n### {item['name']} - {capFirst(item['type'])} - {item['price']} - {item['type']} -  Leaving: {item['outDate']}\n[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
        
        elif item['image'] != None and item['urlExstension'] == None:
            if checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **LEAVING NEXT ROTATION** {item['name']} - {capFirst(item['type'])} - {item['price']} - {item['type']} -  Leaving: {item['outDate']}\n![Image of {item['name']}](../images/{getDate()}/{item['imageLocal']})')
            elif checkSameDate(item['inDate']):
                MarkDown.write(f'\n### **NEW** {item['name']} - {item['price']} - {capFirst(item['type'])} -  Leaving: {item['outDate']}\n![Image of {item['name']}](../images/{getDate()}/{item['imageLocal']})')
            else:
                MarkDown.write(f'\n### {item['name']} - {capFirst(item['type'])} - {item['price']} - {item['type']} -  Leaving: {item['outDate']}\n![Image of {item['name']}](../images/{getDate()}/{item['imageLocal']})')
    MarkDown.close()
    print("Completed Compiling Markdown File")
    repo = git.Repo('C:/Users/ewklu/OneDrive/Desktop/Github_Repos/Fortnite-Item-Shop-Historical')
    repo.index.add([filename, updateReadMe(), 'images/' + f'{getDate()}'])
    print("File Added to Commit")
    
    print("Repo Commited")
    origin = repo.remote(name='origin') 
  
    existing_branch = repo.heads['main'] 
    existing_branch.checkout() 
    repo.index.commit(f"{getDate()} Item Shop")
    print('Commited successfully') 
    origin.push() 
    print("Completed Push to Orgin")
    print("Closing app")
    exit()

scraping()