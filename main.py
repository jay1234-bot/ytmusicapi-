from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
import yt_dlp

# YTMusic object initialize karna
ytmusic = YTMusic()

app = FastAPI(
    title="Krishan Music API",
    description="Advanced backend for YT Music using ytmusicapi & yt-dlp",
    version="1.0.0"
)

# CORS setup taaki frontend (Netlify/Vercel) block na ho
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🏠 HOME ENDPOINT (Main link kholne par)
# ==========================================
@app.get("/", tags=["System"])
def home():
    return {"message": "Welcome to Krishan Music API! Go to /docs to see all features."}

# ==========================================
# 🟢 UPTIME ROBOT PING ENDPOINT (Fix for HEAD request)
# ==========================================
# Yahan GET aur HEAD dono allow kar diye hain
@app.get("/ping", tags=["System"])
@app.head("/ping", tags=["System"])
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
    try:
        results = ytmusic.search(query=query, filter=filter)
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/song/{video_id}", tags=["Music"])
def get_song_details(video_id: str):
    try:
        details = ytmusic.get_watch_playlist(videoId=video_id)
        return {"status": "success", "data": details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lyrics/{browse_id}", tags=["Music"])
def get_song_lyrics(browse_id: str):
    try:
        lyrics = ytmusic.get_lyrics(browseId=browse_id)
        return {"status": "success", "data": lyrics}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Lyrics not found")

@app.get("/artist/{channel_id}", tags=["Music"])
def get_artist_info(channel_id: str):
    try:
        artist = ytmusic.get_artist(channelId=channel_id)
        return {"status": "success", "data": artist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/playlist/{playlist_id}", tags=["Music"])
def get_playlist_data(playlist_id: str):
    try:
        playlist = ytmusic.get_playlist(playlistId=playlist_id)
        return {"status": "success", "data": playlist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 🎧 DIRECT PLAYBACK URL ENDPOINT (yt-dlp)
# ==========================================
@app.get("/stream/{video_id}", tags=["Music"])
def get_stream_url(video_id: str):
    """Gaane ka direct audio streaming URL nikalne ke liye."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True, # Video download nahi karna hai
    }
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info.get('url')
            
            if not audio_url:
                raise Exception("Streaming URL nahi mila.")
                
            return {
                "status": "success", 
                "video_id": video_id,
                "title": info.get('title'),
                "stream_url": audio_url
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting URL: {str(e)}")
