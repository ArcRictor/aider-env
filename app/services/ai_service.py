from openai import OpenAI
from ..config import settings

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8000",  # OpenRouter requires this
                "X-Title": "Smart Email Manager"  # Optional but recommended
            }
        )

    def analyze_email(self, email_content, subject):
        """Analyze email content and provide insights"""
        prompt = f"""
        Analyze this email with subject: "{subject}"
        
        Content:
        {email_content}
        
        Provide only the following two pieces of information:

        Priority: [Single word: High/Medium/Low]
        Action: [Single word: Respond/Archive/Delete]
        """
        
        try:
            if not settings.OPENROUTER_API_KEY.startswith("sk-or-v1-"):
                return "Error: Invalid OpenRouter API key format. Key should start with 'sk-or-v1-'"

            response = self.client.chat.completions.create(
                model="openai/o1-mini-2024-09-12",
                messages=[
                    {"role": "system", "content": "You are a professional email analyst. Provide clear, concise analysis of emails."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing email: {str(e)}"
