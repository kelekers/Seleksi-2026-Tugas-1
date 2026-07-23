-- =========================================================================
-- OPTIMASI 1: INDEXING
-- =========================================================================
-- Masalah: 
-- Mencari properti berdasarkan 'category_id' biasanya pakai Seq Scan yang lambat.
--
-- Solusi: 
-- Membuat index memungkinkan database melakukan Index-Only Scan yang jauh lebih cepat.

-- [BEFORE]
EXPLAIN ANALYZE
SELECT title, price 
FROM properties 
WHERE category_id = 2;

-- [OPTMIZATION]
CREATE INDEX IF NOT EXISTS idx_properties_cat_cover 
ON properties(category_id) INCLUDE (title, price);

-- [AFTER]
EXPLAIN ANALYZE
SELECT title, price 
FROM properties 
WHERE category_id = 2;


-- =========================================================================
-- OPTIMASI 2: MATERIALIZED VIEW
-- =========================================================================
-- Masalah: 
-- Query yang menghitung total listing dan rata-rata harga per kota dan kategori
--
-- Solusi: 
-- Membuat materialized view untuk menyimpan hasil query yang kompleks untuk akses cepat.

-- [BEFORE]
EXPLAIN ANALYZE
SELECT 
    l.city, 
    c.category_name, 
    COUNT(p.property_id) AS total_listing,
    ROUND(AVG(p.price), 2) AS avg_price
FROM properties p
JOIN locations l ON p.location_id = l.location_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY l.city, c.category_name;

-- [OPTIMIZATION]
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_city_category_stats AS
SELECT 
    l.city, 
    c.category_name, 
    COUNT(p.property_id) AS total_listing,
    ROUND(AVG(p.price), 2) AS avg_price
FROM properties p
JOIN locations l ON p.location_id = l.location_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY l.city, c.category_name;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_city_cat ON mv_city_category_stats(city, category_name);

-- [AFTER]
EXPLAIN ANALYZE
SELECT * 
FROM mv_city_category_stats 
WHERE city = 'Jakarta Selatan';


-- =========================================================================
-- OPTIMASI 3: QUERY REWRITING (MENGGANTI COUNT(*) DENGAN EXISTS)
-- =========================================================================
-- Masalah: 
-- Query yang menggunakan COUNT(*) untuk memeriksa apakah ada properti di lokasi tertentu
--
-- Solusi: 
-- Mengganti COUNT(*) dengan EXISTS untuk meningkatkan performa, karena EXISTS berhenti mencari setelah menemukan satu baris yang cocok.

-- [BEFORE]
EXPLAIN ANALYZE
SELECT location_name, city
FROM locations l
WHERE (
    SELECT COUNT(*) 
    FROM properties p 
    WHERE p.location_id = l.location_id
) > 0;


-- [AFTER]
EXPLAIN ANALYZE
SELECT location_name, city
FROM locations l
WHERE EXISTS (
    SELECT 1 
    FROM properties p 
    WHERE p.location_id = l.location_id
);