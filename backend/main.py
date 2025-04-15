from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from poker_env.poker_env import OnePlayerPokerEnv

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later replace * with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global poker game environment
env = OnePlayerPokerEnv()
env.reset()


# Define request body structure
class StepRequest(BaseModel):
    selected_cards: list[int]


@app.post("/step")
def step(req: StepRequest):
    obs, reward, done, _ = env.step(req.selected_cards)
    return {
        "observation": {
            "player_hand": env.player_hand,
            "opponent_cards": env.opponent_cards
        },
        "reward": reward,
        "done": done
    }


@app.get("/reset")
def reset():
    env.reset()
    return {"message": "game reset"}
