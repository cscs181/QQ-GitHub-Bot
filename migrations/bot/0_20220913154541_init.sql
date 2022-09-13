-- upgrade --
CREATE TABLE IF NOT EXISTS "group" (
    "qq_group" BIGINT  UNIQUE,
    "qqguild_channel" VARCHAR(255)  UNIQUE,
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "bind_repo" VARCHAR(255)
);
CREATE INDEX IF NOT EXISTS "idx_group_qq_grou_9d50c8" ON "group" ("qq_group");
CREATE INDEX IF NOT EXISTS "idx_group_qqguild_0531b8" ON "group" ("qqguild_channel");
CREATE TABLE IF NOT EXISTS "user" (
    "qq_id" BIGINT  UNIQUE,
    "qqguild_id" VARCHAR(255)  UNIQUE,
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "access_token" VARCHAR(255) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_user_qq_id_591d35" ON "user" ("qq_id");
CREATE INDEX IF NOT EXISTS "idx_user_qqguild_e5da0e" ON "user" ("qqguild_id");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
