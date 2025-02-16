CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,            -- ID пользователя Telegram
    created_at TIMESTAMP DEFAULT NOW()     -- Дата создания профиля
);

CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,         -- ID сервиса (например, Lamoda, Magnum)
    service_name VARCHAR(50) UNIQUE,       -- Название сервиса
    created_at TIMESTAMP DEFAULT NOW()     -- Дата добавления сервиса
);

CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,    -- Уникальный ID подписки
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
    discount_threshold INT CHECK (discount_threshold >= 0 AND discount_threshold <= 100), -- Порог скидки
    notification_time TIME NOT NULL,       -- Время отправки уведомлений
    last_notified TIMESTAMP,               -- Время последнего уведомления
    created_at TIMESTAMP DEFAULT NOW(),    -- Дата подписки
    UNIQUE(user_id, service_id)            -- Уникальность подписки по пользователю и сервису
);

CREATE TABLE parsed_discounts (
    discount_id SERIAL PRIMARY KEY,        -- ID скидки
    service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
    product_name VARCHAR(255),             -- Название товара
    price_new VARCHAR(50),                 -- Новая цена
    price_old VARCHAR(50),                 -- Старая цена
    discount_percent INT,                  -- Процент скидки
    parsed_at TIMESTAMP DEFAULT NOW(),     -- Дата парсинга
    UNIQUE(service_id, product_name)       -- Уникальность скидки по названию
);

CREATE TABLE sent_discounts (
    sent_id SERIAL PRIMARY KEY,            -- ID отправленной скидки
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
    discount_id INT REFERENCES parsed_discounts(discount_id) ON DELETE CASCADE,
    sent_at TIMESTAMP DEFAULT NOW(),       -- Время отправки скидки
    UNIQUE(user_id, service_id, discount_id) -- Уникальность отправки
);
