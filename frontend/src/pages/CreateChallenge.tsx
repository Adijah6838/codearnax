import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';

export default function CreateChallenge() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState('Beginner');
  const [category, setCategory] = useState('Mathematics');
  const [languages, setLanguages] = useState<string[]>(['python', 'javascript', 'cpp']);
  const [inputSpec, setInputSpec] = useState('');
  const [outputSpec, setOutputSpec] = useState('');
  
  // Test cases state
  const [testCases, setTestCases] = useState([
    { input: '', expected_output: '', is_hidden: false }
  ]);

  const handleAddTestCase = () => {
    setTestCases([...testCases, { input: '', expected_output: '', is_hidden: false }]);
  };

  const handleTestCaseChange = (index: number, field: string, value: any) => {
    const updated = [...testCases];
    updated[index] = { ...updated[index], [field]: value };
    setTestCases(updated);
  };

  const handleLanguageToggle = (lang: string) => {
    if (languages.includes(lang)) {
      setLanguages(languages.filter(l => l !== lang));
    } else {
      setLanguages([...languages, lang]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.post('/challenges', {
        title,
        description,
        difficulty,
        category,
        languages,
        input_spec: inputSpec,
        output_spec: outputSpec,
        test_cases: testCases
      });
      navigate('/admin');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create challenge');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-8 text-white">
      <div className="max-w-4xl mx-auto bg-slate-800 rounded-xl shadow-lg border border-slate-700 p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Create New Challenge</h1>
          <button onClick={() => navigate('/admin')} className="text-slate-400 hover:text-white">&larr; Back</button>
        </div>

        {error && <div className="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded mb-4">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Title</label>
              <input required value={title} onChange={e => setTitle(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:border-blue-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Difficulty</label>
              <select value={difficulty} onChange={e => setDifficulty(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg outline-none">
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Advanced</option>
                <option>Expert</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
            <textarea required rows={4} value={description} onChange={e => setDescription(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:border-blue-500 outline-none" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Input Specification</label>
              <textarea rows={2} value={inputSpec} onChange={e => setInputSpec(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Output Specification</label>
              <textarea rows={2} value={outputSpec} onChange={e => setOutputSpec(e.target.value)} className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg outline-none" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Supported Languages</label>
            <div className="flex gap-4">
              {['python', 'javascript', 'cpp'].map(lang => (
                <label key={lang} className="flex items-center gap-2 text-slate-300">
                  <input type="checkbox" checked={languages.includes(lang)} onChange={() => handleLanguageToggle(lang)} className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-blue-500 focus:ring-blue-500" />
                  <span className="capitalize">{lang === 'cpp' ? 'C++' : lang}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-700 pt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Test Cases</h2>
              <button type="button" onClick={handleAddTestCase} className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded">+ Add Test Case</button>
            </div>
            
            {testCases.map((tc, index) => (
              <div key={index} className="flex gap-4 items-start mb-4 bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="flex-1">
                  <label className="block text-xs text-slate-400 mb-1">Input (stdin)</label>
                  <textarea rows={2} value={tc.input} onChange={e => handleTestCaseChange(index, 'input', e.target.value)} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-sm outline-none" />
                </div>
                <div className="flex-1">
                  <label className="block text-xs text-slate-400 mb-1">Expected Output (stdout)</label>
                  <textarea rows={2} value={tc.expected_output} onChange={e => handleTestCaseChange(index, 'expected_output', e.target.value)} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-sm outline-none" />
                </div>
                <div className="pt-6 flex items-center gap-2">
                  <input type="checkbox" checked={tc.is_hidden} onChange={e => handleTestCaseChange(index, 'is_hidden', e.target.checked)} className="w-4 h-4 rounded bg-slate-800 border-slate-600 text-blue-500" />
                  <span className="text-sm text-slate-400">Hidden</span>
                </div>
              </div>
            ))}
          </div>

          <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Challenge'}
          </button>
        </form>
      </div>
    </div>
  );
}