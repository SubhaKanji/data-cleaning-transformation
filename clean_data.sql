-- ============================================================
-- Data Cleaning & Transformation (SQL approach)
-- Equivalent logic to scripts/clean_data.py, done in-database.
-- Target: PostgreSQL syntax (adjust functions for MySQL/SQL Server as needed)
-- ============================================================

-- 1. Load raw data
CREATE TABLE raw_customer_orders (
    record_id     INT,
    customer_name TEXT,
    email         TEXT,
    region        TEXT,
    signup_date   TEXT,   -- kept as text; formats are inconsistent
    status        TEXT,
    quantity      TEXT,
    unit_price    TEXT
);
-- \copy raw_customer_orders FROM 'data/raw_customer_orders.csv' WITH CSV HEADER;

-- 2. Standardize and clean into a new table
CREATE TABLE cleaned_customer_orders AS
WITH base AS (
    SELECT
        record_id,
        INITCAP(TRIM(REGEXP_REPLACE(customer_name, '\s+', ' ', 'g'))) AS customer_name,
        NULLIF(LOWER(TRIM(email)), '')                                 AS email,
        NULLIF(INITCAP(TRIM(region)), '')                               AS region,
        NULLIF(INITCAP(TRIM(status)), '')                               AS status,
        -- try common date formats; NULL if none match
        COALESCE(
            TO_DATE(NULLIF(TRIM(signup_date), ''), 'YYYY-MM-DD'),
            TO_DATE(NULLIF(TRIM(signup_date), ''), 'MM/DD/YYYY'),
            TO_DATE(NULLIF(TRIM(signup_date), ''), 'DD-MM-YYYY'),
            TO_DATE(NULLIF(TRIM(signup_date), ''), 'YYYY/MM/DD')
        ) AS signup_date,
        NULLIF(quantity, '')::NUMERIC   AS quantity_raw,
        NULLIF(unit_price, '')::NUMERIC AS unit_price_raw
    FROM raw_customer_orders
),
medians AS (
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY quantity_raw) FILTER (WHERE quantity_raw > 0) AS median_qty,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY unit_price_raw) AS median_price
    FROM base
)
SELECT
    record_id,
    customer_name,
    COALESCE(email, 'unknown@missing.com')   AS email,
    COALESCE(region, 'Unknown')              AS region,
    COALESCE(status, 'Unknown')              AS status,
    signup_date,
    COALESCE(
        CASE WHEN quantity_raw > 0 THEN quantity_raw END,
        (SELECT median_qty FROM medians)
    )::INT AS quantity,
    ROUND(
        COALESCE(unit_price_raw, (SELECT median_price FROM medians)),
        2
    ) AS unit_price
FROM base;

-- 3. Remove exact duplicates (ignoring the surrogate record_id)
DELETE FROM cleaned_customer_orders a
USING cleaned_customer_orders b
WHERE a.record_id > b.record_id
  AND a.customer_name = b.customer_name
  AND a.email = b.email
  AND a.region = b.region
  AND a.status = b.status
  AND a.signup_date = b.signup_date
  AND a.quantity = b.quantity
  AND a.unit_price = b.unit_price;

-- 4. Add derived revenue column
ALTER TABLE cleaned_customer_orders ADD COLUMN revenue NUMERIC;
UPDATE cleaned_customer_orders SET revenue = ROUND(quantity * unit_price, 2);

-- 5. Sanity checks
SELECT COUNT(*) AS total_rows FROM cleaned_customer_orders;
SELECT region, COUNT(*) FROM cleaned_customer_orders GROUP BY region;
SELECT status, COUNT(*) FROM cleaned_customer_orders GROUP BY status;
