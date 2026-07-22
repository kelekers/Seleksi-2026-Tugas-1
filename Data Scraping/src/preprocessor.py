import pandas as pd
import json
import os
import re

def parse_price(price_str):
    if not isinstance(price_str, str) or price_str == "0":
        return 0
    
    clean_str = price_str.lower()
    multiplier = 1
    
    if 'miliar' in clean_str:
        multiplier = 1_000_000_000
    elif 'juta' in clean_str:
        multiplier = 1_000_000
    elif 'ribu' in clean_str:
        multiplier = 1_000
        
    match = re.search(r'(\d+[.,\d]*)', clean_str)
    if match:
        num_str = match.group(1)
        num_str = num_str.replace(',', '.')
        try:
            return int(float(num_str) * multiplier)
        except:
            return 0
    return 0

def parse_area(area_str):
    if not isinstance(area_str, str):
        return 0
    match = re.search(r'(\d+)', area_str)
    return int(match.group(1)) if match else 0

def parse_rooms(room_str):
    if not isinstance(room_str, str) or room_str == "0":
        return 0
    try:
        parts = room_str.split('+')
        return sum(int(p.strip()) for p in parts if p.strip().isdigit())
    except:
        return 0

def process_data():
    with open('../data/raw_properties.json', 'r', encoding='utf-8') as f:
        props = json.load(f)
    
    df_props = pd.DataFrame(props)
    df_props = df_props.drop_duplicates(subset=['title', 'raw_price', 'raw_location'], keep='first')
    
    df_props['price'] = df_props['raw_price'].apply(parse_price)
    df_props['installment_15y'] = df_props['raw_installment_15y'].apply(parse_price)
    df_props['installment_20y'] = df_props['raw_installment_20y'].apply(parse_price)
    
    df_props['building_area'] = df_props['raw_building_area'].apply(parse_area)
    df_props['land_area'] = df_props['raw_land_area'].apply(parse_area)
    
    df_props['bedrooms'] = df_props['raw_bedrooms'].apply(parse_rooms)
    df_props['bathrooms'] = df_props['raw_bathrooms'].apply(parse_rooms)
    df_props['garages'] = df_props['raw_garages'].apply(parse_rooms)
    df_props['facilities_count'] = df_props['total_facilities'].apply(parse_area)
    
    tags_data = []
    property_tags_mapping = []
    unique_tags = set()
    
    for idx, row in df_props.iterrows():
        prop_id = row['property_id']
        raw_tags = str(row['raw_tags']).split(',')
        for tag in raw_tags:
            clean_tag = tag.strip()
            if clean_tag and clean_tag.lower() != 'rp' and len(clean_tag) > 2:
                unique_tags.add(clean_tag)
                property_tags_mapping.append({
                    "property_id": prop_id,
                    "tag_name": clean_tag
                })
                
    for tag in unique_tags:
        tags_data.append({"tag_name": tag})
        
    df_props_clean = df_props[['property_id', 'title', 'category', 'price', 'installment_15y', 'installment_20y', 
                               'raw_location', 'bedrooms', 'bathrooms', 'garages', 'building_area', 'land_area', 
                               'facilities_count', 'agent_name']]
    df_props_clean = df_props_clean.rename(columns={'raw_location': 'location_name'})
    
    with open('../data/raw_locations.json', 'r', encoding='utf-8') as f:
        locs = json.load(f)
    df_locs = pd.DataFrame(locs)
    df_locs['city'] = df_locs['raw_location'].apply(lambda x: x.split(',')[-1].strip() if ',' in x else x)
    df_locs['district'] = df_locs['raw_location'].apply(lambda x: x.split(',')[0].strip() if ',' in x else 'Unknown')
    df_locs_clean = df_locs[['raw_location', 'city', 'district']].rename(columns={'raw_location': 'location_name'})
    df_locs_clean = df_locs_clean.drop_duplicates(subset=['location_name'])
    
    with open('../data/raw_agents.json', 'r', encoding='utf-8') as f:
        agents = json.load(f)
    df_agents = pd.DataFrame(agents)
    df_agents_clean = df_agents.rename(columns={'raw_phone_number': 'phone_number'})
    df_agents_clean = df_agents_clean.drop_duplicates(subset=['agent_name'])

    df_props_clean.to_json('../data/clean_properties.json', orient='records', indent=4, force_ascii=False)
    df_locs_clean.to_json('../data/clean_locations.json', orient='records', indent=4, force_ascii=False)
    df_agents_clean.to_json('../data/clean_agents.json', orient='records', indent=4, force_ascii=False)
    
    with open('../data/clean_tags.json', 'w', encoding='utf-8') as f:
        json.dump(tags_data, f, ensure_ascii=False, indent=4)
        
    with open('../data/clean_property_tags.json', 'w', encoding='utf-8') as f:
        json.dump(property_tags_mapping, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    process_data()