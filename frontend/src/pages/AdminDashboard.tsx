import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

export default function AdminDashboard() {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-slate-900 p-8 text-white">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <div className="flex gap-4">
              <Link 
                to="/admin/create-challenge" 
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                + Create Challenge
              </Link>
              <Link 
                to="/admin/create-assessment" 
                className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                + Schedule Assessment
              </Link>
              <Link 
                to="/admin/analytics" 
                className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                View Analytics
              </Link>
              <Link 
                to="/leaderboard" 
                className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Leaderboard
              </Link>
            </div>
          </div>
          
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
            <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
            <p className="text-slate-400">Welcome to the admin panel. Select an action above to proceed.</p>
          </div>
        </div>
      </div>
    </>
  );
}