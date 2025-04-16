import { useState } from 'react';

const BACKEND_URL = 'http://localhost:8000';

const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
const suits = ['♠', '♥', '♦', '♣'];

function App() {
  const [selected, setSelected] = useState([]);
  const [playerHand, setPlayerHand] = useState([]);
  const [opponentCards, setOpponentCards] = useState([]);
  const [reward, setReward] = useState(null);
  const [dealt, setDealt] = useState(new Set());
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleCard = (cardId) => {
      if (dealt.has(cardId)) return; // ⛔ Don't allow dealt cards to be selected

      setSelected((prev) =>
        prev.includes(cardId) ? prev.filter((c) => c !== cardId) : [...prev, cardId]
      );
    };

  const cardLabel = (id) => {
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
      const newlyDealt = new Set([...(data.observation.player_hand || []), ...(data.observation.opponent_cards || []),]);
      setDealt((prev) => new Set([...prev, ...newlyDealt]));
      setSelected([]);
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
      setDealt(new Set());
    } catch (err) {
      console.error('Error calling /reset:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-green-100 p-6 flex gap-6">
      {/* LEFT: 13x4 Card Grid */}
      <div className="w-fit">
          {/* Column Select Buttons (suits) */}
          <div className="flex ml-[30px] gap-1 mb-1">
            {suits.map((_, colIdx) => (
              <button
                key={`col-${colIdx}`}
                onClick={() => {
                  const colIds = Array.from({ length: 13 }, (_, rowIdx) => colIdx * 13 + rowIdx);
                  const filteredIds = colIds.filter((id) => !dealt.has(id));
                  const allSelected = filteredIds.every((id) => selected.includes(id));
                  setSelected((prev) =>
                    allSelected
                      ? prev.filter((id) => !filteredIds.includes(id))
                      : [...new Set([...prev, ...filteredIds])]
                  );
                }}
                className="w-12 h-6 bg-yellow-300 rounded text-xs hover:bg-yellow-400"
              >
                ↓
              </button>
            ))}
          </div>

          {/* Row Select + Grid */}
          <div className="flex gap-1 items-start">
            {/* Row Select Buttons (ranks) */}
            <div className="flex flex-col gap-1">
              {ranks.map((_, rowIdx) => (
                <button
                  key={`row-${rowIdx}`}
                  onClick={() => {
                    const rowIds = Array.from({ length: 4 }, (_, colIdx) => colIdx * 13 + rowIdx);
                    const filteredIds = rowIds.filter((id) => !dealt.has(id));
                    const allSelected = filteredIds.every((id) => selected.includes(id));
                    setSelected((prev) =>
                      allSelected
                        ? prev.filter((id) => !filteredIds.includes(id))
                        : [...new Set([...prev, ...filteredIds])]
                    );
                  }}
                  className="w-6 h-12 bg-yellow-300 rounded text-xs hover:bg-yellow-400"
                >
                  →
                </button>
              ))}
            </div>

            {/* Card Grid: 13 rows x 4 cols */}
            <div className="grid grid-cols-4 grid-rows-13 gap-1">
              {Array.from({ length: 13 }, (_, row) => (
                Array.from({ length: 4 }, (_, col) => {
                  const id = col * 13 + row;
                  const isDealt = dealt.has(id);
                  const isSelected = selected.includes(id);

                  return (
                    <button
                      key={id}
                      onClick={() => {
                        if (!isDealt) toggleCard(id);
                      }}
                      disabled={isDealt}
                      className={`w-12 h-12 rounded border text-center font-mono text-sm transition ${
                        isDealt
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : isSelected
                            ? 'bg-blue-500 text-white'
                            : 'bg-white text-black hover:bg-blue-100'
                      }`}
                    >
                      {cardLabel(id)}
                    </button>
                  );
                })
              ))}
            </div>
          </div>
        </div>

      {/* RIGHT: Play-by-Play Panel */}
      <div className="bg-white text-black p-4 rounded shadow-md w-full max-w-md">
        <h2 className="text-xl font-bold mb-2">Play-by-Play</h2>

        <h3 className="font-semibold mb-1">Your Hand:</h3>
        <div className="flex flex-wrap gap-2 mb-2">
          {playerHand.map((id) => (
            <div key={id} className="border rounded px-2 py-1 text-sm">
              {cardLabel(id)}
            </div>
          ))}
        </div>

        <h3 className="font-semibold mt-4 mb-1">Opponent's Cards:</h3>
        <div className="flex flex-wrap gap-2 mb-2">
          {opponentCards.map((id) => (
            <div key={id} className="border rounded px-2 py-1 text-sm">
              {cardLabel(id)}
            </div>
          ))}
        </div>

        {reward !== null && <p>💰 <strong>Reward:</strong> {reward}</p>}
        {done && <p className="text-red-600 font-semibold mt-2">✅ Game over!</p>}

        <div className="mt-4 flex gap-4">
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
      </div>
    </div>
  );
}

export default App;