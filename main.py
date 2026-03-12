from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
from functools import lru_cache
import yt_dlp
import time

# ----------------------------
# INIT
# ----------------------------

ytmusic = YTMusic()

app = FastAPI(
    title="Krishan Music API",
    description="🎵 High performance music API for bots and websites\nMade with ❤️ by Krishan",
    version="3.0"
)

# ----------------------------
# CORS
# ----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# RATE LIMIT
# ----------------------------

rate_limit = {}

def check_rate_limit(ip):

    now = time.time()

    if ip in rate_limit:
        if now - rate_limit[ip] < 2:
            raise HTTPException(status_code=429, detail="Too many requests")

    rate_limit[ip] = now


# ----------------------------
# HOME
# ----------------------------

@app.get("/")
@app.head("/")
def home():

    return {
        "status": "online",
        "api": "Krishan Music API",
        "version": "3.0",
        "developer": "Krishan",
        "message": "Welcome to Krishan Music API 🎧",
        "endpoints": {
            "search": "/search?query=song name",
            "stream": "/stream/{video_id}",
            "lyrics": "/lyrics/{video_id}",
            "suggestions": "/suggestions/{video_id}"
        }
    }


# ----------------------------
# PING
# ----------------------------

@app.get("/ping")
def ping():
    return {"status": "success", "message": "API alive", "developer": "Krishan"}


# ----------------------------
# SEARCH CACHE
# ----------------------------

@lru_cache(maxsize=200)
def cached_search(query):

    return ytmusic.search(query, filter="songs")


# ----------------------------
# SEARCH
# ----------------------------

@app.get("/search")

def search_music(request: Request, query: str = Query(..., min_length=1)):

    check_rate_limit(request.client.host)

    try:

        data = cached_search(query)

        return {
            "status": "success",
            "developer": "Krishan",
            "results": len(data),
            "data": data
        }

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# STREAM (yt-dlp)
# ----------------------------

@app.get("/stream/{video_id}")

def stream_audio(request: Request, video_id: str):

    check_rate_limit(request.client.host)

    try:

        url = f"https://music.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "nocheckcertificate": True,
            "noplaylist": True,
            "extract_flat": False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)

            audio_url = info["url"]

        return {
            "status": "success",
            "developer": "Krishan",
            "stream_url": audio_url
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Stream extraction failed: {str(e)}"
        )


# ----------------------------
# SUGGESTIONS
# ----------------------------

@app.get("/suggestions/{video_id}")

def get_suggestions(request: Request, video_id: str):

    check_rate_limit(request.client.host)

    try:

        data = ytmusic.get_watch_playlist(videoId=video_id, limit=15)

        return {
            "status": "success",
            "developer": "Krishan",
            "data": data["tracks"]
        }

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# LYRICS
# ----------------------------

@app.get("/lyrics/{video_id}")

def get_lyrics(request: Request, video_id: str):

    check_rate_limit(request.client.host)

    try:

        watch_data = ytmusic.get_watch_playlist(videoId=video_id)

        lyrics_id = watch_data.get("lyrics")

        if not lyrics_id:

            return {
                "status": "error",
                "message": "Lyrics not available"
            }

        lyrics_data = ytmusic.get_lyrics(browseId=lyrics_id)

        return {
            "status": "success",
            "developer": "Krishan",
            "lyrics": lyrics_data["lyrics"]
        }

    except Exception:

        return {
            "status": "error",
            "message": "Lyrics fetch failed"
        }
