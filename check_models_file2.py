import warnings
warnings.filterwarnings('ignore')
import google.generativeai as genai

genai.configure(api_key='AIzaSyAFqKx4tf9WHZyLUyDjDo4nQwI9TSl-6NM')

models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-flash-latest",
    "gemini-3.1-flash-live-preview"
]

output = []
for model_name in models_to_test:
    output.append(f"\n=== Quick test with {model_name} ===")
    try:
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content("Say hello in one word")
        output.append(f"SUCCESS: {resp.text.strip()}")
    except Exception as e:
        output.append(f"FAILED: {e}")

with open("model_test_results.txt", "w") as f:
    f.write("\n".join(output))

print("Results written to model_test_results.txt")
