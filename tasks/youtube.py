import json
import urllib
import requests


def get_youtube_id(artist, title):
    token = "AIzaSyBK4klykt4Crt26v4wDixYN4exwXdjFBn8"
    search_req = urllib.parse.quote_plus(f"{artist} {title}")
    url = (f"https://www.googleapis.com/youtube/v3/search"
           f"?part=snippet&maxResults=1&q={search_req}&key={token}")
    response = requests.get(url)
    data = json.loads(response.text)
    print(f'Updated. youtube_id: {data["items"][0]["id"]["videoId"]}, {artist} - {title}')
    return data["items"][0]["id"]["videoId"]
