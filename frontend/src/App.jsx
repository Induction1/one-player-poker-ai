import { useState } from 'react';
import { useEffect } from 'react';

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
  const [showIntro, setShowIntro] = useState(true);
  const [score, setScore] = useState({ wins: 0, losses: 0, totalRounds: 0 });
  const [playerBest, setPlayerBest] = useState([]);
  const [opponentBest, setOpponentBest] = useState([]);
  const [playerRank, setPlayerRank] = useState('');
  const [opponentRank, setOpponentRank] = useState('');

  const toggleCard = (cardId) => {
      if (dealt.has(cardId)) return;

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
        await new Promise((res) => setTimeout(res, 100));

        const response = await fetch(`${BACKEND_URL}/step`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ selected_cards: selected }),
        });
        const data = await response.json();

        const player = data.observation.player_hand || [];
        const opponent = data.observation.opponent_cards || [];
        const newReward = data.reward;

        setPlayerHand(player);
        setOpponentCards(opponent);
        setReward(newReward);
        setDone(data.done);

        const newlyDealt = new Set([...player, ...opponent]);
        setDealt((prev) => new Set([...prev, ...newlyDealt]));
        setSelected([]);

        if (data.done) {
          setPlayerBest(data.observation.player_best_hand || []);
          setOpponentBest(data.observation.opponent_best_hand || []);
          setPlayerRank(data.observation.player_hand_rank || '');
          setOpponentRank(data.observation.opponent_hand_rank || '');

          setScore((prev) => ({
            wins: prev.wins + (newReward > 0 ? 1 : 0),
            losses: prev.losses + (newReward <= 0 ? 1 : 0),
            totalRounds: prev.totalRounds + 1,
          }));
        }
      } catch (err) {
        console.error('Error calling /step:', err);
      } finally {
        setLoading(false);
      }
    };

  const handleReset = async () => {
      setLoading(true);
      try {
        await new Promise((res) => setTimeout(res, 100));
        await fetch(`${BACKEND_URL}/reset`);
        setPlayerHand([]);
        setOpponentCards([]);
        setReward(null);
        setDone(false);
        setSelected([]);
        setDealt(new Set());

        setPlayerBest([]);
        setOpponentBest([]);
        setPlayerRank('');
        setOpponentRank('');
      } catch (err) {
        console.error('Error calling /reset:', err);
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
      const handleKey = (e) => {
        if (e.key === 'n' || e.key === 'N') {
          if (!loading && !done && selected.length > 0) handleNext();
        }
        if (e.key === 'r' || e.key === 'R') {
          if (!loading) handleReset();
        }
      };

      window.addEventListener('keydown', handleKey);
      return () => window.removeEventListener('keydown', handleKey);
  }, [loading, done, selected, handleNext, handleReset]);

  useEffect(() => {
    const autoReset = async () => {
    try {
      await fetch(`${BACKEND_URL}/reset`);
      setPlayerHand([]);
      setOpponentCards([]);
      setReward(null);
      setDone(false);
      setSelected([]);
      setDealt(new Set());
    } catch (err) {
      console.error('Auto-reset failed:', err);
    }
  };

  autoReset();
}, []);

  return (
    <div className="min-h-screen w-screen bg-green-100 p-6 flex items-center justify-center gap-10">
      {/* LEFT: 13x4 Card Grid */}
      <div className="w-fit">
          {/* Column Select Buttons (with top-left "Select All") */}
          <div className="flex gap-1 mb-1">
            {/* Top-left corner: Select All */}
            <button
              onClick={() => {
                const allCardIds = Array.from({ length: 52 }, (_, i) => i).filter((id) => !dealt.has(id));
                const allAlreadySelected = allCardIds.every((id) => selected.includes(id));
                setSelected(allAlreadySelected ? [] : allCardIds);
              }}
              className="w-6 h-6 bg-purple-400 text-white rounded text-xs hover:bg-purple-500"
            >
              ✦
            </button>

            {/* Suit (Column) Buttons */}
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

          {/* Row Select + Card Grid */}
          <div className="flex gap-1 items-start">
            {/* Rank (Row) Buttons */}
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

            {/* 13x4 Card Grid (vertical fill) */}
            <div className="grid grid-cols-4 grid-rows-13 gap-1">
              {Array.from({ length: 13 }, (_, row) =>
                Array.from({ length: 4 }, (_, col) => {
                  const id = col * 13 + row;
                  const isDealt = dealt.has(id);
                  const isSelected = selected.includes(id);
                  return (
                    <button
                      key={id}
                      onClick={() => !isDealt && toggleCard(id)}
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
              )}
            </div>
          </div>
        </div>

      {/* RIGHT: Play-by-Play Panel */}
        <div className="bg-white text-black p-4 rounded shadow-md w-full max-w-md flex flex-col gap-4 overflow-hidden max-h-[90vh]">
          {/* 🪄 Game Info Section */}
          <div>
            <h2 className="text-xl font-bold mb-2">Game State</h2>

            <h3 className="font-semibold mb-1">Your Hand:</h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  {playerHand.map((id) => (
                    <div
                      key={id}
                      className={`border rounded px-2 py-1 text-sm ${
                        playerBest.includes(id) ? 'bg-green-200 font-bold' : ''
                      }`}
                    >
                      {cardLabel(id)}
                    </div>
                  ))}
                </div>
                <p className="text-center text-xs mt-1 italic text-gray-600">{playerRank}</p>

            <h3 className="font-semibold mt-4 mb-1">Opponent's Cards:</h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  {opponentCards.map((id) => (
                    <div
                      key={id}
                      className={`border rounded px-2 py-1 text-sm ${
                        opponentBest.includes(id) ? 'bg-green-200 font-bold' : ''
                      }`}
                    >
                      {cardLabel(id)}
                    </div>
                  ))}
                </div>
                <p className="text-center text-xs mt-1 italic text-gray-600">{opponentRank}</p>


            {done && (
              <p
                className={`mt-4 font-semibold text-lg ${
                  reward > 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                Game Over: {reward > 0 ? 'Win!' : 'Loss'}
              </p>
            )}

          </div>

          {/* 🕹️ Controls + Score Block */}
          <div className="mt-4">
            <div className="flex gap-4 justify-center mb-4">
              <button
                onClick={handleNext}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50 transition-transform duration-150 active:translate-y-[2px]"
                disabled={loading || done}
              >
                <span className="font-bold underline">N</span>ext
              </button>
              <button
                onClick={handleReset}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:opacity-50 transition-transform duration-150 active:translate-y-[2px]"
                disabled={loading}
              >
                <span className="font-bold underline">R</span>eset
              </button>
            </div>

            <div className="text-sm text-center border-t pt-3">
              <h4 className="font-semibold  text-xl mb-2">Score</h4>
              <div className="flex justify-center gap-6">
                <p className="text-600 font-bold">Wins: {score.wins}</p>
                <p className="text-600 font-bold">Losses: {score.losses}</p>
              </div>
            </div>
          </div>
        </div>

      {showIntro && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-white text-black p-6 rounded-xl shadow-lg max-w-md text-center animate-fade-in">
            <h1 className="text-3xl font-bold mb-4">🃏 Five Eight Poker 🃏</h1>
            <p className="mb-4">
              Each round, pick target cards. The deck flips until one hits—yours to keep. Misses go to your opponent. Your opponent gets at least 8 cards. After 5 rounds, your hand faces off against their best hand. Ties are losses. Have fun!
            </p>
            <button
              onClick={() => setShowIntro(false)}
              className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition"
            >
              Start Game
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;