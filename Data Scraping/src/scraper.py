import time
import json
import os
import uuid
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_rumah123(total_pages=4):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    raw_properties = []
    raw_locations = []
    raw_agents = []
    raw_facilities = []
    
    visited_locations = set()
    visited_agents = set()

    for current_page in range(1, total_pages + 1):
        target_url = f"https://www.rumah123.com/jual/cari/?page={current_page}"
        driver.get(target_url)
        time.sleep(5)
        
        page_source = BeautifulSoup(driver.page_source, 'html.parser')
        property_cards = page_source.find_all('div', class_=lambda c: c and 'card' in c.lower())

        for card in property_cards:
            property_id = str(uuid.uuid4())[:8]
            
            price_node = card.find(string=re.compile(r'Rp', re.IGNORECASE))
            property_price = price_node.parent.text.strip() if price_node else "0"

            title_node = card.find(['h2', 'h3', 'h4'])
            if not title_node:
                title_node = card.find('a', href=re.compile(r'/properti/'))
            property_title = title_node.text.strip() if title_node else "Untitled"

            location_node = card.find(lambda t: t.name in ['span', 'p', 'div'] and t.get('class') and any('location' in c.lower() or 'address' in c.lower() for c in t.get('class', [])))
            property_location = location_node.text.strip() if location_node else "Unknown Location"

            if property_location == "Unknown Location":
                span_elements = card.find_all('span')
                if len(span_elements) >= 2:
                    property_location = span_elements[-1].text.strip()

            property_category = "Unknown"
            property_tags = []

            badge_node = card.find(attrs={"data-test-id": "srp-card-property-type-badge"})
            if badge_node:
                property_category = badge_node.text.strip()

            depth_badges = card.find_all(attrs={"data-test-id": "badge-depth"})
            for db in depth_badges:
                val = db.text.strip()
                if val and val not in property_tags and val != property_category:
                    property_tags.append(val)

            quick_labels = card.find_all('a', class_=lambda c: c and 'chipQuickLabelLink' in c)
            for ql in quick_labels:
                val = ql.text.strip()
                if val and val not in property_tags and val != property_category:
                    property_tags.append(val)

            fallback_badges = card.find_all(lambda t: t.name in ['div', 'span'] and t.get('class') and ('badge' in ' '.join(t.get('class')).lower() or 'tag' in ' '.join(t.get('class')).lower() or 'rounded-full' in ' '.join(t.get('class')).lower()))
            for badge in fallback_badges:
                text_val = badge.text.strip()
                text_lower = text_val.lower()
                if property_category == "Unknown" and text_lower in ['rumah', 'apartemen', 'ruko', 'gudang', 'tanah', 'pabrik', 'ruang usaha']:
                    property_category = text_val
                elif text_val and text_val != property_category and len(text_val) < 30 and text_val not in property_tags:
                    property_tags.append(text_val)

            raw_tags_string = ", ".join(property_tags)

            agent_node = card.find(attrs={"data-test-id": "srp-card-agent-name"})
            agent_name = agent_node.text.strip() if agent_node else "Independent Agent"

            agent_phone = "Not Available"
            phone_link = card.find('a', href=re.compile(r'wa\.me|whatsapp'))
            if phone_link:
                phone_match = re.search(r'phone=(\d+)', phone_link.get('href', ''))
                if phone_match:
                    agent_phone = phone_match.group(1)

            bedrooms = "0"
            bathrooms = "0"
            garages = "0"
            
            attr_list = card.find('div', class_=lambda c: c and 'propertyCardAttributesList' in c)
            if attr_list:
                spans = attr_list.find_all('span', class_=lambda c: c and 'flex' in c)
                for span in spans:
                    use_tag = span.find('use')
                    if use_tag:
                        href_val = use_tag.get('href', '') or use_tag.get('xlink:href', '')
                        val = span.text.strip()
                        if 'bedroom' in href_val.lower():
                            bedrooms = val
                        elif 'bathroom' in href_val.lower():
                            bathrooms = val
                        elif 'carport' in href_val.lower() or 'garage' in href_val.lower():
                            garages = val

            full_text = card.text.replace('\n', ' ')
            
            building_area_match = re.search(r'LB:\s*(\d+)', full_text)
            building_area = f"{building_area_match.group(1)} m2" if building_area_match else "0 m2"
            
            land_area_match = re.search(r'LT:\s*(\d+)', full_text)
            land_area = f"{land_area_match.group(1)} m2" if land_area_match else "0 m2"
            
            facility_match = re.search(r'(\d+)\s*Fasilitas', full_text, re.IGNORECASE)
            total_facilities = facility_match.group(1) if facility_match else "0"
            
            tenor_15_match = re.search(r'(Rp\s*[\d,.]+\s*(?:Jutaan|Juta|Ribu)?\s*\(Tenor 15 Tahun\))', full_text, re.IGNORECASE)
            tenor_15 = tenor_15_match.group(1) if tenor_15_match else "0"
            
            tenor_20_match = re.search(r'(Rp\s*[\d,.]+\s*(?:Jutaan|Juta|Ribu)?\s*\(Tenor 20 Tahun\))', full_text, re.IGNORECASE)
            tenor_20 = tenor_20_match.group(1) if tenor_20_match else "0"

            if property_price != "0" and "Rp" in property_price:
                raw_properties.append({
                    "property_id": property_id,
                    "title": property_title,
                    "category": property_category,
                    "raw_price": property_price,
                    "raw_installment_15y": tenor_15,
                    "raw_installment_20y": tenor_20,
                    "raw_location": property_location,
                    "raw_bedrooms": bedrooms,
                    "raw_bathrooms": bathrooms,
                    "raw_garages": garages,
                    "raw_building_area": building_area,
                    "raw_land_area": land_area,
                    "total_facilities": total_facilities,
                    "raw_tags": raw_tags_string,
                    "agent_name": agent_name
                })

                if property_location not in visited_locations:
                    raw_locations.append({"raw_location": property_location})
                    visited_locations.add(property_location)
                    
                if agent_name not in visited_agents:
                    raw_agents.append({
                        "agent_name": agent_name,
                        "raw_phone_number": agent_phone
                    })
                    visited_agents.add(agent_name)

    driver.quit()
    return raw_properties, raw_locations, raw_agents, raw_facilities

def export_to_json(data_list, file_name):
    target_directory = '../data'
    os.makedirs(target_directory, exist_ok=True)
    target_path = os.path.join(target_directory, file_name)
    with open(target_path, 'w', encoding='utf-8') as file_object:
        json.dump(data_list, file_object, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    properties, locations, agents, facilities = scrape_rumah123(total_pages=4) 
    
    export_to_json(properties, 'raw_properties.json')
    export_to_json(locations, 'raw_locations.json')
    export_to_json(agents, 'raw_agents.json')
    export_to_json(facilities, 'raw_facilities.json')