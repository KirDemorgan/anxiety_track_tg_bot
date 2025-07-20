-- Создание таблиц
CREATE TABLE IF NOT EXISTS pills (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    pill_name VARCHAR(255) NOT NULL,
    dose VARCHAR(100) NOT NULL,
    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_notes (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_pills_user_id ON pills(user_id);
CREATE INDEX IF NOT EXISTS idx_pills_taken_at ON pills(taken_at);
CREATE INDEX IF NOT EXISTS idx_health_notes_user_id ON health_notes(user_id);
CREATE INDEX IF NOT EXISTS idx_health_notes_created_at ON health_notes(created_at);