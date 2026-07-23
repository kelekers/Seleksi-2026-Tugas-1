-- 1. Tabel Dimensi: Lokasi
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(100),
    district VARCHAR(100)
);

-- 2. Tabel Dimensi: Agen
CREATE TABLE agents (
    agent_id SERIAL PRIMARY KEY,
    agent_name VARCHAR(255) UNIQUE NOT NULL,
    phone_prefix VARCHAR(50)
);

-- 3. Tabel Dimensi: Kategori Properti
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

-- 4. Tabel Fakta: Properti
CREATE TABLE properties (
    property_id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    price BIGINT CHECK (price >= 0),
    installment_15y BIGINT DEFAULT 0,
    installment_20y BIGINT DEFAULT 0,
    bedrooms INT DEFAULT 0,
    bathrooms INT DEFAULT 0,
    garages INT DEFAULT 0,
    building_area INT DEFAULT 0,
    land_area INT DEFAULT 0,
    facilities_count INT DEFAULT 0,
    category_id INT REFERENCES categories(category_id) ON DELETE RESTRICT,
    location_id INT REFERENCES locations(location_id) ON DELETE SET NULL,
    agent_id INT REFERENCES agents(agent_id) ON DELETE SET NULL,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tabel Dimensi: Tags
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) UNIQUE NOT NULL
);

-- 6. Tabel Bridge: Properti Tags
CREATE TABLE property_tags (
    property_id VARCHAR(50) REFERENCES properties(property_id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (property_id, tag_id)
);