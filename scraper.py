from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
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

def imageDownload(url, name, date):
    if os.path.isdir(f'./images/{date}') == False:
        os.mkdir(f'./images/{date}')
    with open('images/' + f'{date}/' + name.replace(' ', '-').replace('|', '-').lower() + '.png', "wb") as f:
        f.write(web.get(url).content)

def updateReadMe(date) -> str:
    readme = open("README.md", "w", encoding="utf-8")
    readme.write(f"# Fortnite Item Shop Historical Viewer | {date}\n")
    readme.write(f"## [Toadys Shop as Markdown](https://github.com/RogueMew/Fortnite-Item-Shop-Historical/blob/main/Markdown/{getDate()}-ItemShop.md)\n## [Todays Item Shop Images](https://github.com/RogueMew/Fortnite-Item-Shop-Historical/tree/main/images/{getDate()})")
    readme.close()
    return "README.md"

def updateGitIgnore(fileName):
    file = open('.gitignore', 'a+')
    file.seek(0)
    if fileName not in file.read():
        file.write('\n' + fileName)

def scraper()-> list:
    driver = webdriver.Edge()
    driver.get("https://www.fortnite.com/item-shop?lang=en-US&_data=routes%2Fitem-shop._index")
    content = json.loads(driver.find_element(By.CSS_SELECTOR, 'div[hidden="true"]').get_attribute('textContent'))
    driver.close()
    print("Scraped Site")
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
                        "name" : item.get('title', None),
                        'catagory' : catagory['navLabel'],
                        'section' : section['displayName'],
                        'type' : item['assetType'], 
                        'price' : str(item['pricing']['finalPrice']) + " vbucks",
                        'inDate' : inDate.split("T")[0],
                        'outDate' : outDate.split("T")[0],
                        'image' : item['image'].get('lg', None),
                        'urlExstension' : item.get('urlName', None),
                        'rmtImage' : item['image'].get('wide', None),
                        'imageLocal' : item['title'].replace(' ', '-').replace('|', '-').lower() + '.png',
                        'hasVariants' : item.get('hasVariants', None)
                    }
                    if item_dict['type'] == 'dynamicbundle': item_dict['type'] = 'bundle'
                    elif item_dict['type'] == 'staticbundle': item_dict['type'] = 'bundle'
                    elif item_dict['type'] == 'vmtpack': item_dict['type'] = 'pack'
                    elif item_dict['type'] == 'jamtrack': item_dict['type'] = 'jam-track'
                    elif item_dict['type'] == 'legokit': item_dict['type'] = 'lego-kit'
                    elif item_dict['type'] == 'decor': item_dict['type'] = 'decor-bundle'
                    itemshop.append(item_dict)
    return itemshop

def commit(files) ->None:
    repo = git.Repo('C:\Users\ewklu\Desktop\github_repos\Fortnite-Item-Shop-Historical')
    repo.index.add(files)
    origin = repo.remote(name='origin') 
    existing_branch = repo.heads['main'] 
    existing_branch.checkout() 
    repo.index.commit(f"{getDate()} Item Shop")
    print('Commited successfully, Pushing to Orgin') 
    origin.push()
    print("Completed Push to Orgin")
    print("Closing app")

def write_markdown(file, type,prefix, item, date, include_image=True, include_url=True):
    image_md = f"![Image of {item['name']}](../images/{date}/{item['imageLocal']})" if include_image else ''
    url_md = f"[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type']}s/{item['urlExstension']}?lang=en-US)" if include_url else ''
    file.write(f'\n### {prefix} {item["name"]} - {capFirst(type)}- {item["price"]} - Leaving: {item["outDate"]}\n{image_md}{url_md}')

def handle_item(file, item, type, date):
    prefix = "**NEW**" if checkSameDate(item['inDate']) else "**LEAVING NEXT ROTATION**" if checkSameDate(item['outDate']) else "**NEW** **LEAVING NEXT ROTATION**" if checkSameDate(item['outdate']) and checkSameDate(item['inDate']) else ""
    
    if item['image'] and item['urlExstension']:
        write_markdown(file, type,prefix, item, date)
    elif item['urlExstension']:
        write_markdown(file, type, prefix, item, date, include_image=False)
    elif item['image']:
        write_markdown(file, type, prefix, item, date, include_url=False)

def main()->None:
    itemshop = scraper()
    date = getDate()
    filename = f"Markdown/{date}-ItemShop.md"
    MarkDown = open(filename, "w", encoding="utf-8") 
    catagory = ""
    section = ""
    tempNumber = 1
    print('Compiling to Markdown and Downloading Images')
    MarkDown.write(f'# Item Shop for {date}')
    for item in tqdm(itemshop, total=len(itemshop)):
        if item['name'] == None or item['name'] == '':
            item['name'] = 'temp{}'.format(tempNumber)
            item['imageLocal'] = 'temp{}'.format(tempNumber) + '.png'
            tempNumber = tempNumber + 1
        
        if catagory != item["catagory"]:
            catagory = item["catagory"]
            MarkDown.write(f"\n# {item["catagory"]}")
        
        if section != item["section"]:
            section = item["section"]
            MarkDown.write(f"\n## {item["section"]}")
        
                
        if item['image'] != None:
            imageDownload(item['image'], item['name'], date)

        if item['rmtImage'] != None:
            imageDownload(item['rmtImage'], item['name'], date)
        
        if 'temp' in item['name'] :
            item['name'] = 'Not Listed on Site'
        
        if item['type'] == 'rmtpack':
            MarkDown.write(f'\n### {item['name']} - Costs Real Money\n[![Image of {item['name']}](../images/{date}/{item['imageLocal']})]({item['urlExstension']})')

        elif item['image'] != None and item['urlExstension'] != None:
            if checkSameDate(item['outDate']) and checkSameDate(item['inDate']):
                MarkDown.write(f'\n### **NEW** **LEAVING NEXT ROTATION** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n[![Image of {item['name']}](../images/{date}/{item['imageLocal']})](https://www.fortnite.com/item-shop/{item['type'] +'s'}/{item['urlExstension']}?lang=en-US)')
            elif checkSameDate(item['inDate']):
                MarkDown.write(f'\n### **NEW** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n[![Image of {item['name']}](../images/{date}/{item['imageLocal']})](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
            elif checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **LEAVING NEXT ROTATION** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n[![Image of {item['name']}](../images/{date}/{item['imageLocal']})](https://www.fortnite.com/item-shop/{item['type'] +'s'}/{item['urlExstension']}?lang=en-US)')
            else:
                MarkDown.write(f'\n### {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n[![Image of {item['name']}](../images/{date}/{item['imageLocal']})](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
        
        elif item['image'] == None and item['urlExstension'] != None:
            if checkSameDate(item['outDate']) and checkSameDate(item['inDate']):
                MarkDown.write(f'\n### **NEW** **LEAVING NEXT ROTATION** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
            elif checkSameDate(item['inDate']):
                MarkDown.write(f'\n### **NEW** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
            elif checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **LEAVING NEXT ROTATION** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
            else:
                MarkDown.write(f'\n### {item['name']} - {item['price']} - {item['type']} -  Leaving: {item['outDate']}\n[Link to {item['name']} in the webshop](https://www.fortnite.com/item-shop/{item['type'] + 's'}/{item['urlExstension']}?lang=en-US)')
        
        elif item['image'] != None and item['urlExstension'] == None:
            if checkSameDate(item['outDate']) and checkSameDate(item['inDate']):
                MarkDown.write(f'\n### **NEW** **LEAVING NEXT ROTATION** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n![Image of {item['name']}](../images/{date}/{item['imageLocal']})')
            elif checkSameDate(item['inDate']):
                MarkDown.write(f'\n### **NEW** {item['name']} - {item['price']} - {item['type']} -  Leaving: {item['outDate']}\n![Image of {item['name']}](../images/{date}/{item['imageLocal']})')
            elif checkSameDate(item['outDate']):
                MarkDown.write(f'\n### **LEAVING NEXT ROTATION** {item['name']} - {item['price']} -  Leaving: {item['outDate']}\n![Image of {item['name']}](../images/{date}/{item['imageLocal']})')
            else:
                MarkDown.write(f'\n### {item['name']} - {item['price']} - {item['type']} -  Leaving: {item['outDate']}\n![Image of {item['name']}](../images/{date}/{item['imageLocal']})')
    MarkDown.close()
    
    print("Completed Compiling Markdown File, Adding to Repo")
    filesCommit = [filename, updateReadMe(date), f'images/{date}/']
    commit(filesCommit)
    exit()

main()
