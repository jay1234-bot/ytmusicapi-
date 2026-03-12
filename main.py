from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
from pytube import YouTube
from functools import lru_cache
import time

ytmusic = YTMusic()

app = FastAPI(
    title="Krishan Music API",
    description="🎧 Music API for Telegram Bots & Websites\nMade with ❤️ by Krishan",
    version="5.0"
)

# ---------------------------
# CORS
# ---------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# RATE LIMIT
# ---------------------------

rate_limit = {}

def check_rate_limit(ip):

    now = time.time()

    if ip in rate_limit:
        if now - rate_limit[ip] < 2:
            raise HTTPException(status_code=429, detail="Too many requests")

    rate_limit[ip] = now


# ---------------------------
# HOME
# ---------------------------

@app.get("/")
def home():

    return {
        "status": "online",
        "api": "Krishan Music API",
        "version": "5.0",
        "developer": "Krishan",
        "message": "Welcome to Krishan Music API 🎵",
        "endpoints": {
            "search": "/search?query=song",
            "stream": "/stream/{video_id}"
        }
    }


# ---------------------------
# SEARCH CACHE
# ---------------------------

@lru_cache(maxsize=200)
def cached_search(query):

    return ytmusic.search(query, filter="songs")


# ---------------------------
# SEARCH
# ---------------------------

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


# ---------------------------
# STREAM USING PYTUBE
# ---------------------------

@app.get("/stream/{video_id}")

def stream_audio(request: Request, video_id: str):

    check_rate_limit(request.client.host)

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:

        yt = YouTube(url)

        stream = (
            yt.streams
            .filter(only_audio=True)
            .order_by("abr")
            .desc()
            .first()
        )

        if not stream:

            raise HTTPException(
                status_code=404,
                detail="Audio stream not found"
            )

        return {
            "status": "success",
            "developer": "Krishan",
            "stream_url": stream.url
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Stream failed: {str(e)}"
        )
