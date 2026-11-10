import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';

export default function TakeAssessment() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [data, setData] = useState<any>(null);
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const startExam = async () => {
      try {
        const res = await api.post(`/assessments/${id}/start`);
        setData(res.data);
        setTimeLeft(res.data.time_remaining_seconds);
      } catch (err: any) {
        alert(err.response?.data?.detail || "Failed to start assessment");
        navigate('/dashboard');
      } finally {
        setLoading(false);
      }
    };
    startExam();
  }, [id, navigate]);

  // Countdown timer
  useEffect(() => {
    if (timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  if (loading || !data) return <div className="text-white p-8">Loading exam...</div>;

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="bg-red-900/40 border-b border-red-700 p-4 flex justify-between items-center sticky top-0 z-10">
        <h1 className="text-xl font-bold">Exam Mode: Do not refresh</h1>
        <div className="text-2xl font-mono font-bold text-red-400 bg-red-950 px-4 py-1 rounded-lg">
          ⏱ {formatTime(timeLeft)}
        </div>
      </div>

      <div className="p-8 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6">Assigned Challenges</h2>
        <div className="space-y-4">
          {data.challenges.map((c: any) => (
            <div key={c.id} className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">{c.title}</h3>
                <span className="text-xs bg-slate-700 px-2 py-1 rounded mt-2 inline-block">{c.difficulty}</span>
              </div>
              <button 
                onClick={() => alert("In a full implementation, this opens the Monaco editor in exam mode.")}
                className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
              >
                Solve
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}s