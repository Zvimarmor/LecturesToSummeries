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
        
        # Using Gemini 1.5 Pro for its large context window
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def generate_summary(self, transcript, materials_text, summary_type="normal", language="english"):
        """
        Generates a summary based on transcript and lecture materials.
        
        :param summary_type: 'informative', 'brief', or 'normal'
        :param language: 'english' or 'hebrew'
        """
        
        prompts = {
            "informative": (
                "Create a highly detailed and informative summary of the following lecture. "
                "Include all main points, examples, and technical details discussed. "
                "The target audience is students who missed the lecture and need to understand everything. "
            ),
            "brief": (
                "Create a brief summary and a list of key 'memory-joggers' for the following lecture. "
                "Focus on the main themes and important keywords. "
                "The target audience is students who attended the lecture and just need a quick reminder. "
            ),
            "normal": (
                "Create a clear and balanced summary of the following lecture. "
                "Highlight the core concepts and the structure of the talk. "
                "The target audience is students who attended but want a structured review of the content. "
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
