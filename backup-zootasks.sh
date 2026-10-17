#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

PROJECT_DIR="${HOME}/ZooTasks"
BACKUP_DIR="${HOME}/zootasks-backups"
DATE="$(date +%Y-%m-%d_%H-%M-%S)"

BACKUP_FILE="${BACKUP_DIR}/zootasks-backup-${DATE}.tar.gz"
DB_BACKUP_FILE="${BACKUP_DIR}/db-${DATE}.sqlite3"

# Backups are sensitive recovery assets.
umask 077
mkdir -p "${BACKUP_DIR}"
chmod 700 "${BACKUP_DIR}"

TMP_BACKUP_FILE="$(mktemp "${BACKUP_DIR}/.zootasks-backup.XXXXXX")"
TMP_DB_BACKUP_FILE="$(mktemp "${BACKUP_DIR}/.zootasks-db.XXXXXX")"

cleanup() {
    rm -f -- "${TMP_BACKUP_FILE}" "${TMP_DB_BACKUP_FILE}"
}
trap cleanup EXIT INT TERM

cd "${PROJECT_DIR}"

# Source archive: exclude credentials, private keys, databases, production
# dumps, user uploads, local recovery artifacts, runtime logs, virtual
# environments and Git metadata. The SQLite database is backed up separately.
tar \
  --exclude='./.git' \
  --exclude='./backend/venv' \
  --exclude='./venv' \
  --exclude='./venv-zootasks' \
  --exclude='./__pycache__' \
  --exclude='*/__pycache__' \
  --exclude='*.pyc' \
  --exclude='./.env' \
  --exclude='./.env.*' \
  --exclude='*/.env' \
  --exclude='*/.env.*' \
  --exclude='./.ssh' \
  --exclude='*/.ssh' \
  --exclude='./.aws' \
  --exclude='*/.aws' \
  --exclude='./secrets' \
  --exclude='*/secrets' \
  --exclude='./credentials' \
  --exclude='*/credentials' \
  --exclude='./keys' \
  --exclude='*/keys' \
  --exclude='./certs' \
  --exclude='*/certs' \
  --exclude='./certificates' \
  --exclude='*/certificates' \
  --exclude='./dumps' \
  --exclude='*/dumps' \
  --exclude='./exports' \
  --exclude='*/exports' \
  --exclude='./media' \
  --exclude='*/media' \
  --exclude='./uploads' \
  --exclude='*/uploads' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='*.p12' \
  --exclude='*.pfx' \
  --exclude='*.jks' \
  --exclude='*.keystore' \
  --exclude='id_rsa*' \
  --exclude='id_ed25519*' \
  --exclude='*.dump' \
  --exclude='*.pgdump' \
  --exclude='*.sql.gz' \
  --exclude='*-dump.sql' \
  --exclude='*-backup.sql' \
  --exclude='*production*.sql' \
  --exclude='*prod*.sql' \
  --exclude='*.rdb' \
  --exclude='*.aof' \
  --exclude='*.bak*' \
  --exclude='*.backup*' \
  --exclude='*.before-*' \
  --exclude='*-backup*' \
  --exclude='*.sqlite3*' \
  --exclude='*.db*' \
  --exclude='*.log*' \
  --exclude='./backups' \
  --exclude='./backup_*' \
  --exclude='*/backups' \
  --exclude='*/backup_*' \
  --exclude='*.tar.gz' \
  -czf "${TMP_BACKUP_FILE}" .

chmod 600 "${TMP_BACKUP_FILE}"
mv -f -- "${TMP_BACKUP_FILE}" "${BACKUP_FILE}"

# SQLite backup API is used instead of cp so a live database is copied through
# SQLite's consistency mechanism (including WAL-mode databases).
if [ -f "${PROJECT_DIR}/backend/db.sqlite3" ]; then
    PYTHON_BIN="${PROJECT_DIR}/venv/bin/python"
    if [ ! -x "${PYTHON_BIN}" ]; then
        PYTHON_BIN="$(command -v python)"
    fi

    PYTHON_BIN="${PYTHON_BIN}" SRC_DB="${PROJECT_DIR}/backend/db.sqlite3" DST_DB="${TMP_DB_BACKUP_FILE}" \
      "${PYTHON_BIN}" - <<'PY'
import os
import sqlite3

src_path = os.environ["SRC_DB"]
dst_path = os.environ["DST_DB"]

src = sqlite3.connect(src_path)
dst = sqlite3.connect(dst_path)
try:
    src.backup(dst)
    dst.commit()
    result = dst.execute("PRAGMA integrity_check").fetchone()[0]
    if result != "ok":
        raise SystemExit(f"SQLite integrity check failed: {result}")
finally:
    dst.close()
    src.close()
PY

    chmod 600 "${TMP_DB_BACKUP_FILE}"
    mv -f -- "${TMP_DB_BACKUP_FILE}" "${DB_BACKUP_FILE}"
else
    DB_BACKUP_FILE=""
fi

echo "======================================"
echo "ZooTasks Backup Completed"
echo "======================================"
echo "Backup file:"
echo "${BACKUP_FILE}"

if [ -n "${DB_BACKUP_FILE}" ]; then
    echo
    echo "Database backup:"
    echo "${DB_BACKUP_FILE}"
else
    echo
    echo "Database backup:"
    echo "No backend/db.sqlite3 found"
fi
