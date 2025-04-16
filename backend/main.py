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

    if done:
        player_best = env.best_5_cards(env.player_hand)
        player_rank = env.hand_rank_name(player_best)

        best_score, best_opponent_hand = env.best_opponent_hand_rank()
        opponent_best = best_opponent_hand
        opponent_rank = env.hand_rank_name(best_opponent_hand)
    else:
        player_best = []
        player_rank = ""
        opponent_best = []
        opponent_rank = ""

    return {
        "observation": {
            "player_hand": env.player_hand,
            "opponent_cards": env.opponent_cards,
            "player_best_hand": player_best,
            "opponent_best_hand": opponent_best,
            "player_hand_rank": player_rank,
            "opponent_hand_rank": opponent_rank
        },
        "reward": reward,
        "done": done
    }


@app.get("/reset")
def reset():
    env.reset()
    return {"message": "game reset"}
