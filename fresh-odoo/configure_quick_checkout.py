"""Configure quick payment exclusively on the FRESH trial register."""
from bootstrap_trial import call

call("ir.module.module", "update_list", [])
module = call("ir.module.module", "search_read", [[["name", "=", "fresh_pos"]]], {"fields": ["state"]})
if len(module) != 1:
    raise RuntimeError("FRESH addon not discovered. Restart Odoo first.")
if module[0]["state"] != "installed":
    call("ir.module.module", "button_immediate_install", [[module[0]["id"]]])
configs = call("pos.config", "search", [[["name", "=", "FRESH — Quick Checkout"]]])
if not configs:
    configs = [call("pos.config", "create", [{"name": "FRESH — Quick Checkout"}])]
config = call("pos.config", "read", [configs], {"fields": ["payment_method_ids", "company_id"]})[0]
quick_ids = []
for name, code, sequence in [("كاش / Cash", "FCA", 10), ("ويش / Whish", "FWH", 20), ("توترز / Toters", "FTT", 30)]:
    journals = call("account.journal", "search", [[["code", "=", code], ["company_id", "=", config["company_id"][0]]]])
    journal = journals[0] if journals else call("account.journal", "create", [{"name": name + " — Trial", "code": code, "type": "cash" if code == "FCA" else "bank", "company_id": config["company_id"][0]}])
    ids = call("pos.payment.method", "search", [[["name", "=", name], ["company_id", "=", config["company_id"][0]]]])
    values = {"name": name, "journal_id": journal, "sequence": sequence, "split_transactions": False, "payment_method_type": "none"}
    if ids:
        call("pos.payment.method", "write", [ids, values])
        quick_ids.append(ids[0])
    else:
        quick_ids.append(call("pos.payment.method", "create", [values]))
call("pos.config", "write", [configs, {
    "payment_method_ids": [[6, 0, list(dict.fromkeys(config["payment_method_ids"] + quick_ids))]],
    "fast_payment_method_ids": [[6, 0, quick_ids]],
    "use_fast_payment": True,
    "iface_print_auto": True,
    "iface_print_skip_screen": True,
}])
print("FRESH quick checkout configured: Cash, Whish, Toters. Automatic receipt enabled.")
