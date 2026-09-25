"""Prepare local trial credentials without replacing existing files."""
from pathlib import Path
import os
import secrets

root = Path(__file__).resolve().parent
for folder in ("secrets", "config", "addons"):
    (root / folder).mkdir(exist_ok=True)

def create_once(path, content, mode):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    except FileExistsError:
        return
    with os.fdopen(fd, "w") as handle:
        handle.write(content)

create_once(root / "secrets/db_password", secrets.token_urlsafe(32) + "\n", 0o600)
create_once(root / "config/odoo.conf", "\n".join([
    "[options]",
    "admin_passwd = " + secrets.token_urlsafe(32),
    "data_dir = /var/lib/odoo",
    "addons_path = /mnt/extra-addons",
    "dbfilter = ^fresh_trial$",
    "list_db = True",
    "proxy_mode = False",
    "workers = 0",
    "",
]), 0o644)
print("Local trial configuration prepared. Existing credentials preserved.")
