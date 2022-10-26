-- upgrade --
CREATE TABLE IF NOT EXISTS "group_subscription" (
    "qq_group" BIGINT  UNIQUE,
    "qqguild_channel" VARCHAR(255)  UNIQUE,
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "owner" VARCHAR(255) NOT NULL,
    "repo" VARCHAR(255) NOT NULL,
    "event" VARCHAR(255) NOT NULL,
    "action" VARCHAR(255)
);
CREATE INDEX IF NOT EXISTS "idx_group_subsc_qq_grou_9d77e0" ON "group_subscription" ("qq_group");
CREATE INDEX IF NOT EXISTS "idx_group_subsc_qqguild_8a9fcf" ON "group_subscription" ("qqguild_channel");
CREATE INDEX IF NOT EXISTS "idx_group_subsc_owner_cda9bf" ON "group_subscription" ("owner", "repo", "event", "action");
CREATE TABLE IF NOT EXISTS "user_subscription" (
    "qq_id" BIGINT,
    "qqguild_id" VARCHAR(255),
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "owner" VARCHAR(255) NOT NULL,
    "repo" VARCHAR(255) NOT NULL,
    "event" VARCHAR(255) NOT NULL,
    "action" VARCHAR(255)
);
CREATE INDEX IF NOT EXISTS "idx_user_subscr_qq_id_d076c7" ON "user_subscription" ("qq_id");
CREATE INDEX IF NOT EXISTS "idx_user_subscr_qqguild_f24790" ON "user_subscription" ("qqguild_id");
CREATE INDEX IF NOT EXISTS "idx_user_subscr_owner_7cb964" ON "user_subscription" ("owner", "repo", "event", "action");-- downgrade --
DROP TABLE IF EXISTS "group_subscription";
DROP TABLE IF EXISTS "user_subscription";
