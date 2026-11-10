import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import Workspace from './pages/Workspace';
import CreateChallenge from './pages/CreateChallenge';
import Analytics from './pages/Analytics';
import Leaderboard from './pages/Leaderboard';
import CreateAssessment from './pages/CreateAssessment';
import CandidateAssessments from './pages/CandidateAssessments';
import TakeAssessment from './pages/TakeAssessment';

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode, allowedRoles: string[] }) {
  const { user, isLoading } = useAuth();
  
  if (isLoading) return <div className="min-h-screen flex items-center justify-center text-white">Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  if (!allowedRoles.includes(user.role)) return <Navigate to="/login" />;
  
  return <>{children}</>;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/dashboard" element={<ProtectedRoute allowedRoles={['Candidate']}><Dashboard /></ProtectedRoute>} />
          <Route path="/workspace/:id" element={<ProtectedRoute allowedRoles={['Candidate']}><Workspace /></ProtectedRoute>} />
          <Route path="/assessments" element={<ProtectedRoute allowedRoles={['Candidate']}><CandidateAssessments /></ProtectedRoute>} />
          <Route path="/assessment/:id" element={<ProtectedRoute allowedRoles={['Candidate']}><TakeAssessment /></ProtectedRoute>} />
          
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['Administrator', 'AssessmentManager']}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/create-challenge" element={<ProtectedRoute allowedRoles={['Administrator', 'AssessmentManager']}><CreateChallenge /></ProtectedRoute>} />
          <Route path="/admin/create-assessment" element={<ProtectedRoute allowedRoles={['Administrator', 'AssessmentManager']}><CreateAssessment /></ProtectedRoute>} />
          <Route path="/admin/analytics" element={<ProtectedRoute allowedRoles={['Administrator', 'AssessmentManager']}><Analytics /></ProtectedRoute>} />
          
          <Route path="/leaderboard" element={<ProtectedRoute allowedRoles={['Candidate', 'Administrator', 'AssessmentManager']}><Leaderboard /></ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;