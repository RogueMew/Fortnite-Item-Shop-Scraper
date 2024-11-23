from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tqdm import tqdm

import json
import pandas

import datetime

class shop:
    options = webdriver.EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    def __init__(self) -> None:
        
        def checkKey(dictionary: dict, key: str) -> None:
            if not dictionary.get(key, None):
                raise KeyError("Proper Data Doesnt Exist")
            
        def parser(data: dict) -> list:
            
            data = json.loads(data)
            
            checkKey(data, "catalog")
            checkKey(data["catalog"], "categories")
            
            data = data["catalog"]["categories"]
            itemShop = []
            
            for category in data :
                for section in category["sections"]:
                    for offer in section["offerGroups"]:
                        for item in offer["items"]:
                            
                            inDate = item.get("inDate", "N/A")
                            outDate = item.get("outDate", "N/A")
                            
                            item_dict = {
                                "name" : item.get("title", None).replace("&amp;", "&"),
                                "category" : category["navLabel"].replace("&amp;", "&"),
                                "section" : section["displayName"].replace("&amp;", "&"),
                                "type" : item["assetType"].replace("dynamicbundle", "bundle").replace("jamtrack", "jam track").replace("rmtpack", "real money pack"),
                                "price" : (str(item["pricing"]["finalPrice"]) + " V-Bucks") if item["assetType"] != "rmtpack" else "$" + "".join([x for x in str(item["pricing"]["finalPrice"])[:len(str(item["pricing"]["finalPrice"]))-2]]) + "." + str(item["pricing"]["finalPrice"])[-2:],
                                "inDate" : inDate if inDate == None else inDate.split("T")[0] if "T" in inDate else inDate,
                                "outDate" : outDate if outDate == None else outDate.split("T")[0] if "T" in outDate else outDate,
                                "hasVariants" : item.get("hasVariants", None)
                            }

                            itemShop.append(item_dict)
                            del item_dict
            return itemShop
        
        driver = webdriver.Edge(self.options)
        driver.get("https://www.fortnite.com/item-shop?lang=en-US&_data=routes%2Fitem-shop._index")
        
        self.__RAWdata = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[hidden="true"]'))).get_attribute("innerHTML")
        self.__parsed = parser(self.__RAWdata)
             
    @property
    def RAW(self) -> dict:
        return self.__RAWdata
    
    @property
    def parsed(self) -> dict:
        return self.__parsed
        
    @property
    def new(self) -> dict:
        date = datetime.datetime.now()
        date = f"{date.year}-{date.month}-{str(date.day + 1) if int(date.strftime("%H")) >= 17 and int(date.strftime("%H")) <= 23 else str(date.day)}"
        
        df = pandas.DataFrame(self.__parsed)
        
        return df[df.inDate == date].to_json(orient="records", index=False)
    
    @property
    def sections(self) -> list:
        df = pandas.DataFrame(self.__parsed)
        return list(set(df["section"]))
    
    def section(self, section: str) -> dict:
        date = datetime.datetime.now()
        date = f"{date.year}-{date.month}-{str(date.day + 1) if int(date.strftime("%H")) >= 17 and int(date.strftime("%H")) <= 23 else str(date.day)}"
        
        df = pandas.DataFrame(self.__parsed)
        
        return df[df.section == section].to_json(orient="records", index = False)
    
    def type(self, type: str = "emote") -> dict:
        df = pandas.DataFrame(self.__parsed)
        return df[df.type == type].to_json(orient="records", index = False)
    
    @property
    def categories(self) -> list:
        df = pandas.DataFrame(self.__parsed)
        return list(set(df["category"]))

    @property
    def leaving(self) -> dict:
        date = datetime.datetime.now()
        date = f"{date.year}-{date.month}-{str(date.day + 1) if int(date.strftime("%H")) >= 17 and int(date.strftime("%H")) <= 23 else str(date.day)}"
        
        df = pandas.DataFrame(self.__parsed)
        
        return df[df.outDate == date].to_json(orient="records", index = False)
    
    def varaints(self, hasVaraints: bool = True) -> dict:
        df = pandas.DataFrame(self.__parsed)
        return df[df.hasVariants == hasVaraints].to_json(orient="records")