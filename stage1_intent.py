from utils import client, clean_json
import json

systemPrompt =  """
    You are stage 1 of an app compiler. Your job is to extract intent from user's natural language description of an app they want to build.
    Return ONLY this exact JSON structure, no explanations, no markdown:
    {
        "app_name": "string",
        "app_type": "string",
        "core_features": ["string"],
        "user_roles": ["string"],
        "auth_required": boolean,
        "payment_required": boolean,
        "payment_provider": "string or null",
        "key_entities": ["string"],
        "assumptions": ["string"]
    }
    Rules:
    -If something is not mentioned, make a reasonable assumption and include it in the assumptions.
    -user_roles should include atleast one role.
    -key_entities are the main data objects that the app manages (ex: User,Contact, Invoice)
"""
def extract_intent(user_input):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"system",
                "content": systemPrompt
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )
    raw = response.choices[0].message.content
    intent = json.loads(clean_json(raw))
    return intent

if __name__ == "__main__":
    user_input = "Build a CRM with login, contacts, dashboard, role-based access and premium plan with payments. Admin can see the analytics."
    result = extract_intent(user_input)
    print(json.dumps(result,indent=2))