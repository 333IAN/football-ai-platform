import React, { useState, useEffect } from 'react';
import { Trophy, Swords, Activity, AlertCircle, BarChart3, Globe } from 'lucide-react';

export default function App() {
  const [teams, setTeams] = useState([]);
  const [homeTeamId, setHomeTeamId] = useState('');
  const [awayTeamId, setAwayTeamId] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch teams from the FastAPI backend on load
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/teams`);
        if (!response.ok) throw new Error('Failed to connect to AI server.');
        const data = await response.json();
        // Sort teams alphabetically
        const sortedTeams = data.sort((a, b) => a.name.localeCompare(b.name));
        setTeams(sortedTeams);
      } catch (err) {
        setError('Cannot reach the FastAPI backend. Ensure uvicorn is running.');
      }
    };
    fetchTeams();
  }, []);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!homeTeamId || !awayTeamId) {
      setError("Please select both a home and away team.");
      return;
    }
    if (homeTeamId === awayTeamId) {
      setError("A team cannot play itself.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          home_team_id: homeTeamId,
          away_team_id: awayTeamId
        })
      });

      if (!response.ok) throw new Error('Prediction engine failed to process request.');
      
      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to map the raw class from XGBoost to human-readable text
  const getOutcomeText = (predictedClass) => {
    const map = {
      "0": "Home Win",
      "1": "Draw",
      "2": "Away Win"
    };
    return map[String(predictedClass)] || "Unknown Outcome";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-indigo-500/30">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-900/20">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white">
              Football <span className="text-indigo-400">AI Platform</span>
            </h1>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium text-emerald-400 bg-emerald-400/10 px-3 py-1.5 rounded-full border border-emerald-400/20">
            <Globe className="w-4 h-4" />
            <span>Engine Online</span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-12 gap-8">
        
        {/* Left Column: Matchup Selector */}
        <div className="md:col-span-5 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
              <Swords className="w-5 h-5 text-indigo-400" />
              Configure Matchup
            </h2>
            
            <form onSubmit={handlePredict} className="space-y-6">
              {/* Home Team */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-400 block">Home Team</label>
                <select 
                  value={homeTeamId}
                  onChange={(e) => setHomeTeamId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                >
                  <option value="">-- Select Home Team --</option>
                  {teams.map(team => (
                    <option key={`home-${team.team_id}`} value={team.team_id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* VS Divider */}
              <div className="relative flex items-center py-2">
                <div className="flex-grow border-t border-slate-800"></div>
                <span className="flex-shrink-0 mx-4 text-slate-500 font-bold text-sm bg-slate-900 px-2">VS</span>
                <div className="flex-grow border-t border-slate-800"></div>
              </div>

              {/* Away Team */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-400 block">Away Team</label>
                <select 
                  value={awayTeamId}
                  onChange={(e) => setAwayTeamId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                >
                  <option value="">-- Select Away Team --</option>
                  {teams.map(team => (
                    <option key={`away-${team.team_id}`} value={team.team_id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Error Message */}
              {error && (
                <div className="flex items-center gap-2 text-rose-400 bg-rose-400/10 p-4 rounded-xl border border-rose-400/20 text-sm">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <p>{error}</p>
                </div>
              )}

              <button 
                type="submit" 
                disabled={isLoading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg shadow-indigo-900/30 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <BarChart3 className="w-5 h-5" />
                    Run AI Prediction
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Prediction Results */}
        <div className="md:col-span-7">
          {prediction ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-500">
              
              {/* Result Header */}
              <div className="text-center mb-10">
                <p className="text-indigo-400 font-semibold tracking-wider text-sm uppercase mb-2">AI Forecast Output</p>
                <div className="flex justify-center items-center gap-4 text-3xl md:text-4xl font-bold text-white mb-4">
                  <span className="truncate max-w-[200px]">{prediction.home_team}</span>
                  <span className="text-slate-600 font-light">vs</span>
                  <span className="truncate max-w-[200px]">{prediction.away_team}</span>
                </div>
                
                <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-slate-800 border border-slate-700">
                  <Trophy className={`w-5 h-5 ${
                    prediction.prediction_class === "0" ? "text-emerald-400" :
                    prediction.prediction_class === "2" ? "text-blue-400" : "text-amber-400"
                  }`} />
                  <span className="text-slate-300 font-medium">
                    Favored Outcome: <span className="text-white font-bold">{getOutcomeText(prediction.prediction_class)}</span>
                  </span>
                </div>
              </div>

              {/* Elo Stats Comparison */}
              <div className="grid grid-cols-2 gap-4 mb-10">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                  <p className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">Home Elo Rating</p>
                  <p className="text-2xl font-bold text-emerald-400">{prediction.home_elo.toLocaleString()}</p>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                  <p className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">Away Elo Rating</p>
                  <p className="text-2xl font-bold text-blue-400">{prediction.away_elo.toLocaleString()}</p>
                </div>
              </div>

              {/* Probability Bars */}
              <div className="space-y-6">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800 pb-2">Outcome Probabilities</h3>
                
                {/* Home Win Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-300">Home Win ({prediction.home_team})</span>
                    <span className="font-bold text-emerald-400">{((prediction.raw_mapped_probabilities?.["0"] || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
                    <div 
                      className="bg-emerald-500 h-full rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${(prediction.raw_mapped_probabilities?.["0"] || 0) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Draw Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-300">Draw</span>
                    <span className="font-bold text-amber-400">{((prediction.raw_mapped_probabilities?.["1"] || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
                    <div 
                      className="bg-amber-500 h-full rounded-full transition-all duration-1000 ease-out delay-150"
                      style={{ width: `${(prediction.raw_mapped_probabilities?.["1"] || 0) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Away Win Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-300">Away Win ({prediction.away_team})</span>
                    <span className="font-bold text-blue-400">{((prediction.raw_mapped_probabilities?.["2"] || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
                    <div 
                      className="bg-blue-500 h-full rounded-full transition-all duration-1000 ease-out delay-300"
                      style={{ width: `${(prediction.raw_mapped_probabilities?.["2"] || 0) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

            </div>
          ) : (
            <div className="bg-slate-900/50 border border-slate-800 border-dashed rounded-2xl p-12 h-full flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
                <BarChart3 className="w-8 h-8 text-slate-600" />
              </div>
              <h3 className="text-lg font-medium text-slate-300 mb-2">Ready for Analysis</h3>
              <p className="text-slate-500 max-w-sm">
                Select a home and away team from the configured matchups to run the XGBoost prediction engine.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}