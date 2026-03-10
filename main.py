from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic

# YTMusic object initialize karna (Bina login ke public features ke liye)
ytmusic = YTMusic()

app = FastAPI(
    title="YouTube Music Custom API",
    description="Advanced backend for YT Music using ytmusicapi",
    version="1.0.0"
)

# CORS middleware add karna taaki aapka frontend is API ko call kar sake bina kisi error ke
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🟢 UPTIME ROBOT PING ENDPOINT
# ==========================================
@app.get("/ping", tags=["System"])
def ping_server():
    """UptimeRobot is endpoint ko hit karega server ko zinda rakhne ke liye."""
    return {"status": "success", "message": "Server is awake and running!"}

# ==========================================
# 🎵 MUSIC API ENDPOINTS
# ==========================================

@app.get("/search", tags=["Music"])
def search_music(
    query: str = Query(..., description="Gaane, artist ya album ka naam"),
    filter: str = Query(None, description="Filter: 'songs', 'videos', 'albums', 'artists', 'playlists'")
):
    """YouTube Music par kuch bhi search karne ke liye."""
    try:
        results = ytmusic.search(query=query, filter=filter)
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/song/{video_id}", tags=["Music"])
def get_song_details(video_id: str):
    """Kisi bhi gaane ki details nikalne ke liye uska Video ID use karein."""
    try:
        # Ye gaane ka metadata aur 'Up Next' queue laata hai
        details = ytmusic.get_watch_playlist(videoId=video_id)
        return {"status": "success", "data": details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lyrics/{browse_id}", tags=["Music"])
def get_song_lyrics(browse_id: str):
    """Gaane ke lyrics nikalne ke liye (browse_id search ya song details se milega)."""
    try:
        lyrics = ytmusic.get_lyrics(browseId=browse_id)
        return {"status": "success", "data": lyrics}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Lyrics not found or error occurred")

@app.get("/artist/{channel_id}", tags=["Music"])
def get_artist_info(channel_id: str):
    """Artist ki profile, top songs aur albums nikalne ke liye."""
    try:
        artist = ytmusic.get_artist(channelId=channel_id)
        return {"status": "success", "data": artist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/playlist/{playlist_id}", tags=["Music"])
def get_playlist_data(playlist_id: str):
    """Kisi bhi public playlist ke saare gaane fetch karne ke liye."""
    try:
        playlist = ytmusic.get_playlist(playlistId=playlist_id)
        return {"status": "success", "data": playlist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Note: Agar aapko User ki private playlists access karni hai, toh aapko OAuth/Headers setup karna padega.
# Ye code public data ke liye perfectly work karega.
