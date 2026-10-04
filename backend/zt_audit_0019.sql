BEGIN;
--
-- Add field expires_at to ownersessionbinding
--
ALTER TABLE "accounts_ownersessionbinding" ADD COLUMN "expires_at" datetime NULL;
--
-- Raw Python operation
--
-- THIS OPERATION CANNOT BE WRITTEN AS SQL
--
-- Alter field expires_at on ownersessionbinding
--
CREATE TABLE "new__accounts_ownersessionbinding" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "binding_token_hash" varchar(64) NOT NULL UNIQUE, "session_key_hash" varchar(64) NOT NULL, "created_at" datetime NOT NULL, "last_seen_at" datetime NULL, "revoked_at" datetime NULL, "owner_entity_id" bigint NOT NULL REFERENCES "accounts_accountentity" ("id") DEFERRABLE INITIALLY DEFERRED, "trusted_device_id" bigint NULL REFERENCES "accounts_ownertrusteddevice" ("id") DEFERRABLE INITIALLY DEFERRED, "webauthn_credential_id" bigint NULL REFERENCES "accounts_ownerwebauthncredential" ("id") DEFERRABLE INITIALLY DEFERRED, "expires_at" datetime NOT NULL);
INSERT INTO "new__accounts_ownersessionbinding" ("id", "binding_token_hash", "session_key_hash", "created_at", "last_seen_at", "revoked_at", "owner_entity_id", "trusted_device_id", "webauthn_credential_id", "expires_at") SELECT "id", "binding_token_hash", "session_key_hash", "created_at", "last_seen_at", "revoked_at", "owner_entity_id", "trusted_device_id", "webauthn_credential_id", coalesce("expires_at", NULL) FROM "accounts_ownersessionbinding";
DROP TABLE "accounts_ownersessionbinding";
ALTER TABLE "new__accounts_ownersessionbinding" RENAME TO "accounts_ownersessionbinding";
CREATE UNIQUE INDEX "acct_owner_sess_active_uniq" ON "accounts_ownersessionbinding" ("owner_entity_id", "session_key_hash") WHERE "revoked_at" IS NULL;
CREATE INDEX "accounts_ownersessionbinding_owner_entity_id_263f1e37" ON "accounts_ownersessionbinding" ("owner_entity_id");
CREATE INDEX "accounts_ownersessionbinding_trusted_device_id_3f0e6265" ON "accounts_ownersessionbinding" ("trusted_device_id");
CREATE INDEX "accounts_ownersessionbinding_webauthn_credential_id_62294f21" ON "accounts_ownersessionbinding" ("webauthn_credential_id");
CREATE INDEX "acct_owner_sess_rev_idx" ON "accounts_ownersessionbinding" ("owner_entity_id", "revoked_at");
COMMIT;
