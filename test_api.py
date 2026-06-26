from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant who responds only in valid JSON format. No explanations, no markdown, just raw JSON."
            },
            {
                "role": "user",
                "content": "Give me a person object with name,age and skills fields."
            }
        ]
)

data = json.loads(response.choices[0].message.content)  

print(data["name"])
#print(response.choices[0].message.content)