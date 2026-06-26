import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client =  Groq(api_key=os.getenv("GROQ_API_KEY"))

def clean_json(raw):
    cleaned = raw.replace("```json","").replace("```","").strip()
    return cleaned