BEGIN;
--
-- Add field webauthn_user_handle to accountentity
--
CREATE TABLE "new__accounts_accountentity" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "webauthn_user_handle" BLOB NULL UNIQUE, "entity_type" varchar(32) NOT NULL, "identity_email" varchar(254) NULL UNIQUE, "email_verified_at" datetime NULL, "is_active" bool NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__accounts_accountentity" ("id", "entity_type", "identity_email", "email_verified_at", "is_active", "created_at", "updated_at", "user_id", "webauthn_user_handle") SELECT "id", "entity_type", "identity_email", "email_verified_at", "is_active", "created_at", "updated_at", "user_id", NULL FROM "accounts_accountentity";
DROP TABLE "accounts_accountentity";
ALTER TABLE "new__accounts_accountentity" RENAME TO "accounts_accountentity";
CREATE UNIQUE INDEX "accounts_single_owner_entity" ON "accounts_accountentity" ("entity_type") WHERE "entity_type" = 'owner';
--
-- Create model OwnerWebAuthnCredential
--
CREATE TABLE "accounts_ownerwebauthncredential" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "credential_id" BLOB NOT NULL UNIQUE, "public_key" BLOB NOT NULL, "user_handle" BLOB NOT NULL, "sign_count" bigint unsigned NOT NULL CHECK ("sign_count" >= 0), "aaguid" varchar(36) NOT NULL, "transports" text NOT NULL CHECK ((JSON_VALID("transports") OR "transports" IS NULL)), "label" varchar(100) NOT NULL, "backup_eligible" bool NOT NULL, "backed_up" bool NOT NULL, "created_at" datetime NOT NULL, "last_used_at" datetime NULL, "revoked_at" datetime NULL, "owner_entity_id" bigint NOT NULL REFERENCES "accounts_accountentity" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model OwnerWebAuthnChallenge
--
CREATE TABLE "accounts_ownerwebauthnchallenge" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "session_key_hash" varchar(64) NOT NULL, "ceremony" varchar(20) NOT NULL, "challenge_hash" varchar(64) NOT NULL UNIQUE, "expires_at" datetime NOT NULL, "used_at" datetime NULL, "created_at" datetime NOT NULL, "owner_entity_id" bigint NOT NULL REFERENCES "accounts_accountentity" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "accounts_ownerwebauthncredential_owner_entity_id_8fb3ce82" ON "accounts_ownerwebauthncredential" ("owner_entity_id");
CREATE INDEX "acct_owner_webauthn_idx" ON "accounts_ownerwebauthncredential" ("owner_entity_id", "revoked_at");
CREATE INDEX "accounts_ownerwebauthnchallenge_owner_entity_id_4bfb440d" ON "accounts_ownerwebauthnchallenge" ("owner_entity_id");
CREATE INDEX "acct_owner_webauthn_chal_idx" ON "accounts_ownerwebauthnchallenge" ("owner_entity_id", "ceremony", "created_at");
COMMIT;
