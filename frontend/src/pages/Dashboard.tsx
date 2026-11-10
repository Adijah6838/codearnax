import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import Navbar from '../components/Navbar';

interface Challenge {
  id: number;
  title: string;
  difficulty: string;
  category: string;
}

export default function Dashboard() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchChallenges = async () => {
      try {
        const res = await api.get('/challenges');
        setChallenges(res.data);
      } catch (err) {
        console.error("Failed to load challenges", err);
      } finally {
        setLoading(false);
      }
    };
    fetchChallenges();
  }, []);

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-slate-900 p-8">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-8">Available Challenges</h1>
          
          {loading ? (
            <p className="text-slate-400">Loading challenges...</p>
          ) : challenges.length === 0 ? (
            <p className="text-slate-400">No challenges published yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {challenges.map((c) => (
                <div key={c.id} className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-blue-500 transition-colors">
                  <h2 className="text-xl font-semibold text-white mb-2">{c.title}</h2>
                  <div className="flex gap-2 mb-4">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      c.difficulty === 'Beginner' ? 'bg-green-500/20 text-green-400' :
                      c.difficulty === 'Intermediate' ? 'bg-yellow-500/20 text-yellow-400' :
                      c.difficulty === 'Advanced' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {c.difficulty}
                    </span>
                    <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-300">
                      {c.category}
                    </span>
                  </div>
                  <Link 
                    to={`/workspace/${c.id}`}
                    className="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors"
                  >
                    Solve Challenge
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}