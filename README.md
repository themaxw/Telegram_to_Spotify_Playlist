# Playlist Adder Bot
This Bot adds all spotify tracks sent into a telegram group to a playlist

## Configuration
All important configuration is performed in the config file `config.yml`

```yaml
telegram_token: BOT_TOKEN
chat_ids: # list of allowed chats
  - 123450
default_playlist: SPOTIFY_ID_OF_PLAYLIST

spotify_client_id: SPOTIFY_CLIENT_ID
spotify_client_secret: SPOTIFY_CLIENT_SECRET

```