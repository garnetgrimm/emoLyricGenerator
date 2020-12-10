from bs4 import BeautifulSoup
import requests
import urllib.request as urllib2
import json

import argparse

def getSongsFromWeb(download_list, api_token, download_dir):
    with open(download_list) as file:
        for song in file:
            getSongFromWeb(song.strip(), api_token, download_dir)

def getSongFromWeb(search_term, api_token, download_dir):
    print("downloading:", search_term, end="")
    _URL_API = "https://api.genius.com/"
    _URL_SEARCH = "search?q="
    querystring = _URL_API + _URL_SEARCH + urllib2.quote(search_term)
    request = urllib2.Request(querystring)
    client_access_token = api_token
    request.add_header("Authorization", "Bearer " + client_access_token)
    request.add_header("User-Agent", "")
    response = urllib2.urlopen(request, timeout=3)
    print(".",end="")
    encoding = response.info().get_content_charset('utf-8')
    json_obj = json.loads(response.read().decode(encoding))
    song_info = json_obj['response']['hits'][0]['result']
    page = requests.get(song_info['url'])
    html = BeautifulSoup(page.text, "html.parser")
    lyrics = html.find("div", class_="lyrics").get_text()
    song_info = json_obj['response']['hits'][0]['result']
    song_title = song_info['title'].lower().replace(" ", "-")
    song_artist = song_info['primary_artist']['name'].lower().replace(" ", "-")
    print(".",end="")
    with open(download_dir + '/' + song_artist + "." + song_title, 'w') as file:
        file.write(lyrics)
    print(".",end="")
    print("done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--download_list', help='Location of song download list, defaults to downloadList.txt')
    parser.add_argument('--api_token', help='API key for genius lyrics, used only in download mode ( https://genius.com/api-clients )')
    parser.add_argument('--download_dir', help='Where to place/find downloaded songs, defaults to lyrics/')
    args = parser.parse_args()
    getSongsFromWeb(args.download_list, args.api_token, args.download_dir)
