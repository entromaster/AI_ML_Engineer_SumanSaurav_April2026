import warnings
warnings.filterwarnings('ignore')
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Warning: GOOGLE_API_KEY not found in environment")
genai.configure(api_key=api_key)

print("=== Available Gemini Models ===")
for m in genai.list_models():
    if 'gemini' in m.name.lower():
        print(m.name)

print("\n=== Quick test with gemini-2.0-flash ===")
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content("Say hello in one word")
    print(f"SUCCESS: {resp.text}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n=== Quick test with gemini-1.5-flash ===")
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content("Say hello in one word")
    print(f"SUCCESS: {resp.text}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n=== Quick test with gemini-2.0-flash-lite ===")
try:
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    resp = model.generate_content("Say hello in one word")
    print(f"SUCCESS: {resp.text}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n=== Quick test with gemini-2.5-flash-preview-04-17 ===")
try:
    model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
    resp = model.generate_content("Say hello in one word")
    print(f"SUCCESS: {resp.text}")
except Exception as e:
    print(f"FAILED: {e}")
