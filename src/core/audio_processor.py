import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

class AudioProcessor:
    def __init__(self, silence_threshold=-32.0, min_silence_len=60000, keep_silence=1000, relative_offset=-1.5):
        """
        Initialize the AudioProcessor with thresholds.
        
        :param silence_threshold: The fixed upper bound (in dBFS) IF relative_offset is None.
        :param min_silence_len: The minimum length of silence to be considered a 'break' (in ms).
        :param keep_silence: Amount of silence to keep around the trimmed audio (in ms).
        :param relative_offset: If provided, silence_threshold = audio.dBFS + relative_offset.
        """
        self.silence_threshold = silence_threshold
        self.min_silence_len = min_silence_len
        self.keep_silence = keep_silence
        self.relative_offset = relative_offset

    def detect_breaks(self, audio_path):
        """
        Detects breaks in the audio file using a windowed RMS approach.
        This is more robust than simple silence detection as it ignores short spikes.
        """
        print(f"Loading audio from {audio_path}...")
        audio = AudioSegment.from_file(audio_path)
        
        # Calculate dynamic threshold if requested
        file_rms = audio.dBFS
        thresh = self.silence_threshold
        if self.relative_offset is not None:
            thresh = file_rms + self.relative_offset
            print(f"File Avg dBFS: {file_rms:.2f}. Using relative threshold: {thresh:.2f} dBFS (offset={self.relative_offset})")
        else:
            print(f"Using fixed threshold: {thresh:.2f} dBFS")

        print(f"Analyzing audio in windows of 1 second...")
        # Step 1: Calculate RMS for each 1-second segment
        # We'll use 1-second segments for granularity
        segment_len = 1000 # ms
        rms_values = []
        for i in range(0, len(audio), segment_len):
            chunk = audio[i:i+segment_len]
            rms_values.append(chunk.dBFS)

        # Step 2: Smoothing/Filtering (Simple Moving Average or Median-like logic)
        # We want to find long regions where RMS is consistently low.
        # Let's look for segments of 'min_silence_len' where the MOST of the windows are below thresh.
        print(f"Identifying breaks (min_silence_len={self.min_silence_len}ms)...")
        
        # Simplified: Marks windows below threshold
        below_thresh = [1 if r < thresh else 0 for r in rms_values]
        
        # Find contiguous blocks of '1's that exceed min_silence_len
        min_windows = self.min_silence_len // segment_len
        
        silent_ranges_ms = []
        start_idx = None
        for i, val in enumerate(below_thresh):
            if val == 1:
                if start_idx is None:
                    start_idx = i
            else:
                if start_idx is not None:
                    duration = i - start_idx
                    if duration >= min_windows:
                        silent_ranges_ms.append((start_idx * segment_len, i * segment_len))
                    start_idx = None
        
        if start_idx is not None:
            duration = len(below_thresh) - start_idx
            if duration >= min_windows:
                silent_ranges_ms.append((start_idx * segment_len, len(below_thresh) * segment_len))

        # We return NON-SILENT chunks (the lectures)
        nonsilent_chunks = []
        last_end = 0
        for b_start, b_end in silent_ranges_ms:
            if b_start > last_end:
                nonsilent_chunks.append((last_end, b_start))
            last_end = b_end
        if last_end < len(audio):
            nonsilent_chunks.append((last_end, len(audio)))

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
            # Use lower quality for faster export if it's just for transcription
            trimmed_audio.export(output_path, format=os.path.splitext(output_path)[1][1:])
            print(f"Trimmed audio saved to {output_path}")
        
        return trimmed_audio, nonsilent_chunks

if __name__ == "__main__":
    # Quick test if run directly
    import sys
    if len(sys.argv) > 1:
        processor = AudioProcessor()
        processor.trim_breaks(sys.argv[1], "trimmed_output.mp3")
    else:
        print("Usage: python audio_processor.py <path_to_audio>")
