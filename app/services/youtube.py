from googleapiclient.discovery import build
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from typing import Dict, List, Optional
from datetime import datetime
from app.core.settings import get_settings
from app.models.schemas import VideoInfo, CaptionItem
from fastapi import HTTPException

settings = get_settings()


class YouTubeService:
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    async def get_latest_video_id(self, channel_id: str = "@Fireship") -> str:
        """Get the latest video ID from a YouTube channel."""
        try:
            # Get channel ID from handle
            channel_response = (
                self.youtube.search()
                .list(part="snippet", q=channel_id, type="channel", maxResults=1)
                .execute()
            )

            if not channel_response["items"]:
                raise HTTPException(status_code=404, detail="Channel not found")

            channel_id = channel_response["items"][0]["id"]["channelId"]

            # Get latest video
            video_response = (
                self.youtube.search()
                .list(
                    part="snippet",
                    channelId=channel_id,
                    order="date",
                    type="video",
                    maxResults=1,
                )
                .execute()
            )

            if not video_response["items"]:
                raise HTTPException(status_code=404, detail="No videos found")

            return video_response["items"][0]["id"]["videoId"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_video_info(self, video_id: str) -> VideoInfo:
        """Get video information from YouTube API."""
        try:
            response = self.youtube.videos().list(part="snippet", id=video_id).execute()

            if not response["items"]:
                raise HTTPException(status_code=404, detail="Video not found")

            video = response["items"][0]
            return VideoInfo(
                video_id=video_id,
                title=video["snippet"]["title"],
                published_at=datetime.fromisoformat(
                    video["snippet"]["publishedAt"].replace("Z", "+00:00")
                ),
                channel_id=video["snippet"]["channelId"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_transcript(self, video_id: str) -> List[CaptionItem]:
        """Get video transcript with proper error handling."""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return [
                CaptionItem(
                    text=item["text"], start=item["start"], duration=item["duration"]
                )
                for item in transcript
            ]
        except TranscriptsDisabled:
            raise HTTPException(
                status_code=404, detail="Transcripts are disabled for this video"
            )
        except NoTranscriptFound:
            raise HTTPException(
                status_code=404, detail="No transcript found for this video"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


youtube_service = YouTubeService()
