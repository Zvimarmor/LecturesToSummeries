import os
import argparse
from src.core.audio_processor import AudioProcessor
from src.core.transcriber import Transcriber
from src.core.material_parser import MaterialParser
from src.core.summarizer import Summarizer

def main():
    parser = argparse.ArgumentParser(description="LecturesToSummaries: Generate lecture summaries from audio and slides.")
    
    # Arguments
    parser.add_argument("--audio", help="Path to the lecture audio file")
    parser.add_argument("--materials", help="Path to lecture materials (PDF or PPTX)")
    parser.add_argument("--type", choices=["informative", "brief", "normal"], default="normal", help="Summary type")
    parser.add_argument("--lang", choices=["english", "hebrew"], default="english", help="Lecture language")
    parser.add_argument("--trim", action="store_true", help="Enable break detection and trimming")
    parser.add_argument("--output", help="Path to save the summary (Markdown)")
    parser.add_argument("--import_transcript", help="Path to a saved transcript JSON file to skip transcription")
    
    args = parser.parse_args()

    # Validation: Need at least one source
    if not args.audio and not args.materials:
        parser.error("You must provide at least one source: --audio or --materials")

    # 1. Audio Processing (Trimming)
    transcript_text = ""
    transcript_segments = []
    source_name = "lecture"
    nonsilent_chunks = []
    
    if args.audio:
        source_name = os.path.basename(args.audio).split('.')[0]
        audio_to_transcribe = args.audio
        if args.trim:
            print("--- Phase 1: Trimming Audio ---")
            processor = AudioProcessor()
            trimmed_path = f"data/recordings/trimmed_{os.path.basename(args.audio)}"
            if not os.path.exists("data/recordings"):
                os.makedirs("data/recordings")
            _, nonsilent_chunks = processor.trim_breaks(args.audio, trimmed_path)
            audio_to_transcribe = trimmed_path

        if args.import_transcript:
            import json
            print(f"--- Loading Transcript from {args.import_transcript} ---")
            with open(args.import_transcript, "r", encoding="utf-8") as f:
                transcript_data = json.load(f)
            transcript_text = transcript_data["text"]
        else:
            # 2. Transcription
            print("--- Phase 1.5: Transcribing ---")
            transcriber = Transcriber(model_name="base")
            lang_code = "he" if args.lang == "hebrew" else "en"
            transcript_data = transcriber.transcribe(audio_to_transcribe, language=lang_code)
            transcript_text = transcript_data["text"]
            
            # Save for future resume
            if not os.path.exists("outputs"):
                os.makedirs("outputs")
            import json
            with open(f"outputs/transcript_metadata_{source_name}.json", "w", encoding="utf-8") as f:
                json.dump(transcript_data, f, indent=2)
        
        # If we have multiple chunks and want informative summary, split transcript
        if (args.trim or args.import_transcript) and args.type == "informative":
            # We need nonsilent_chunks for splitting. 
            # If we don't have them (e.g. from resume), we might need to recalculate them if audio is available
            if not nonsilent_chunks:
                 processor = AudioProcessor()
                 nonsilent_chunks, _ = processor.detect_breaks(args.audio)
            
            if len(nonsilent_chunks) > 1:
                print(f"Splitting transcript into {len(nonsilent_chunks)} segments...")
                seg_texts = ["" for _ in nonsilent_chunks]
                chunk_durations = [(e - s) / 1000.0 for s, e in nonsilent_chunks]
                
                for seg in transcript_data["segments"]:
                    seg_mid_time = (seg["start"] + seg["end"]) / 2.0
                    temp_cum = 0
                    for i, dur in enumerate(chunk_durations):
                        if seg_mid_time <= temp_cum + dur or i == len(chunk_durations) - 1:
                            seg_texts[i] += seg["text"] + " "
                            break
                        temp_cum += dur
                
                transcript_segments = [t.strip() for t in seg_texts if t.strip()]
    
    # 3. Material Parsing
    materials_text = ""
    if args.materials:
        if not args.audio:
            source_name = os.path.basename(args.materials).split('.')[0]
        print("--- Phase 2: Parsing Materials ---")
        parser_tool = MaterialParser()
        materials_text = parser_tool.parse_material(args.materials)

    # 4. Summarization
    print("--- Phase 3: Summarizing ---")
    summarizer = Summarizer()
    
    if args.type == "informative" and transcript_segments:
        summary = summarizer.generate_informative_summary(
            transcript_segments,
            materials_text,
            language=args.lang
        )
    else:
        summary = summarizer.generate_summary(
            transcript_text, 
            materials_text, 
            summary_type=args.type, 
            language=args.lang
        )

    # 5. Save Output
    output_path = args.output or f"outputs/summary_{source_name}.md"
    transcript_path = f"outputs/transcript_{source_name}.txt"
    
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        
    # Save Transcript
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    print(f"Transcript saved to: {transcript_path}")

    # Save Summary
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Lecture Summary: {source_name}\n\n")
        f.write(f"**Type:** {args.type.capitalize()}\n")
        f.write(f"**Language:** {args.lang.capitalize()}\n\n")
        f.write("## Summary\n")
        f.write(summary)

    print(f"\n--- SUCCESS ---")
    print(f"Summary saved to: {output_path}")

if __name__ == "__main__":
    main()
