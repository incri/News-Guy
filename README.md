# News Guy

A system that fetches and processes Fireship YouTube videos, with a FastAPI MCP backend for AI-powered queries.

## FastAPI MCP Implementation

- **MCP Server**: Handles context and state for AI interactions
- **CLI Tools**: Directly interact with the MCP server from the command line
- **Pydantic Models**: Type-safe API contracts

### CLI Examples
```bash
newsguy query "What's new with Fireship?"
newsguy latest --format=json
```

## Development Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies using uv (faster alternative to pip):
```bash
uv pip install -e .
```

3. Configure environment variables:
```bash
echo "YOUTUBE_API_KEY=your_key" >> .env
echo "GEMINI_API_KEY=your_key" >> .env
```

4. Start the development server:
```bash
uvicorn app.main:app --reload
```

Note: The `pyproject.toml` contains all project dependencies and configuration.


## Features
- MCP context management
- CLI integration
- Video processing


## License
MIT

