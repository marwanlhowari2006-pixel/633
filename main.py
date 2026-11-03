file:///data/user/0/com.foxdebug.acodefree/files/public/main.pyfrom fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import os

app = FastAPI(title="AI Game Spectator Cloud Server", version="2.0")

SECRET_API_KEY = os.getenv("API_KEY", "my_super_secret_game_key_123")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != SECRET_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key - Access Denied")
    return x_api_key

class PlayerTelemetry(BaseModel):
    player_id: str
    current_speed: float
    altitude: float
    in_vehicle: bool = False
    parachuting: bool = False

class ServerMetrics(BaseModel):
    high_ping_count: int = 0
    desync_events: int = 0

class MatchFrameData(BaseModel):
    server_metrics: ServerMetrics
    players: list[PlayerTelemetry]

GAME_RULES = {"max_speed": 12.0, "max_altitude": 5.0}

@app.post("/api/v1/spectate/frame")
def analyze_match_frame(data: MatchFrameData, api_key: str = Depends(verify_api_key)):
    actions_to_execute = []
    server_wide_lag_active = False
    if data.server_metrics.high_ping_count > 40 or data.server_metrics.desync_events > 8:
        server_wide_lag_active = True

    for player in data.players:
        is_speeding = player.current_speed > GAME_RULES["max_speed"] and not player.in_vehicle and not player.parachuting
        is_flying = player.altitude > GAME_RULES["max_altitude"] and not player.in_vehicle and not player.parachuting

        if is_speeding or is_flying:
            reason = "Speed Hack Detected" if is_speeding else "Fly Hack Detected"
            if server_wide_lag_active:
                continue
            actions_to_execute.append({
                "player_id": player.player_id,
                "action": "BAN_PLAYER",
                "reason": reason
            })

    return {
        "status": "success",
        "cloud_processed": True,
        "flagged_players_count": len(actions_to_execute),
        "actions": actions_to_execute
    }

@app.get("/")
def home():
    return {"message": "AI Game Spectator Cloud Server is Online and Secure!"}
