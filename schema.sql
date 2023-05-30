CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    password TEXT,
    is_admin BOOLEAN
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    comment TEXT,
    target_id INTEGER REFERENCES shops,
    likes INTEGER,
    date TEXT
);
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    target_id INTEGER REFERENCES comments,
    user_id INTEGER REFERENCES users
);
CREATE TABLE shops (
    id SERIAL PRIMARY KEY,
    name TEXT,
    cord_x INTEGER,
    cord_y INTEGER,
    has_pic BOOLEAN,
    picture BYTEA
);
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price FLOAT,
    shop_id INTEGER
);
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    rating INTEGER,
    target_id INTEGER REFERENCES shops
);