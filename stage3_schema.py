import json
from utils import client, clean_json

systemPrompt = """
    You are stage 3 of an app compiler. You receive intent and desgin JSON and generate a complete app schema.

    Return ONLY this exact JSON structure, no explanations, no markdown:
    {
        "ui_schema": {
            "components": [
                {
                    "id": "string",
                    "type": "string",
                    "props": {},
                    "page": "string"
                }
            ]
        },
        "api_schema": {
            "endpoints": [
                {
                    "method": "string",
                    "path": "string",
                    "auth": boolean,
                    "roles": ["string"],
                    "request_body": {},
                    "response": {}
                }
            ]
        },
        "db_schema": {
            "tables": [
                {
                    "name": "string",
                    "columns": [
                        {
                            "name": "string",
                            "type": "string",
                            "nullable": boolean,
                            "unique": boolean
                        }
                    ],
                    "relations": ["string"]
                }
            ]
        },
        "auth_schema": {
            "strategy": "string",
            "roles": ["string"],
            "permissions": {}
        }
    }
    Rules:
    - Every API endpoint field must match a DB column.
    - Every UI component must map to a page from the design.
    - If auth is required, users table must exist in DB with id, email, password, role columns.
    - If payment is required, include a subscriptions table and payment endpoints.
"""

def generate_schema(intent, design):
    combined = {"intent": intent, "design": design}
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [
            {
                "role": "system",
                "content": systemPrompt
            },
            {
                "role": "user",
                "content": json.dumps(combined)
            }
        ]
    )
    raw = response.choices[0].message.content
    cleaned = clean_json(raw)
    schema = json.loads(cleaned)
    return schema

if __name__ == "__main__":
    sample_intent = {
        "app_name": "CRM System",
        "app_type": "Customer Relationship Management",
        "core_features": ["login", "contacts", "dashboard", "role-based access", "premium plan"],
        "user_roles": ["Admin", "User"],
        "auth_required": True,
        "payment_required": True,
        "payment_provider": "Stripe",
        "key_entities": ["User", "Contact", "Invoice", "Subscription"],
        "assumptions": []
    }
    sample_design = {
        "pages": [
            {"name": "Login", "route": "/login", "access": ["Admin", "User"], "components": ["LoginForm"]},
            {"name": "Dashboard", "route": "/dashboard", "access": ["Admin", "User"], "components": ["StatsCard", "Chart"]},
            {"name": "Contacts", "route": "/contacts", "access": ["Admin", "User"], "components": ["ContactList", "ContactForm"]}
        ],
        "auth_strategy": "Session-based authentication",
        "role_permissions": {
            "Admin": {"can": ["view_contacts", "edit_contacts", "manage_users"], "cannot": []},
            "User": {"can": ["view_contacts"], "cannot": ["edit_contacts", "manage_users"]}
        },
        "payment_flow": "Stripe Checkout",
        "background_jobs": ["SendInvoiceReminders"],
        "third_party_integrations": ["Stripe"]
    }
    result = generate_schema(sample_intent, sample_design)
    print(json.dumps(result,indent=2))