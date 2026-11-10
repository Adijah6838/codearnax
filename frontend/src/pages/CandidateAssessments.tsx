import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import Navbar from '../components/Navbar';

export default function CandidateAssessments() {
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const res = await api.get('/assessments');
        setAssessments(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAssessments();
  }, []);

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-slate-900 p-8 text-white">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">My Assessments</h1>
          
          {loading ? <p className="text-slate-400">Loading...</p> : (
            <div className="grid gap-4">
              {assessments.map(a => (
                <div key={a.id} className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex justify-between items-center">
                  <div>
                    <h2 className="text-xl font-semibold">{a.title}</h2>
                    <p className="text-sm text-slate-400 mt-1">Ends: {new Date(a.ends_at).toLocaleString()}</p>
                  </div>
                  <Link to={`/assessment/${a.id}`} className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-medium">
                    Start Assessment
                  </Link>
                </div>
              ))}
              {assessments.length === 0 && <p className="text-slate-400">No assessments assigned to you.</p>}
            </div>
          )}
        </div>
      </div>
    </>
  );
}