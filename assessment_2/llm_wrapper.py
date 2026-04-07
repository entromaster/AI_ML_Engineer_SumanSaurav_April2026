"""
LLM Wrapper
Allows seamless switching between Google Gemini and OpenAI based on available API keys.
"""

class LLMResponse:
    def __init__(self, text):
        self.text = text


class LLMWrapper:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        
        if provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        else:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel("gemini-2.0-flash")
            
    def generate_content(self, prompt: str):
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return LLMResponse(response.choices[0].message.content)
        else:
            return self.client.generate_content(prompt)
