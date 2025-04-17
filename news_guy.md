### **🎯 Goal**

Automatically fetch new videos from [Fireship YouTube Channel](https://www.youtube.com/@Fireship), extract captions/subtitles, store them in a database, and make that data queryable inside Cursor IDE using a Gemini-powered assistant, following the Model Context Protocol (MCP).

---

## **✅ Key Components (Corrected \+ Structured)**

### **1\. YouTube Video Fetching**

* **On-Demand Fetching**:
  * Use **YouTube Data API v3** to get the latest videos (requires an API key)
  * Fetch happens only when user makes a query
  * No background polling or scheduling needed

### **2\. Extract Captions/Subtitles**

* ✅ If the video has captions (auto-generated or uploaded), use:
  * `youtube_transcript_api` (Python library) — reliable and easy
  * Fallback: Download video with `yt-dlp` and extract subs
* ❌ Note: Not all videos have good captions; handle missing ones

### **3\. Store in a Database**

* ✅ Use **SQLite** for local development and simplicity
* Store:
  * `video_id`, `title`, `publishedAt`, `description`, `captions`, `link`, maybe `tags`

### **4\. Serve API Endpoints**

* ✅ Use **FastAPI** (recommended) or Flask to expose endpoints like:
  * `GET /videos`: list all videos
  * `GET /video/{id}`: get full captions
  * `POST /query`: ask questions about videos (see below)

### **5\. Embed into Vector DB**

* ✅ Process and chunk captions
* ✅ Use **FAISS** to store vector embeddings of captions
* Use Gemini embedding model or another one compatible with your workflow

### **6\. Query via Gemini \+ MCP**

* ✅ Wrap Gemini API with your **MCP logic**
* When user types a query (e.g., "What's new with Fireship?"):
  * Fetch latest videos from YouTube API
  * Extract and store captions in SQLite
  * Generate and store embeddings in FAISS
  * Retrieve relevant chunks from FAISS
  * Use Gemini to answer, with retrieval + generation
  * Return answers in Cursor IDE

---

## **🧠 MCP Integration Suggestion**

Since you're experimenting with **Model Context Protocol**, define:

```json
{
  "context": [
    { "source": "video_caption", "content": "..." }
  ],
  "query": "Summarize what the latest video said about AI tools"
}
```

Let MCP layer handle:
* Context injection from caption DB
* Gemini API routing
* Metadata tagging (source = Fireship, type = YouTube, topic = AI)

---

## **🧪 IDE (Cursor) Integration**

You can:
* Add a **custom command or extension** inside Cursor to send a query to your backend
* Get answers injected inline or as Markdown

If you go CLI-based:
```bash
fireship-news "what's new with AI?"
```

Or build a **Cursor plugin** (Cursor supports `devtools`, it's open to customization).

---

## **✅ MVP Plan (Checklist)**

| Task | Tool/Stack | Status |
| ----- | ----- | ----- |
| ✅ Get Fireship video list | YouTube API v3 | 🔲 |
| ✅ Fetch captions/subtitles | `youtube_transcript_api` | 🔲 |
| ✅ Store video+captions | SQLite | 🔲 |
| ✅ Expose REST API | FastAPI | 🔲 |
| ✅ Store + embed captions | FAISS | 🔲 |
| ✅ MCP protocol interface | Custom JSON schema | 🔲 |
| ✅ LLM query + response | Gemini Pro | 🔲 |
| ✅ Cursor IDE access | CLI or Cursor plugin | 🔲 |

---

## **🛠 Stack Recommendation**

| Layer | Tech |
| ----- | ----- |
| 🧠 LLM | Gemini API |
| 🔍 Vector DB | FAISS |
| 🗃 DB | SQLite |
| 🌐 API Server | FastAPI |
| 🎞 YouTube API | YouTube Data API v3 |
| 🧪 Subtitles | `youtube_transcript_api` |
| 🖥 Cursor IDE | Plugin or CLI |
| 🧠 MCP | Custom layer on top of query system |

---

## **🚨 Caveats to Keep in Mind**

1. **YouTube API limits** — 10,000 units/day (1 search = 100 units)
2. **Not all videos have captions**
3. **Gemini token usage** — monitor usage and cost
4. **Embedding Model** — you can use Gemini's if available or OpenAI if hybrid
5. **Privacy** — Be cautious if you store/transmit user queries

---

## **🚀 Suggestions to Make it Better Later**

* Add **topic tagging** (e.g., AI, Web Dev, etc.)
* Add **summaries** for each video
* Make it **multi-channel** (e.g., Theo, Fireship, etc.)
* Add **notifications** when a new video matches your interest (LangChain, AI, etc.)

