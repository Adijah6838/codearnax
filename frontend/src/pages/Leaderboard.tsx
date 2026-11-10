import { useEffect, useState } from 'react';
import { api } from '../api';
import Navbar from '../components/Navbar';

interface LeaderboardEntry {
  candidate_id: number;
  email: string;
  full_name: string;
  total_score: number;
  challenges_completed: number;
}

export default function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await api.get('/leaderboard');
        setEntries(res.data);
      } catch (err: any) {
        if (err.response?.status === 403) {
          setError("The leaderboard is currently hidden by the administrator.");
        } else {
          setError("Failed to load leaderboard.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchLeaderboard();
  }, []);

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-slate-900 p-8 text-white">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Global Leaderboard</h1>

          {loading ? (
            <p className="text-slate-400">Loading...</p>
          ) : error ? (
            <div className="bg-red-500/10 border border-red-500 text-red-400 p-4 rounded-lg">
              {error}
            </div>
          ) : (
            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
              <table className="w-full text-left">
                <thead className="bg-slate-900/50 border-b border-slate-700">
                  <tr>
                    <th className="px-6 py-4 font-semibold text-slate-300">Rank</th>
                    <th className="px-6 py-4 font-semibold text-slate-300">Candidate</th>
                    <th className="px-6 py-4 font-semibold text-slate-300 text-right">Score</th>
                    <th className="px-6 py-4 font-semibold text-slate-300 text-right">Challenges</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {entries.map((entry, index) => (
                    <tr key={entry.candidate_id} className="hover:bg-slate-700/20 transition-colors">
                      <td className="px-6 py-4">
                        <span className={`font-bold ${index === 0 ? 'text-yellow-400 text-lg' : index === 1 ? 'text-gray-300 text-lg' : index === 2 ? 'text-amber-600 text-lg' : 'text-slate-500'}`}>
                          #{index + 1}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-medium text-white">{entry.full_name}</div>
                        <div className="text-sm text-slate-400">{entry.email}</div>
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-blue-400 font-semibold">
                        {entry.total_score.toFixed(0)} pts
                      </td>
                      <td className="px-6 py-4 text-right text-slate-300">
                        {entry.challenges_completed}
                      </td>
                    </tr>
                  ))}
                  {entries.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-slate-400">No candidates on the leaderboard yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}