import whisper
import os

class Transcriber:
    def __init__(self, model_name="base", device=None):
        """
        Initialize the Transcriber with a specific Whisper model.
        :param model_name: 'tiny', 'base', 'small', 'medium', 'large'
        :param device: 'cpu' or 'cuda' (MPS for Mac)
        """
        print(f"Loading Whisper model '{model_name}'...")
        self.model = whisper.load_model(model_name, device=device)

    def transcribe(self, audio_path, language=None):
        """
        Transcribes the audio file.
        :param audio_path: Path to the audio file.
        :param language: Language code (e.g., 'en', 'he'). If None, Whisper will auto-detect.
        """
        print(f"Transcribing {audio_path}...")
        
        # task="transcribe" for speech-to-text in the original language
        # task="translate" for speech-to-text translated to English
        options = {}
        if language:
            options["language"] = language
            
        result = self.model.transcribe(audio_path, **options)
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"]
        }

    def save_transcript(self, transcript_data, output_path):
        """
        Saves the transcript text to a file.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript_data["text"])
        print(f"Transcript saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # For Mac with M-series chips, "mps" is better if supported, else "cpu"
        # For simplicity and broad compatibility, we'll let whisper decide or default to cpu.
        transcriber = Transcriber(model_name="base")
        
        lang = None
        if len(sys.argv) > 2:
            lang = sys.argv[2] # e.g. 'he' or 'en'
            
        result = transcriber.transcribe(sys.argv[1], language=lang)
        print(f"Detected language: {result['language']}")
        
        base_name = os.path.splitext(sys.argv[1])[0]
        transcriber.save_transcript(result, f"{base_name}_transcript.txt")
    else:
        print("Usage: python transcriber.py <path_to_audio> [language_code]")
