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

    def generate_informative_summary(self, transcript_segments, materials_text, language="english"):
        """
        Generates a highly informative summary by processing each segment separately and combining them.
        """
        num_segments = len(transcript_segments)
        segment_summaries = []

        for i, segment_text in enumerate(transcript_segments):
            if not segment_text.strip():
                continue
                
            print(f"Summarizing segment {i+1} of {num_segments}...")
            
            prompt = (
                f"Topic: Lecture Transcription Summary\n"
                f"Context: This is segment {i+1} out of {num_segments} from a full lecture recording.\n\n"
                f"TASK: Write a detailed, textbook-style chapter for this specific segment of the lecture.\n"
                f"INSTRUCTIONS:\n"
                f"1. Directly explain the concepts, theories, and examples discussed in the transcript segment below.\n"
                f"2. Use the provided presentation materials (slides) only if they are directly relevant to this segment. IGNORE any slides that cover other parts of the lecture.\n"
                f"3. Maintain a formal, academic tone. Do NOT mention 'the speaker' or 'the recording'.\n"
                f"4. Focus on clarity and technical depth.\n\n"
                f"Language: {language}\n\n"
                f"--- TRANSCRIPT SEGMENT {i+1}/{num_segments} ---\n"
                f"{segment_text}\n\n"
                f"--- LECTURE MATERIALS (Full Slide Text) ---\n"
                f"{materials_text}\n\n"
                "--- END OF DATA ---"
            )
            
            response = self.model.generate_content(prompt)
            segment_summaries.append(response.text)

        # Final pass to combine and clean up
        if not segment_summaries:
            return "No content to summarize."

        print("Combining segment summaries into a single document...")
        combined_summary = "\n\n---\n\n".join(segment_summaries)
        
        final_prompt = (
            "You are a textbook editor. I am providing you with multiple detailed summary sections from different parts of the same lecture. "
            "Your task is to integrate them into a single, cohesive, and logically structured textbook chapter.\n\n"
            "REQUIREMENTS:\n"
            "1. Create deep transitions between sections to form a unified narrative.\n"
            "2. Ensure consistent terminology throughout the document.\n"
            "3. Clean up any redundant introductions or conclusions from the individual segments.\n"
            "4. Organize with clear, descriptive headers.\n"
            f"Language: {language}\n\n"
            "--- SEGMENT SUMMARIES TO INTEGRATE ---\n"
            f"{combined_summary}\n\n"
            "--- END OF DATA ---"
        )
        
        final_response = self.model.generate_content(final_prompt)
        return final_response.text

if __name__ == "__main__":
    # Test stub (requires API key in .env)
    summarizer = Summarizer()
    # test_output = summarizer.generate_summary("Transcribed text here...", "Slide text here...")
    # print(test_output)
