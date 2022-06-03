from bs4 import BeautifulSoup
from random import randint
import requests
import json

def getYoutubeVideo(search):
    URL = f"https://www.youtube.com/results?search_query={search}"

    result = requests.get(URL)
    result.encoding = "utf8"
    data = BeautifulSoup(result.text,'html.parser')
    for i in data.find_all('script'):
        text = str(i)
        spt = text.split()
        if spt[2] == "ytInitialData":
            j = 0
            
            while text[j] != "{":
                j += 1
            start = j
            # f.write(text[start:-10])
            video = json.loads(text[start:-10])

    content = video["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

    video_result = []
    for i in content:
        if "videoRenderer" in i:
            renderer = i['videoRenderer']
            video_result.append({
                "url": f"https://www.youtube.com/watch?v={renderer['videoId']}",
                "title": renderer["title"]["runs"][0]["text"]
            })

    return video_result