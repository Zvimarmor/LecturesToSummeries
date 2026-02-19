# LecturesToSummaries

**LecturesToSummaries** is a powerful tool designed to transform lecture recordings and slides into high-quality, study-ready summaries. By combining audio transcription (Whisper) with slide text extraction (PDF/PPTX) and advanced LLM summarization (Gemini), it generates explanations that are comprehensive and easy to study from.

## Features

- **Multimodal Input**: Accepts audio recordings (`.mp3`, `.wav`), lecture slides (`.pdf`, `.pptx`), or both.
- **Smart Audio Processing**: Automatically detects and trims silence/breaks in recordings to optimize processing.
- **Whisper Transcription**: High-accuracy Speech-to-Text support for both **English** and **Hebrew**.
- **Context-Aware Summaries**: Uses slide content to ground the summary in the actual course material.
- **Multiple Summary Styles**:
    - **Normal**: Structured, balanced review (Default)
    - **Informative**: Textbook-style deep dive
    - **Brief**: Cheat-sheet / Memory joggers

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Zvimarmor/LecturesToSummeries.git
    cd LecturesToSummeries
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```bash
    GEMINI_API_KEY=your_api_key_here
    ```

## Usage

Run the tool via the command line:

```bash
# Full pipeline (Audio + Slides)
python main.py --audio "recording.mp3" --materials "slides.pdf" --lang hebrew

# Audio only (Transcription + Summary)
python main.py --audio "recording.mp3" --lang english

# Slides only (Study notes from materials)
python main.py --materials "presentation.pptx" --type informative
```

### Options

| Flag | Description |
| :--- | :--- |
| `--audio` | Path to the audio file |
| `--materials`| Path to the slide deck (PDF or PPTX) |
| `--type` | Summary style: `normal`, `brief`, or `informative` |
| `--lang` | Target language: `english` or `hebrew` |
| `--trim` | Enable automatic silence trimming for audio |
| `--output` | Custom path for the output `.md` file |

## Requirements

- Python 3.10+
- FFmpeg (required by `pydub` and `whisper` for audio processing)
- Google Gemini API Key

## License

Personal Project.
