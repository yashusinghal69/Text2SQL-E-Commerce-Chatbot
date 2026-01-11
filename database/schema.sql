-- Brazilian E-Commerce Dataset Schema

-- 1. Product Category Translation
CREATE TABLE IF NOT EXISTS product_category_name_translation (
    product_category_name TEXT PRIMARY KEY,
    product_category_name_english TEXT
);

-- 2. Sellers
CREATE TABLE IF NOT EXISTS sellers (
    seller_id UUID PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city TEXT,
    seller_state TEXT
);

-- 3. Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY,
    customer_unique_id UUID,
    customer_zip_code_prefix INTEGER,
    customer_city TEXT,
    customer_state TEXT
);

-- 4. Geolocation (Large table, no primary key usually provided in this dataset)
CREATE TABLE IF NOT EXISTS geolocation (
    geolocation_zip_code_prefix INTEGER,
    geolocation_lat DOUBLE PRECISION,
    geolocation_lng DOUBLE PRECISION,
    geolocation_city TEXT,
    geolocation_state TEXT
);

-- 5. Products
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY,
    product_category_name TEXT,
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

-- 6. Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(customer_id),
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

-- 7. Order Items
CREATE TABLE IF NOT EXISTS order_items (
    order_id UUID REFERENCES orders(order_id),
    order_item_id INTEGER,
    product_id UUID REFERENCES products(product_id),
    seller_id UUID REFERENCES sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price DOUBLE PRECISION,
    freight_value DOUBLE PRECISION,
    PRIMARY KEY (order_id, order_item_id)
);

-- 8. Order Payments
CREATE TABLE IF NOT EXISTS order_payments (
    order_id UUID REFERENCES orders(order_id),
    payment_sequential INTEGER,
    payment_type TEXT,
    payment_installments INTEGER,
    payment_value DOUBLE PRECISION,
    PRIMARY KEY (order_id, payment_sequential)
);

-- 9. Order Reviews
CREATE TABLE IF NOT EXISTS order_reviews (
    review_id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(order_id),
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);
