import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Match {
  id: number;
  home_team: { name: string };
  away_team: { name: string };
  match_date: string;
  status: string;
  home_goals?: number;
  away_goals?: number;
}

interface Prediction {
  home_win_prob: number;
  draw_prob: number;
  away_win_prob: number;
  most_likely_score: string;
}

export default function Dashboard() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [predictions, setPredictions] = useState<Record<number, Prediction>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUpcomingMatches();
  }, []);

  const fetchUpcomingMatches = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/matches/upcoming?limit=10`);
      setMatches(response.data);
      
      // Fetch predictions for each match
      const predictionsData: Record<number, Prediction> = {};
      for (const match of response.data) {
        try {
          const predResponse = await axios.get(`${API_BASE}/predict/match/${match.id}`);
          predictionsData[match.id] = predResponse.data.prediction;
        } catch (err) {
          console.error(`Error fetching prediction for match ${match.id}`);
        }
      }
      setPredictions(predictionsData);
    } catch (error) {
      console.error('Error fetching matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProbabilityColor = (prob: number): string => {
    if (prob > 0.5) return 'bg-green-500';
    if (prob > 0.33) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Premier League Analyst Pro</h1>
        <p className="text-gray-400">AI-Powered Match Predictions</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upcoming Matches */}
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold mb-4">Upcoming Matches</h2>
          <div className="space-y-4">
            {matches.map((match) => {
              const pred = predictions[match.id];
              return (
                <div
                  key={match.id}
                  onClick={() => setSelectedMatch(match)}
                  className={`p-4 rounded-lg cursor-pointer transition ${
                    selectedMatch?.id === match.id
                      ? 'bg-blue-600'
                      : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex justify-between items-center mb-3">
                    <div className="text-lg font-semibold">
                      {match.home_team.name} vs {match.away_team.name}
                    </div>
                    <div className="text-sm text-gray-400">
                      {new Date(match.match_date).toLocaleDateString()}
                    </div>
                  </div>

                  {pred && (
                    <div className="grid grid-cols-3 gap-2">
                      <div className={`p-2 rounded text-center ${getProbabilityColor(pred.home_win_prob)}`}>
                        <div className="text-sm">Win</div>
                        <div className="font-bold">{(pred.home_win_prob * 100).toFixed(1)}%</div>
                      </div>
                      <div className={`p-2 rounded text-center ${getProbabilityColor(pred.draw_prob)}`}>
                        <div className="text-sm">Draw</div>
                        <div className="font-bold">{(pred.draw_prob * 100).toFixed(1)}%</div>
                      </div>
                      <div className={`p-2 rounded text-center ${getProbabilityColor(pred.away_win_prob)}`}>
                        <div className="text-sm">Loss</div>
                        <div className="font-bold">{(pred.away_win_prob * 100).toFixed(1)}%</div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Detail Panel */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Match Details</h2>
          {selectedMatch ? (
            <div>
              <h3 className="text-xl font-semibold mb-4">
                {selectedMatch.home_team.name} vs {selectedMatch.away_team.name}
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="text-gray-400">Match Date</label>
                  <p>{new Date(selectedMatch.match_date).toLocaleString()}</p>
                </div>
                <div>
                  <label className="text-gray-400">Status</label>
                  <p>{selectedMatch.status}</p>
                </div>
                {selectedMatch.status === 'FINISHED' && (
                  <div>
                    <label className="text-gray-400">Result</label>
                    <p className="text-2xl font-bold">
                      {selectedMatch.home_goals} - {selectedMatch.away_goals}
                    </p>
                  </div>
                )}
                {predictions[selectedMatch.id] && (
                  <div>
                    <label className="text-gray-400">Predicted Score</label>
                    <p className="text-xl font-bold">
                      {predictions[selectedMatch.id].most_likely_score}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <p className="text-gray-400">Select a match to see details</p>
          )}
        </div>
      </div>
    </div>
  );
}
