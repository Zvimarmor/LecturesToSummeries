import os
import argparse
from src.core.audio_processor import AudioProcessor
from src.core.transcriber import Transcriber
from src.core.material_parser import MaterialParser
from src.core.summarizer import Summarizer

def main():
    parser = argparse.ArgumentParser(description="LecturesToSummaries: Generate lecture summaries from audio and slides.")
    
    # Required arguments
    parser.add_argument("audio", help="Path to the lecture audio file")
    
    # Optional arguments
    parser.add_argument("--materials", help="Path to lecture materials (PDF or PPTX)")
    parser.add_argument("--type", choices=["informative", "brief", "normal"], default="normal", help="Summary type")
    parser.add_argument("--lang", choices=["english", "hebrew"], default="english", help="Lecture language")
    parser.add_argument("--trim", action="store_true", help="Enable break detection and trimming")
    parser.add_argument("--output", help="Path to save the summary (Markdown)")
    
    args = parser.parse_args()

    # 1. Audio Processing (Trimming)
    audio_to_transcribe = args.audio
    if args.trim:
        print("--- Phase 1: Trimming Audio ---")
        processor = AudioProcessor()
        trimmed_path = f"data/recordings/trimmed_{os.path.basename(args.audio)}"
        if not os.path.exists("data/recordings"):
            os.makedirs("data/recordings")
        processor.trim_breaks(args.audio, trimmed_path)
        audio_to_transcribe = trimmed_path

    # 2. Transcription
    print("--- Phase 2: Transcribing ---")
    transcriber = Transcriber(model_name="base")
    lang_code = "he" if args.lang == "hebrew" else "en"
    transcript_data = transcriber.transcribe(audio_to_transcribe, language=lang_code)
    
    # 3. Material Parsing
    materials_text = ""
    if args.materials:
        print("--- Phase 3: Parsing Materials ---")
        parser_tool = MaterialParser()
        materials_text = parser_tool.parse_material(args.materials)

    # 4. Summarization
    print("--- Phase 4: Summarizing ---")
    summarizer = Summarizer()
    summary = summarizer.generate_summary(
        transcript_data["text"], 
        materials_text, 
        summary_type=args.type, 
        language=args.lang
    )

    # 5. Save Output
    output_path = args.output or f"outputs/summary_{os.path.basename(args.audio).split('.')[0]}.md"
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Lecture Summary: {os.path.basename(args.audio)}\n\n")
        f.write(f"**Type:** {args.type.capitalize()}\n")
        f.write(f"**Language:** {args.lang.capitalize()}\n\n")
        f.write("## Summary\n")
        f.write(summary)

    print(f"\n--- SUCCESS ---")
    print(f"Summary saved to: {output_path}")

if __name__ == "__main__":
    main()
