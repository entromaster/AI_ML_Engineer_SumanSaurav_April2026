import warnings
warnings.filterwarnings('ignore')
import google.generativeai as genai
import traceback

genai.configure(api_key='AIzaSyAFqKx4tf9WHZyLUyDjDo4nQwI9TSl-6NM')

output = []

output.append("=== Available Gemini Models ===")
try:
    for m in genai.list_models():
        if 'gemini' in m.name.lower():
            output.append(m.name)
except Exception as e:
    output.append(f"Error listing models: {e}")

models_to_test = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-preview-04-17",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash"
]

for model_name in models_to_test:
    output.append(f"\n=== Quick test with {model_name} ===")
    try:
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content("Say hello in one word")
        output.append(f"SUCCESS: {resp.text.strip()}")
    except Exception as e:
        output.append(f"FAILED: {e}")
        # Only add first line of traceback for brevity if needed
        # output.append(traceback.format_exc().split('\\n')[-2])

with open("model_test_results.txt", "w") as f:
    f.write("\n".join(output))

print("Results written to model_test_results.txt")
