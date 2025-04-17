# News Guy

A system that fetches and processes Fireship YouTube videos, making them queryable through a Gemini-powered assistant in Cursor IDE.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## Usage

1. Start the server
2. Use the Cursor IDE integration or CLI to query videos
3. Example queries:
   - "What's new with Fireship?"
   - "Tell me about the latest video on AI"
   - "What did Fireship say about Python?"

## Development

- Python 3.8+
- FastAPI for the backend
- SQLite for local storage
- FAISS for vector embeddings
- Gemini API for LLM capabilities 
