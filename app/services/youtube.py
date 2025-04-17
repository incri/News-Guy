from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from app.config import get_settings
from typing import List, Dict, Optional

settings = get_settings()


class YouTubeService:
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)

    def get_latest_videos(self, max_results: int = 5) -> List[Dict]:
        """Fetch latest videos from the channel."""
        request = self.youtube.search().list(
            part="snippet",
            channelId=settings.channel_id,
            maxResults=max_results,
            order="date",
            type="video",
        )
        response = request.execute()
        return response.get("items", [])

    def get_video_details(self, video_id: str) -> Dict:
        """Get detailed information about a specific video."""
        request = self.youtube.videos().list(part="snippet,contentDetails", id=video_id)
        response = request.execute()
        return response.get("items", [{}])[0]

    def get_captions(self, video_id: str) -> Optional[str]:
        """Get captions for a video."""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([entry["text"] for entry in transcript])
        except Exception as e:
            print(f"Error fetching captions: {e}")
            return None
