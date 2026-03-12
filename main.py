from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ytmusicapi import YTMusic
import yt_dlp
import time
import random

# -----------------------------
# INIT
# -----------------------------

app = FastAPI(
    title="Krishan Music API",
    description="Music streaming API for bots & websites - Made by Krishan",
    version="7.0"
)

ytmusic = YTMusic()

# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# RATE LIMIT
# -----------------------------

rate_limit = {}

def check_rate(ip):

    now = time.time()

    if ip in rate_limit:
        if now - rate_limit[ip] < 3:
            raise HTTPException(429, "Too many requests")

    rate_limit[ip] = now


# -----------------------------
# HOME
# -----------------------------

@app.get("/")
def home():

    return {
        "status": "online",
        "api": "Krishan Music API",
        "developer": "Krishan",
        "version": "7.0",
        "endpoints": {
            "ping": "/ping",
            "search": "/search?query=song",
            "stream": "/stream/{video_id}"
        }
    }


# -----------------------------
# PING (UptimeRobot)
# -----------------------------

@app.get("/ping")
@app.head("/ping")
def ping():

    return JSONResponse(
        content={
            "status": "ok",
            "service": "Krishan Music API",
            "message": "pong"
        }
    )


# -----------------------------
# SEARCH SONG
# -----------------------------

@app.get("/search")
def search_song(query: str):

    try:

        results = ytmusic.search(query, filter="songs")

        return {
            "status": "success",
            "results": results
        }

    except Exception as e:

        raise HTTPException(500, str(e))


# -----------------------------
# STREAM (yt-dlp)
# -----------------------------

@app.get("/stream/{video_id}")
def stream(video_id: str, request: Request):

    check_rate(request.client.host)

    url = f"https://www.youtube.com/watch?v={video_id}"

    clients = [
        ("android", "com.google.android.youtube/17.36.4"),
        ("web", "Mozilla/5.0"),
        ("ios", "com.google.ios.youtube/17.33.2")
    ]

    for client, agent in clients:

        ydl_opts = {

            "quiet": True,
            "skip_download": True,
            "nocheckcertificate": True,
            "format": "bestaudio/best",

            "extractor_args": {
                "youtube": {
                    "player_client": [client]
                }
            },

            "http_headers": {
                "User-Agent": agent
            }
        }

        try:

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(url, download=False)

                stream_url = info["url"]

                return {
                    "status": "success",
                    "stream_url": stream_url
                }

        except Exception as e:

            print("retrying with next client:", e)

            time.sleep(random.uniform(2,5))

    raise HTTPException(
        status_code=500,
        detail="Stream extraction failed"
    )
