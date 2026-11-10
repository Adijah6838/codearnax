import { useEffect, useState } from 'react';
import { api } from '../api';
import Navbar from '../components/Navbar';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, CartesianGrid } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Analytics() {
  const [overview, setOverview] = useState<any>(null);
  const [languages, setLanguages] = useState<any[]>([]);
  const [failures, setFailures] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ovRes, langRes, failRes] = await Promise.all([
          api.get('/analytics/overview'),
          api.get('/analytics/languages'),
          api.get('/analytics/failures')
        ]);
        
        setOverview(ovRes.data);
        
        setLanguages(Object.keys(langRes.data).map(key => ({ name: key, value: langRes.data[key] })));
        setFailures(Object.keys(failRes.data).map(key => ({ name: key, value: failRes.data[key] })));
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading || !overview) return <div className="min-h-screen bg-slate-900 text-white p-8">Loading analytics...</div>;

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-slate-900 p-8 text-white">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Platform Analytics</h1>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-slate-400 text-sm mb-2">Total Challenges</h3>
              <p className="text-3xl font-bold">{overview.total_challenges}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-slate-400 text-sm mb-2">Total Submissions</h3>
              <p className="text-3xl font-bold">{overview.total_submissions}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-slate-400 text-sm mb-2">Accepted</h3>
              <p className="text-3xl font-bold text-green-400">{overview.accepted_submissions}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-slate-400 text-sm mb-2">Avg Execution Time</h3>
              <p className="text-3xl font-bold text-blue-400">{overview.average_execution_ms.toFixed(0)} ms</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-lg font-semibold mb-6">Language Usage</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={languages} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                      {languages.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-lg font-semibold mb-6">Failure Categories</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={failures}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" allowDecimals={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }} cursor={{fill: '#334155'}} />
                    <Bar dataKey="value" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}