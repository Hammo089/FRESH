"""Create an isolated Community trial over the local Odoo API."""
import configparser
import json
import os
from pathlib import Path
import secrets
import xmlrpc.client

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:18069"
DB = "fresh_trial"
credential_path = ROOT / "secrets/trial_login.json"
if not credential_path.exists():
    credentials = {"url": URL, "database": DB, "login": "fresh.admin", "password": secrets.token_urlsafe(24)}
    fd = os.open(credential_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        json.dump(credentials, handle, indent=2)
credentials = json.loads(credential_path.read_text())
database = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/db", allow_none=True)
if DB not in database.list():
    config = configparser.ConfigParser()
    config.read(ROOT / "config/odoo.conf")
    database.create_database(config["options"]["admin_passwd"], DB, False, "en_US", credentials["password"], credentials["login"], "LB")
    print("Created isolated trial database.", flush=True)
common = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, credentials["login"], credentials["password"], {})
if not uid:
    raise RuntimeError("Trial authentication failed; existing database was not altered.")
models = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object", allow_none=True)
def call(model, method, args, kwargs=None):
    return models.execute_kw(DB, uid, credentials["password"], model, method, args, kwargs or {})

modules = call("ir.module.module", "search_read", [[["name", "=", "point_of_sale"]]], {"fields": ["state"]})
if len(modules) != 1:
    raise RuntimeError("Community POS module not found.")
if modules[0]["state"] != "installed":
    print("Installing Community Point of Sale and its dependencies.", flush=True)
    call("ir.module.module", "button_immediate_install", [[modules[0]["id"]]])
print("Trial login and Community POS installation verified. Credentials: secrets/trial_login.json", flush=True)
