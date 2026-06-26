import json
from utils import client, clean_json

def validate_repair(intent, schema):
    results = []

    #Check 1: Users table exists
    tables = [t["name"] for t in schema["db_schema"]["tables"]]
    if "users" not in tables:
        schema["db_schema"]["tables"].append(
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "integer", "nullable": False, "unique": True},
                    {"name": "email", "type": "string", "nullable": False, "unique": True},
                    {"name": "password", "type": "string", "nullable": False, "unique": False},
                    {"name": "role", "type": "string", "nullable": False, "unique": False}
                ],
                "relations": []
            }
        )
        results.append({"check": "Users table exists","passed": False,"fix": "Injected users table"})
    else:
        results.append({"check": "Users table exists","passed": True,"fix": None})

    #Check 2: Auth endpoints exist
    paths = [e["path"] for e in schema["api_schema"]["endpoints"]]
    if intent["auth_required"] and "/login" not in paths:
        schema["api_schema"]["endpoints"].insert(0, {
            "method": "POST",
            "path": "/login",
            "auth": False,
            "roles": [],
            "request_body": {"email": "string","password": "string"},
            "response": {"token": "string"}
        })
        results.append({"check": "Auth endpoint exist", "passed": False, "fix": "Injected /login endpoint"})
    else:
        results.append({"check": "Auth endpoint exist", "passed": True, "fix": None})
    
    #Check 3: Payment endpoints exist
    if intent["payment_required"] and "/subscriptions" not in paths:
        schema["api_schema"]["endpoints"].insert(0, {
            "method": "POST",
            "path": "/subscriptions",
            "auth": True,
            "roles": ["Admin","User"],
            "request_body": {"plain_id": "string"},
            "response": {"subscription_id": "string"}
        })
        results.append({"check": "Payment endpoints exist", "passed": False, "fix": "Injected /subscription endpoint"})
    else:
        results.append({"check": "Payment endpoint exist", "passed": True, "fix": None})

    #Check 4: All intent roles in auth schema
    auth_roles = schema["auth_schema"]["roles"]
    intent_roles = intent["user_roles"]
    missing_roles = [r for r in intent_roles if r not in auth_roles]
    if missing_roles:
        schema["auth_schema"]["roles"].extend(missing_roles)
        results.append({"check": "All roles present in auth schema", "passed": False, "fix": f"Added missing roles: {missing_roles}"})
    else:
        results.append({"check": "All roles present in auth schema", "passed": True, "fix": None})

    #Check 5: All pages have components
    pages_without_components = [p["name"] for p in schema.get("pages",[]) if not p.get("components")]
    if pages_without_components:
        results.append({"check": "All pages have components", "passed": False, "fix": f"Pages missing components: {pages_without_components}"})
    else:
        results.append({"check": "All pages have components", "passed": True, "fix": None})
    
    #Check 6: Required top level keys exist
    required_keys = ["ui_schema","api_schema","db_schema","auth_schema"]
    missing_keys = [k for k in required_keys if k not in schema]
    if missing_keys:
        results.append({"check": "All required keys present", "passed": False, "fix": f"Missing keys: {missing_keys}"})
    else:
        results.append({"check": "All required keys present", "passed": True, "fix": None})
    
    return schema, results

if __name__ == "__main__":
    sample_intent = {
        "auth_required": True,
        "payment_required": True,
        "user_roles": ["Admin", "User"]
    }
    
    sample_schema = {
        "ui_schema": {"components": []},
        "api_schema": {"endpoints": []},
        "db_schema": {"tables": []},
        "auth_schema": {"strategy": "JWT", "roles": ["Admin"], "permissions": {}}
    }
    fixed_schema, validation = validate_repair(sample_intent,sample_schema)

    print("Validation Results: ")
    for r in validation:
        status = "PASS" if r["passed"] else "FIXED"
        fix = f" -> {r["fix"]}" if r["fix"] else ""
        print(f"[{status}] {r["check"]} {fix}")