
from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup
import config
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # from Koyeb env vars

app = Client(
    "filmyzilla_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.text)
def extract_links(client, message):
    url = message.text.strip()
    if "filmyzilla0.com/category/" not in url:
        message.reply("Please send a valid FilmyZilla category link.")
        return

    msg = message.reply("Scraping links, please wait...")

    try:
        res = requests.get(url, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        movie_links = [
            "https://www.filmyzilla0.com" + a["href"]
            for a in soup.select("a.d-flex.flex-row") if "/movies/" in a["href"]
        ]

        final_links = []

        for m_url in movie_links:
            m_res = requests.get(m_url, timeout=15)
            m_soup = BeautifulSoup(m_res.text, "html.parser")

            download_buttons = m_soup.select("a.btn.btn-light.btn-lg.btn-block")

            for btn in download_buttons:
                dlink = btn.get("href", "")
                if "/downloads/" in dlink:
                    dl_page = "https://www.filmyzilla0.com" + dlink
                    dl_res = requests.get(dl_page, timeout=15)
                    dl_soup = BeautifulSoup(dl_res.text, "html.parser")

                    for a in dl_soup.find_all("a", href=True):
                        href = a["href"]
                        if "workers.dev" in href and (".mkv" in href or ".mp4" in href):
                            filename = href.split("/")[-1]
                            final_links.append(f"**{filename}**
{href}
")
                            break

        if final_links:
            output = "
".join(final_links)
            msg.edit(output[:4096])
        else:
            msg.edit("No working links found.")
    except Exception as e:
        msg.edit(f"Error: {str(e)}")

app.run()
