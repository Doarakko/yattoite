CREATE TABLE freee_users (
    id SERIAL NOT NULL,
    employee_id integer,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id)
);

CREATE TABLE messages (
    id SERIAL NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id)
);

CREATE TABLE freee_access_tokens (
    id SERIAL NOT NULL,
    token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expired_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id)
);