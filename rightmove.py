# Import necessary modules
import requests
from bs4 import BeautifulSoup
import json
import datetime
import csv


headers={
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'
	}

class RightMoveScrapper:
    def __init__(self, url):
        # result file creation 
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        self.filename = "%s.csv" % now
        self.file_details = open("%s" % self.filename,"w",encoding='UTF-8')
        self.writer_details = csv.writer(self.file_details, delimiter=",",lineterminator="\n")
        # headers row writing
        self.writer_details.writerow([
            "Property ID",
            "Title",
            "Published Date",
            "Bed",
            "Bath",
            "Price",
            "Address",
            "Distances",
            "Latitude",
            "Longitude",
            "Contact",
            "Display Name",
            "Property Link"
            ])
        self.url = url
        self.visit_listing_page(self.url)

    # visit all paginations
    def visit_listing_page(self, url):
        print("---> %s" % url)
        site = requests.get(url, headers=headers).text
        soup = BeautifulSoup(site, "html.parser")
        json_script = self.get_json_script(soup)
        json_data = self.from_string_to_json(json_script)
        self.parse_properties(json_data)
        pagination = json_data["pagination"]
        total_pagination = pagination["total"]
        page = pagination["page"]
        if int(page) < int(total_pagination):
            print(page)
            print(total_pagination)
            if "&index=" not in url:
                new_url = url + "&index=24"
                self.visit_listing_page(new_url)
            else:
                url_splitted = url.split("&index=")
                index_number = int(page)*24
                new_url = url_splitted[0] + "&index=" + str(index_number) + url_splitted[1].partition("&")[2]
                self.visit_listing_page(new_url)
    
    # get json data
    def get_json_script(self, soup):
        script_tags = soup.find_all("script")
        json_script = ""
        for tag in script_tags:
            if "window.jsonModel = " in tag.text:
                json_script = tag.text
        
        return json_script

    # parse properties data from json data
    def parse_properties(self, json_data):
        properties = json_data["properties"]
        for property in properties:
            property_id = property["id"]
            property_title = property["propertyTypeFullDescription"]
            published_date = property["firstVisibleDate"]
            bedrooms = property["bedrooms"]
            bathrooms = property["bathrooms"]
            if bathrooms == None:
                bathrooms = "0"
            displayAddress = property["displayAddress"]
            countryCode = property.get("countryCode")
            if countryCode:
                displayAddress += " %s" % countryCode
            
            latitude = ""
            longitude = ""
            location = property.get("location")
            if location:
                latitude = location["latitude"]
                longitude = location["longitude"]
            
            price = property["price"]
            amount = price["amount"]

            customer = property["customer"]
            contactTelephone = customer["contactTelephone"]
            branchDisplayName = customer["branchDisplayName"]
            property_link = "https://www.rightmove.co.uk/properties/" + str(property_id)

            distances = self.get_distances_from_url(property_link)
            self.writer_details.writerow([
                property_id,
                property_title,
                published_date,
                bedrooms,
                bathrooms,
                amount,
                displayAddress,
                str(distances),
                latitude,
                longitude,
                contactTelephone,
                branchDisplayName,
                property_link,
                ])
            self.file_details.flush()
            print([
                property_id,
                property_title,
                published_date,
                bedrooms,
                bathrooms,
                amount,
                displayAddress,
                str(distances),
                contactTelephone,
                branchDisplayName,
                property_link,
                ])
    
    # get distances from a property url
    def get_distances_from_url(self, url):
        site = requests.get(url, headers=headers).text
        soup = BeautifulSoup(site, "html.parser")
        stations_div = soup.find("div", {"id": "Stations-panel"})
        distance_dict = {}

        if stations_div:
            stations_lis = stations_div.find_all("li")
        
            for stations_li in stations_lis:
                spans = stations_li.find_all("span")
                if spans != []:
                    span_station_name = spans[0].text
                    span_distance = spans[1].text
                    distance_dict[span_station_name] = span_distance
        return distance_dict            

    # converting string to json
    def from_string_to_json(self, json_script):
        json_script = json_script.replace("window.jsonModel = ", "")
        json_data = json.loads(json.loads(json.dumps(json_script)))
        return json_data


# this is for test
if __name__ == "__main__":
    RightMoveScrapper("https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E87490&insId=1&radius=0.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false")