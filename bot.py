import asyncio
from telegram import ReactionType, ReactionTypeEmoji, Update, Message
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)
from telegram.ext.filters import Entity
from telegram.constants import MessageEntityType, ReactionEmoji
import yaml
from pathlib import Path
import logging

from spotify import PlaylistAdder

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARN
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="hallo wie geht"
    )


async def url_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in allowed_chats:
        return
    got_spotify_track = False
    for entity in update.message.entities:
        url = None
        if entity.type == MessageEntityType.URL:
            url = Message.parse_entity(update.message, entity)

        elif entity.type == MessageEntityType.TEXT_LINK:
            url = entity.url

        if url is not None:
            print(url)
            got_spotify_track = playlistadder.add_to_playlist(url) or got_spotify_track
            # TODO check that link is spotify link
            # TODO add to playlist

    # reply_message = None
    # if update.message.is_topic_message:
    #     reply_message = update.message.message_thread_id
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text="got url",
    #     reply_to_message_id=reply_message,
    # )
    if got_spotify_track:
        await context.bot.set_message_reaction(
            update.effective_chat.id,
            update.message.id,
            ReactionTypeEmoji(ReactionEmoji.HUNDRED_POINTS_SYMBOL),
        )


if __name__ == "__main__":
    with open(Path(__file__).parent / "config.yml") as f:
        conf = yaml.safe_load(f)

    allowed_chats = conf["chat_ids"]

    playlistadder = PlaylistAdder(
        conf["spotify_client_id"],
        conf["spotify_client_secret"],
        conf["default_playlist"],
    )
    app = ApplicationBuilder().token(conf["telegram_token"]).build()

    url_handler = MessageHandler(
        Entity(MessageEntityType.URL) | Entity(MessageEntityType.TEXT_LINK),
        url_received,
    )
    app.add_handler(url_handler)

    app.run_polling()
