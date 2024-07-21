from spotify import PlaylistAdder
import yaml

import json
from urllib.parse import urlparse
from pathlib import Path

telegram_export_file = Path("PATH/TO/TELEGRAM/EXPORT/results.json")
group_name = "GROUPNAME"

if __name__ == "__main__":
    with open(telegram_export_file) as f:
        data = json.load(f)

    track_urls = []
    shortlink_urls = []
    for chat in data["chats"]["list"]:
        if chat["name"] == group_name:
            for message in chat["messages"]:
                if "text_entities" not in message:
                    continue

                for entity in message["text_entities"]:
                    if entity["type"] != "link":
                        continue
                    url = entity["text"]
                    o = urlparse(url)
                    if o.hostname == "open.spotify.com" and o.path.startswith("/track"):
                        track_urls.append(o.path[len("/track/") :])

                    elif o.hostname == "spotify.link":
                        shortlink_urls.append(url)

    track_urls = list(set(track_urls))

    with open(Path(__file__).parent / "config.yml") as f:
        conf = yaml.safe_load(f)

    pa = PlaylistAdder(
        conf["spotify_client_id"],
        conf["spotify_client_secret"],
        conf["default_playlist"],
    )
    for tracks in [track_urls[x : x + 30] for x in range(0, len(track_urls), 30)]:

        pa.user.playlist_add_items(conf["default_playlist"], tracks)
    # track_uris = []
    # print(len(shortlink_urls))

    # for track in shortlink_urls:
    #     print(track)
    #     sp_tracks = pa.sp.track(track)
    #     track_uris.append(sp_tracks["uri"])
    # print(shortlink_urls)
    # print(track_uris)
