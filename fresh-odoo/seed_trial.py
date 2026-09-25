"""Seed clearly labelled sample data only in the isolated fresh_trial database."""
from bootstrap_trial import call

company = call("res.company", "search", [[]])
if len(company) != 1:
    raise RuntimeError("Expected one trial company.")
call("res.company", "write", [company, {"name": "FRESH — TEST ONLY"}])
category_ids = {}
for name in ("TEST — Drinks / مشروبات", "TEST — Bakery / مخبوزات"):
    ids = call("pos.category", "search", [[["name", "=", name]]])
    category_ids[name] = ids[0] if ids else call("pos.category", "create", [{"name": name}])

samples = [
    ("FRESH-TEST-WATER", "TEST — Water / مياه", 50000, "TEST — Drinks / مشروبات"),
    ("FRESH-TEST-JUICE", "TEST — Juice / عصير", 100000, "TEST — Drinks / مشروبات"),
    ("FRESH-TEST-BREAD", "TEST — Bread / خبز", 75000, "TEST — Bakery / مخبوزات"),
]
for code, name, price, category in samples:
    if not call("product.template", "search", [[["default_code", "=", code]]]):
        call("product.template", "create", [{
            "name": name, "default_code": code, "list_price": price,
            "available_in_pos": True, "sale_ok": True,
            "taxes_id": [[5, 0, 0]], "supplier_taxes_id": [[5, 0, 0]],
            "pos_categ_ids": [[6, 0, [category_ids[category]]]],
        }])
configs = call("pos.config", "search", [[["name", "=", "FRESH — Trial Cashier"]]])
if not configs:
    configs = [call("pos.config", "create", [{"name": "FRESH — Trial Cashier"}])]
print(call("pos.config", "read", [configs], {"fields": ["name", "currency_id", "payment_method_ids"]}))
print("Three tax-free test products prepared. Prices are fictional LBP amounts.")
