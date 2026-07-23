import json
import psycopg2
import os

DB_CONFIG = {
    "dbname": "rumah123_db",
    "user": "postgres",
    "password": "12345678",
    "host": "localhost",
    "port": "5432"
}

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"File tidak ditemukan: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def nullify_zero(val):
    if val == 0 or val == "0":
        return None
    return val

def insert_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Memasukkan data ke tabel locations...")
        locations = load_json('../../Data Scraping/data/clean_locations.json')
        for loc in locations:
            cursor.execute("""
                INSERT INTO locations (location_name, city, district)
                VALUES (%s, %s, %s)
                ON CONFLICT (location_name) DO NOTHING;
            """, (loc.get('location_name'), loc.get('city'), loc.get('district')))
        conn.commit()

        print("Memasukkan data ke tabel agents...")
        agents = load_json('../../Data Scraping/data/clean_agents.json')
        for agent in agents:
            cursor.execute("""
                INSERT INTO agents (agent_name, phone_prefix)
                VALUES (%s, %s)
                ON CONFLICT (agent_name) DO NOTHING;
            """, (agent.get('agent_name'), agent.get('phone_prefix')))
        conn.commit()

        print("Memasukkan data ke tabel categories...")
        categories = load_json('../../Data Scraping/data/clean_categories.json')
        for cat in categories:
            cursor.execute("""
                INSERT INTO categories (category_name)
                VALUES (%s)
                ON CONFLICT (category_name) DO NOTHING;
            """, (cat.get('category_name'),))
        conn.commit()

        print("Memasukkan data ke tabel tags...")
        tags = load_json('../../Data Scraping/data/clean_tags.json')
        for tag in tags:
            cursor.execute("""
                INSERT INTO tags (tag_name)
                VALUES (%s)
                ON CONFLICT (tag_name) DO NOTHING;
            """, (tag.get('tag_name'),))
        conn.commit()

        print("Memetakan Foreign Keys...")
        cursor.execute("SELECT location_name, location_id FROM locations")
        location_map = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT agent_name, agent_id FROM agents")
        agent_map = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT category_name, category_id FROM categories")
        category_map = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT tag_name, tag_id FROM tags")
        tag_map = {row[0]: row[1] for row in cursor.fetchall()}

        print("Memasukkan data ke tabel properties...")
        properties = load_json('../../Data Scraping/data/clean_properties.json')
        for prop in properties:
            loc_id = location_map.get(prop.get('location_name'))
            agent_id = agent_map.get(prop.get('agent_name'))
            cat_id = category_map.get(prop.get('category_name'))

            beds = nullify_zero(prop.get('bedrooms'))
            baths = nullify_zero(prop.get('bathrooms'))
            garages = nullify_zero(prop.get('garages'))
            b_area = nullify_zero(prop.get('building_area'))
            l_area = nullify_zero(prop.get('land_area'))
            fac_count = nullify_zero(prop.get('facilities_count'))

            cursor.execute("""
                INSERT INTO properties (
                    property_id, title, price, installment_15y, installment_20y,
                    bedrooms, bathrooms, garages, building_area, land_area, facilities_count,
                    category_id, location_id, agent_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (property_id) DO NOTHING;
            """, (
                prop.get('property_id'), prop.get('title'), prop.get('price'), 
                prop.get('installment_15y'), prop.get('installment_20y'),
                beds, baths, garages, b_area, l_area, fac_count,
                cat_id, loc_id, agent_id
            ))
        conn.commit()

        print("Memasukkan data ke tabel property_tags...")
        property_tags = load_json('../../Data Scraping/data/clean_property_tags.json')
        for pt in property_tags:
            tag_id = tag_map.get(pt.get('tag_name'))
            if tag_id:
                cursor.execute("""
                    INSERT INTO property_tags (property_id, tag_id)
                    VALUES (%s, %s)
                    ON CONFLICT (property_id, tag_id) DO NOTHING;
                """, (pt.get('property_id'), tag_id))
        conn.commit()

        print("Data berhasil dimasukkan ke PostgreSQL!")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    insert_data()