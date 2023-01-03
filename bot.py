# Copyright ©️ 2023 Sanila Ranatunga. All Rights Reserved
# You are free to use this code in any of your project, but you MUST include the following in your README.md (Copy & paste)
# ##Credits - [Telegram-Lyrics-Bot](https://github.com/sanila2007/telegram-lyrics-bot)

# Read GNU General Public License v3.0: https://github.com/sanila2007/telegram-lyrics-bot/blob/mai/LICENSE
# Don't forget to follow github.com/sanila2007 because I am doing these things for free and open source
# Star, fork, enjoy!

import os
import lyricsgenius
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from requests.exceptions import Timeout, HTTPError
from pyrogram.errors import MessageTooLong
from config import Config

bot = Client(
    "bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

GENIUS = lyricsgenius.Genius(Config.TOKEN)


@bot.on_message(filters.command("start") & filters.private)
async def start(bot, message):
    await bot.send_message(message.chat.id, f"Hello **{message.from_user.first_name}**!!\n\nWelcome to Lyrics bot."
                                            f"You can get lyrics of any song which is on Genius.com using this bot. Just"
                                            f" send the name of the song that you want to get lyrics. This is"
                                            f" quite simple.", reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔍Search inline...", switch_inline_query_current_chat="")
            ]
        ]
    ))


@bot.on_message(filters.text & filters.private)
async def lyric_get(bot, message):
    try:
        m = await message.reply(
            "🔍Searching..."
        )
        song_name = message.text
        LYRICS = GENIUS.search_song(song_name)
        if LYRICS is None:
            await m.edit_text(
                "❌Oops\nFound no result"
            )
        global TITLE
        global ARTISTE
        global TEXT
        TITLE = LYRICS.title
        ARTISTE = LYRICS.artist
        TEXT = LYRICS.lyrics
    except Timeout:
        pass
    except HTTPError as https_e:
        print(https_e)
    try:
        await m.edit_text(
            f"🎶Song Name: **{TITLE}**\n🎙️Artiste: **{ARTISTE}**\n\n`{TEXT}`", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔍Search for lyrics...", switch_inline_query_current_chat="")
                    ]
                ]
            )
        )
    except MessageTooLong:
        with open(f'downloads/{TITLE}.txt', 'w') as file:
            file.write(f'{TITLE}\n{ARTISTE}\n\n{TEXT}')
            await m.edit_text(
                "Changed into a text file because the text is too long..."
            )
            await bot.send_document(message.chat.id, document=f'downloads/{TITLE}.txt', caption=f'\n{TITLE}\n{ARTISTE}')
            os.remove(f'downloads/{TITLE}.txt')


@bot.on_inline_query()
async def inlinequery(client, inline_query):
    answer = []
    if inline_query.query == "":
        await inline_query.answer(
            results=[

                InlineQueryResultArticle(
                    title="Search to get lyrics...",
                    description="Lyrics bot",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("🔍Search for Lyrics..", switch_inline_query_current_chat="")
                            ]
                        ]
                    ),
                    input_message_content=InputTextMessageContent(
                        "Search for lyrics inline..."
                    )
                )
            ]
        )
    else:
        INLINE_SONG = inline_query.query
        print(INLINE_SONG)
        INLINE_LYRICS = GENIUS.search_song(INLINE_SONG)
        INLINE_TITLE = INLINE_LYRICS.title
        INLINE_ARTISTE = INLINE_LYRICS.artist
        INLINE_TEXT = INLINE_LYRICS.lyrics
        answer.append(
            InlineQueryResultArticle(
                title=INLINE_TITLE,
                description=INLINE_ARTISTE,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("❌Wrong result?", switch_inline_query_current_chat=INLINE_SONG),
                            InlineKeyboardButton("🔍Search again..", switch_inline_query_current_chat="")
                        ]
                    ]
                ),
                input_message_content=InputTextMessageContent(f"**Inline lyrics result...**\n\n🎶Name: **{INLINE_TITLE}**\n🎙️Artiste: **{INLINE_ARTISTE}**\n\n`{INLINE_TEXT}`")
            )
        )
    await inline_query.answer(
        results=answer,
        cache_time=1
    )


print("Lyric bot is online")
bot.run()
