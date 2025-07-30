import requests
import os

def search_youtube_videos(query, api_key=None, max_results=1):
    """
    Search YouTube for videos matching the query and return a list of video URLs. Defaults to 1 video per query.
    """
    if api_key is None:
        api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        return []
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        video_urls = [
            f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            for item in data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]
        return video_urls[:1]
    except Exception as e:
        return []
