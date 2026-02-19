import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class Summarizer:
    def __init__(self, api_key=None):
        """
        Initialize Gemini API.
        """
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            print("Warning: GEMINI_API_KEY not found in environment.")
        else:
            genai.configure(api_key=key)
        
        # Using Gemini 1.5 Flash (latest) for increased rate limit availability
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_summary(self, transcript, materials_text, summary_type="normal", language="english"):
        """
        Generates a summary based on transcript and lecture materials.
        
        :param summary_type: 'informative', 'brief', or 'normal'
        :param language: 'english' or 'hebrew'
        """
        
        prompts = {
            "informative": (
                "Create a comprehensive textbook-style explanation of the topics covered in this lecture. "
                "Explain the concepts, theories, and examples in depth. "
                "DO NOT use phrases like 'The lecture talks about', 'The speaker mentions', or 'In this video'. "
                "Instead, directly state the facts and explanations as if writing an article or educational resource. "
                "The goal is to teach the material to someone who has never seen the lecture."
            ),
            "brief": (
                "Create a concise cheat-sheet of the key concepts from this lecture. "
                "Provide direct definitions and bullet points of the main takeaways. "
                "DO NOT use meta-language like 'The lecture covers'. "
                "Focus strictly on the information itself for quick review."
            ),
            "normal": (
                "Create a clear and structured summary of the material. "
                "Organize the content logically with headings. "
                "Explain the ideas directly without referring to 'the lecture' or 'the speaker'. "
                "Focus on delivering the knowledge efficiently."
            )
        }

        lang_instruction = f"Please provide the output in {language}."
        
        base_prompt = prompts.get(summary_type, prompts["normal"])
        
        full_prompt = (
            f"{base_prompt}\n\n"
            f"{lang_instruction}\n\n"
            "--- LECTURE TRANSCRIPT ---\n"
            f"{transcript}\n\n"
            "--- LECTURE MATERIALS (Slides Text) ---\n"
            f"{materials_text}\n\n"
            "--- END OF DATA ---"
        )

        print(f"Generating {summary_type} summary in {language}...")
        response = self.model.generate_content(full_prompt)
        
        return response.text

if __name__ == "__main__":
    # Test stub (requires API key in .env)
    summarizer = Summarizer()
    # test_output = summarizer.generate_summary("Transcribed text here...", "Slide text here...")
    # print(test_output)
