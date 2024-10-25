import requests

from src.utils.moosic_error import MoosicError
from src.utils.helpers import Helpers

class MoosicVideo:
    def __init__(self, data):
        self.data = data
        self.details = data["videoDetails"]

    def get_id(self):
        return self.details["videoId"]

    def get_title(self):
        return self.details["title"]

    def get_duration(self):
        return int(self.details["lengthSeconds"])

    def is_live(self):
        return True if self.data["videoDetails"].get("isLive") else False

    def get_thumbnail(self):
        return self.data["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]

    def get_audio_url(self, itag = 251):
        if not self.is_live():
            formats = self.data["streamingData"]["adaptiveFormats"]
            for i in reversed(formats):
                if i.get("itag") == itag:
                    return i.get("url")
            return formats[-1].get("url")
        else:
            return self.data["streamingData"]["hlsManifestUrl"] 

class MoosicGrabber:
    @staticmethod
    def request_yt(video_id):
        url = "https://www.youtube.com/youtubei/v1/player?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
        payload = {"videoId": video_id, "context" : {"client" : { "clientName" : "IOS", "clientVersion" : "19.29.1" }}}
        request = requests.post(url, json=payload)
        if request.status_code != 200:
            raise MoosicError("er_himalformed")
        return MoosicVideo(request.json())
