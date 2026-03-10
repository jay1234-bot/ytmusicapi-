from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic

ytmusic = YTMusic()

app = FastAPI(title="Krishan Music Pro API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
def home():
    return {"status": "online", "message": "Krishan Music API Pro is Running"}

@app.get("/ping")
@app.head("/ping")
def ping():
    return {"status": "success"}

@app.get("/search")
def search_music(query: str):
    try:
        return {"status": "success", "data": ytmusic.search(query, filter="songs")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggestions/{video_id}")
def get_suggestions(video_id: str):
    try:
        # Watch playlist suggests similar songs
        data = ytmusic.get_watch_playlist(videoId=video_id, limit=15)
        return {"status": "success", "data": data['tracks']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lyrics/{video_id}")
def get_lyrics(video_id: str):
    try:
        # Pehle watch playlist se browseId nikalna padta hai lyrics ke liye
        watch_data = ytmusic.get_watch_playlist(videoId=video_id)
        lyrics_id = watch_data.get('lyrics')
        if not lyrics_id:
            return {"status": "error", "message": "No lyrics found"}
        
        lyrics_data = ytmusic.get_lyrics(browseId=lyrics_id)
        return {"status": "success", "data": lyrics_data['lyrics']}
    except Exception as e:
        return {"status": "error", "message": "Lyrics not available"}
