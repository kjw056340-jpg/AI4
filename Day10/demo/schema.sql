-- note-demo / PostgreSQL target schema. The current app uses localStorage.
-- password_mock is for a demo only; replace it with password_hash before production.
BEGIN;

CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    nickname VARCHAR(20) NOT NULL CHECK (char_length(trim(nickname)) BETWEEN 2 AND 20),
    password_mock VARCHAR(100) NOT NULL CHECK (char_length(password_mock) BETWEEN 6 AND 100),
    role VARCHAR(10) NOT NULL DEFAULT 'MEMBER' CHECK (role IN ('MEMBER', 'ADMIN')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (email = lower(trim(email)))
);

CREATE TABLE posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    author_id BIGINT NOT NULL REFERENCES users(id),
    title VARCHAR(100) NOT NULL CHECK (char_length(trim(title)) > 0),
    content TEXT NOT NULL CHECK (char_length(trim(content)) > 0 AND char_length(content) <= 10000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);

CREATE TABLE comments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id BIGINT NOT NULL REFERENCES users(id),
    content VARCHAR(1000) NOT NULL CHECK (char_length(trim(content)) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blocked_keywords (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    keyword VARCHAR(30) NOT NULL CHECK (char_length(trim(keyword)) > 0),
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX blocked_keywords_unique_lower ON blocked_keywords (lower(keyword));
CREATE INDEX posts_latest ON posts (created_at DESC, id DESC);
CREATE INDEX posts_author_latest ON posts (author_id, created_at DESC, id DESC);
CREATE INDEX comments_post_created ON comments (post_id, created_at, id);

COMMIT;

-- List page (supply the zero-based :offset parameter; mask titles before returning):
-- SELECT id, title, author_id, created_at FROM posts
-- ORDER BY created_at DESC, id DESC LIMIT 10 OFFSET :offset;
-- SELECT COUNT(*) FROM posts;

-- Server authorization examples (supply authenticated :current_user_id):
-- UPDATE posts SET title = :title, content = :content, updated_at = CURRENT_TIMESTAMP
-- WHERE id = :post_id AND author_id = :current_user_id;
-- DELETE FROM posts WHERE id = :post_id AND author_id = :current_user_id;
-- INSERT INTO blocked_keywords (keyword, created_by)
-- SELECT :keyword, id FROM users WHERE id = :current_user_id AND role = 'ADMIN';
