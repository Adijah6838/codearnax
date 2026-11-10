import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { api } from '../api';

const STARTER_CODE: Record<string, string> = {
  python: `# Read input from standard input (stdin)\nimport sys\n\ndef solve():\n    # Write your code here\n    pass\n\nif __name__ == '__main__':\n    solve()`,
  javascript: `// Read input from standard input (stdin)\nconst fs = require('fs');\nconst input = fs.readFileSync(0, 'utf-8').trim();\n\n// Write your code here\n`,
  cpp: `#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your code here\n    return 0;\n}`
};

export default function Workspace() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [challenge, setChallenge] = useState<any>(null);
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState(STARTER_CODE['python']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentSubmissionId, setCurrentSubmissionId] = useState<number | null>(null);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const fetchChallenge = async () => {
      try {
        const res = await api.get(`/challenges/${id}`);
        setChallenge(res.data);
      } catch (err) {
        navigate('/dashboard');
      }
    };
    fetchChallenge();
  }, [id, navigate]);

  // WebSocket Listener for Instant Updates
  useEffect(() => {
    const ws = new WebSocket('ws://127.0.0.1:8010/ws/monitor');
    
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      
      // If the update is for the current submission we are looking at
      if (data.event === 'submission_update' && data.submission_id === currentSubmissionId) {
        if (data.status === 'Running') {
          setResult({ status: 'Running' });
        } else {
          // If it's a final status (Accepted, WrongAnswer, etc.), fetch results
          const resultsRes = await api.get(`/submissions/${currentSubmissionId}/results`);
          setResult({
            status: data.status,
            tests: resultsRes.data
          });
          setIsSubmitting(false);
          setCurrentSubmissionId(null);
        }
      }
    };

    return () => ws.close();
  }, [currentSubmissionId]);

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const lang = e.target.value;
    setLanguage(lang);
    setCode(STARTER_CODE[lang]);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setResult(null);
    try {
      const res = await api.post('/submissions', {
        challenge_id: Number(id),
        language: language,
        source_code: code
      });
      
      setCurrentSubmissionId(res.data.id);
      setResult({ status: 'Queued' });
      
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Submission failed');
      setIsSubmitting(false);
    }
  };

  if (!challenge) return <div className="text-white p-8">Loading...</div>;

  return (
    <div className="h-screen flex flex-col bg-slate-900">
      {/* Top Bar */}
      <div className="h-14 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/dashboard')} className="text-slate-400 hover:text-white">&larr; Back</button>
          <h1 className="text-white font-semibold">{challenge.title}</h1>
        </div>
        <div className="flex items-center gap-4">
          <select 
            value={language} 
            onChange={handleLanguageChange}
            className="bg-slate-900 text-white border border-slate-600 rounded px-3 py-1 text-sm outline-none"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="cpp">C++</option>
          </select>
          <button 
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-1.5 rounded font-medium text-sm disabled:opacity-50"
          >
            {isSubmitting ? 'Running...' : 'Submit Code'}
          </button>
        </div>
      </div>

      {/* Main Split Area */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left: Problem Description */}
        <div className="w-1/3 border-r border-slate-700 p-6 overflow-y-auto bg-slate-800/50">
          <h2 className="text-xl font-bold text-white mb-4">Description</h2>
          <p className="text-slate-300 whitespace-pre-wrap mb-6">{challenge.description}</p>
          
          {challenge.input_spec && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-white mb-1">Input</h3>
              <p className="text-slate-400 text-sm">{challenge.input_spec}</p>
            </div>
          )}
          
          {challenge.output_spec && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-white mb-1">Output</h3>
              <p className="text-slate-400 text-sm">{challenge.output_spec}</p>
            </div>
          )}

          {result && (
            <div className={`mt-8 p-4 rounded-lg border ${
              result.status === 'Accepted' ? 'bg-green-500/10 border-green-500 text-green-400' :
              result.status === 'Running' || result.status === 'Queued' ? 'bg-blue-500/10 border-blue-500 text-blue-400' :
              'bg-red-500/10 border-red-500 text-red-400'
            }`}>
              <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                {result.status === 'Running' && <span className="animate-spin text-xl">↻</span>}
                {result.status}
              </h3>
              {result.tests && (
                <p className="text-sm">Passed {result.tests.filter((t: any) => t.passed).length} / {result.tests.length} test cases.</p>
              )}
            </div>
          )}
        </div>

        {/* Right: Monaco Editor */}
        <div className="w-2/3 flex flex-col">
          <Editor
            height="100%"
            language={language === 'cpp' ? 'cpp' : language}
            theme="vs-dark"
            value={code}
            onChange={(val) => setCode(val || '')}
            options={{
              minimap: { enabled: false },
              fontSize: 16,
              padding: { top: 20 },
              scrollBeyondLastLine: false,
            }}
          />
        </div>

      </div>
    </div>
  );
}