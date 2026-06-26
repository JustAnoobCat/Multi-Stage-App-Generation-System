from utils import client, clean_json
import json

systemPrompt =  """
    You are stage 2 of an app compiler. You receive a structured intent JSON and convert it into a system design.

    Return ONLY this exact JSON structure, no explanations, no markdown:
    {
        "pages":[
            {
                "name":"string",
                "route":"string",
                "access":["string"],
                "components":["string"]
            }
        ],
        "auth_strategy":"string",
        "role_permissions":{
            "role_name":{
                "can": ["string"],
                "cannot": ["string"]
            }
        },
        "payment_flow":"string or null",
        "background_jobs":["string"],
        "third_party_integrations":["string"]
    }

    Rules:
    -Every role in role_intent should appear in role_permissions.
    -Every page must have atleast one component.
    -If auth_required is true, always include a login page and register page.
    -If payment_required is true, always include a pricing page and payment_flow.

    """

def generate_design(intent):
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [
            {
                "role":"system",
                "content": systemPrompt
            },
            {
                "role":"user",
                "content": json.dumps(intent)
            }
        ]
    )
    raw = response.choices[0].message.content   
    design = json.loads(clean_json(raw))
    return design

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

    result = generate_design(sample_intent)
    print(json.dumps(result, indent=2))    