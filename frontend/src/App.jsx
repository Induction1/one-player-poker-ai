import { useState } from 'react';

const BACKEND_URL = 'http://localhost:8000'; // Change this if you deploy

function App() {
  const initialDeck = Array.from({ length: 52 }, (_, i) => i);
  const [selected, setSelected] = useState([]);
  const [playerHand, setPlayerHand] = useState([]);
  const [reward, setReward] = useState(null);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [opponentCards, setOpponentCards] = useState([]);

  const toggleCard = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const cardLabel = (id) => {
    const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
    const suits = ['♠', '♥', '♦', '♣'];
    const rank = ranks[id % 13];
    const suit = suits[Math.floor(id / 13)];
    return rank + suit;
  };

  const handleNext = async () => {
    if (selected.length === 0) return;
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selected_cards: selected }),
      });
      const data = await response.json();
      setPlayerHand(data.observation.player_hand || []);
      setOpponentCards(data.observation.opponent_cards || []);
      setReward(data.reward);
      setDone(data.done);
      setSelected([]); // clear selection after action
    } catch (err) {
      console.error('Error calling /step:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await fetch(`${BACKEND_URL}/reset`);
      setPlayerHand([]);
      setOpponentCards([]);
      setReward(null);
      setDone(false);
      setSelected([]);
    } catch (err) {
      console.error('Error calling /reset:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl text-black font-bold mb-4">🎴 One-Player Poker</h1>

      <div className="grid grid-cols-13 gap-2 mb-6">
        {initialDeck.map((cardId) => (
          <button
            key={cardId}
            onClick={() => toggleCard(cardId)}
            className={`rounded border p-2 text-center font-mono text-sm transition ${
              selected.includes(cardId)
                ? 'bg-blue-500 text-white'
                : 'bg-white text-black hover:bg-blue-100'
            }`}
          >
            {cardLabel(cardId)}
          </button>
        ))}
      </div>

      <div className="flex gap-4 mb-6">
        <button
          onClick={handleNext}
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
          disabled={loading || done}
        >
          Next
        </button>
        <button
          onClick={handleReset}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:opacity-50"
          disabled={loading}
        >
          Reset
        </button>
      </div>

      <div className="bg-white p-4 text-black rounded shadow-md max-w-md">
        <h2 className="font-semibold mb-2">Your Hand:</h2>
        <div className="flex gap-2 flex-wrap mb-2">
          {playerHand.map((id) => (
            <div key={id} className="border rounded px-2 py-1 text-sm">
              {cardLabel(id)}
            </div>
          ))}
        </div>
        {reward !== null && <p>💰 <strong>Reward:</strong> {reward}</p>}
        {done && <p className="text-red-600 font-semibold mt-2">✅ Game over!</p>}

        <h2 className="font-semibold mt-4 mb-2">Opponent’s Cards:</h2>
        <div className="flex gap-2 flex-wrap mb-2">
          {opponentCards.map((id) => (
            <div key={id} className="border rounded px-2 py-1 text-sm">
              {cardLabel(id)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;