from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi import HTTPException
from app.config import Config


class YouTubeService:
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=Config.YOUTUBE_API_KEY)

    def get_latest_video_id(self, channel_id: str = "@Fireship") -> str:
        try:
            channel_response = (
                self.youtube.search()
                .list(part="snippet", q=channel_id, type="channel", maxResults=1)
                .execute()
            )

            if not channel_response["items"]:
                raise HTTPException(status_code=404, detail="Channel not found")

            channel_id = channel_response["items"][0]["id"]["channelId"]

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

    def get_video_info(self, video_id: str) -> dict:
        try:
            response = self.youtube.videos().list(part="snippet", id=video_id).execute()

            if not response["items"]:
                return {}

            video = response["items"][0]
            return {
                "title": video["snippet"]["title"],
                "published_at": video["snippet"]["publishedAt"],
            }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}

    def get_transcript(self, video_id: str) -> list:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
