import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import Navbar from '../components/Navbar';

export default function CreateAssessment() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [startsAt, setStartsAt] = useState('');
  const [endsAt, setEndsAt] = useState('');
  const [challenges, setChallenges] = useState<any[]>([]);
  const [selectedChallenge, setSelectedChallenge] = useState<number | ''>('');
  
  // For simplicity in this demo, we will hardcode assigning to candidate ID 3 (cand@codearnax.dev)
  // In a real app, you would fetch all users with role 'Candidate' and show checkboxes.
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchChallenges = async () => {
      const res = await api.get('/challenges');
      setChallenges(res.data);
      if (res.data.length > 0) setSelectedChallenge(res.data[0].id);
    };
    fetchChallenges();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/assessments', {
        title,
        starts_at: new Date(startsAt).toISOString(),
        ends_at: new Date(endsAt).toISOString(),
        challenge_ids: [Number(selectedChallenge)],
        candidate_ids: [3] // cand@codearnax.dev
      });
      navigate('/admin');
    } catch (err) {
      alert("Failed to create assessment");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-slate-900 p-8 text-white">
        <div className="max-w-2xl mx-auto bg-slate-800 rounded-xl border border-slate-700 p-8">
          <h1 className="text-2xl font-bold mb-6">Schedule an Assessment</h1>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-300 mb-1">Assessment Title</label>
              <input required value={title} onChange={e => setTitle(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg outline-none" />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-slate-300 mb-1">Starts At</label>
                <input type="datetime-local" required value={startsAt} onChange={e => setStartsAt(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg outline-none text-white" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Ends At</label>
                <input type="datetime-local" required value={endsAt} onChange={e => setEndsAt(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg outline-none text-white" />
              </div>
            </div>

            <div>
              <label className="block text-sm text-slate-300 mb-1">Select Challenge</label>
              <select value={selectedChallenge} onChange={e => setSelectedChallenge(Number(e.target.value))} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg outline-none">
                {challenges.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
              </select>
            </div>

            <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg font-medium mt-4">
              {loading ? 'Scheduling...' : 'Schedule Assessment'}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}