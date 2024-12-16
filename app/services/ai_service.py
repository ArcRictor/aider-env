from openai import OpenAI
from ..config import settings

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

    def analyze_email(self, email_content, subject):
        """Analyze email content and provide insights"""
        prompt = f"""
        Analyze this email with subject: "{subject}"
        
        Content:
        {email_content}
        
        Provide a brief, professional analysis focusing on:
        1. The main purpose/intent of the email
        2. Key points or action items
        3. Priority level (High/Medium/Low)
        
        Keep the analysis concise and actionable.
        """
        
        try:
            if not settings.OPENROUTER_API_KEY.startswith("sk-or-v1-"):
                return "Error: Invalid OpenRouter API key format. Key should start with 'sk-or-v1-'"

            response = self.client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional email analyst. Provide clear, concise analysis of emails."},
                    {"role": "user", "content": prompt}
                ],
                headers={
                    "HTTP-Referer": "http://localhost:8000",  # OpenRouter requires this
                    "X-Title": "Smart Email Manager"  # Optional but recommended
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing email: {str(e)}"
