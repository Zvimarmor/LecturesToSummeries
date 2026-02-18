import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

class AudioProcessor:
    def __init__(self, silence_threshold=-40.0, min_silence_len=1000, keep_silence=100):
        """
        Initialize the AudioProcessor with default thresholds.
        
        :param silence_threshold: The upper bound for how quiet is considered silence (in dBFS).
        :param min_silence_len: The minimum length of silence to be considered a 'break' (in ms).
        :param keep_silence: Amount of silence to keep around the trimmed audio (in ms).
        """
        self.silence_threshold = silence_threshold
        self.min_silence_len = min_silence_len
        self.keep_silence = keep_silence

    def detect_breaks(self, audio_path):
        """
        Detects silent breaks in the audio file.
        Returns a list of tuples (start_ms, end_ms) for non-silent chunks.
        """
        print(f"Loading audio from {audio_path}...")
        audio = AudioSegment.from_file(audio_path)
        
        print("Detecting non-silent chunks...")
        nonsilent_chunks = detect_nonsilent(
            audio,
            min_silence_len=self.min_silence_len,
            silence_thresh=self.silence_threshold
        )
        
        return nonsilent_chunks, audio

    def trim_breaks(self, audio_path, output_path=None):
        """
        Trims the breaks (silence/low volume) and merges the remaining audio.
        """
        nonsilent_chunks, audio = self.detect_breaks(audio_path)
        
        if not nonsilent_chunks:
            print("No significant audio detected (mostly silence).")
            return None

        print(f"Found {len(nonsilent_chunks)} non-silent sections. Merging...")
        
        trimmed_audio = AudioSegment.empty()
        for start, end in nonsilent_chunks:
            # Add some padding around the chunks
            padded_start = max(0, start - self.keep_silence)
            padded_end = min(len(audio), end + self.keep_silence)
            trimmed_audio += audio[padded_start:padded_end]

        if output_path:
            trimmed_audio.export(output_path, format=os.path.splitext(output_path)[1][1:])
            print(f"Trimmed audio saved to {output_path}")
        
        return trimmed_audio

if __name__ == "__main__":
    # Quick test if run directly
    import sys
    if len(sys.argv) > 1:
        processor = AudioProcessor()
        processor.trim_breaks(sys.argv[1], "trimmed_output.mp3")
    else:
        print("Usage: python audio_processor.py <path_to_audio>")
