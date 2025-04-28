CREATE TABLE users IF NOT EXISTS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE files IF NOT EXISTS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL
);

CREATE TABLE access IF NOT EXISTS (
    user_id INTEGER,
    file_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    PRIMARY KEY (user_id, file_id)
);