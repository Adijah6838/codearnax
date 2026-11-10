import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center text-white">
      <div className="flex items-center gap-6">
        <Link to="/" className="text-xl font-bold tracking-wider text-blue-400">CODEARENA X</Link>
        {user.role === 'Candidate' && (
          <>
            <Link to="/dashboard" className="text-slate-300 hover:text-white transition-colors">Challenges</Link>
            <Link to="/assessments" className="text-slate-300 hover:text-white transition-colors">My Assessments</Link>
            <Link to="/leaderboard" className="text-slate-300 hover:text-white transition-colors">Leaderboard</Link>
          </>
        )}
        {(user.role === 'Administrator' || user.role === 'AssessmentManager') && (
          <>
            <Link to="/admin" className="text-slate-300 hover:text-white transition-colors">Admin Panel</Link>
            <Link to="/admin/analytics" className="text-slate-300 hover:text-white transition-colors">Analytics</Link>
          </>
        )}
      </div>
      
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-400">
          {user.full_name} <span className="text-xs px-2 py-1 bg-slate-700 rounded-full ml-1">{user.role}</span>
        </span>
        <button 
          onClick={handleLogout}
          className="bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white px-4 py-1.5 rounded-lg text-sm font-medium transition-colors"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}