import React, { useState } from 'react';
import { Upload, Plus, Trash2, Download, AlertCircle } from 'lucide-react';

export default function MarketingClassifier() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState([]);
  const [results, setResults] = useState(null);
  const [dictionaries, setDictionaries] = useState({
    urgency_marketing: [
      'limited', 'limited time', 'limited run', 'limited edition', 'order now',
      'last chance', 'hurry', 'while supplies last', "before they're gone",
      'selling out', 'selling fast', 'act now', "don't wait", 'today only',
      'expires soon', 'final hours', 'almost gone'
    ],
    exclusive_marketing: [
      'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
      'members only', 'vip', 'special access', 'invitation only',
      'premium', 'privileged', 'limited access', 'select customers',
      'insider', 'private sale', 'early access'
    ]
  });
  const [newTactic, setNewTactic] = useState('');
  const [newKeyword, setNewKeyword] = useState({});

  const parseCSV = (text) => {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length === 0) return [];
    
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = [];
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const row = {};
      headers.forEach((header, idx) => {
        row[header] = values[idx] || '';
      });
      rows.push(row);
    }
    
    return rows;
  };

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result;
        const parsed = parseCSV(text);
        setData(parsed);
        setResults(null);
      };
      reader.readAsText(uploadedFile);
    }
  };

  const classifyStatement = (text, dicts) => {
    if (!text) return {};
    
    const textLower = text.toLowerCase();
    const results = {};
    
    Object.entries(dicts).forEach(([tactic, keywords]) => {
      const matches = keywords.filter(keyword => 
        textLower.includes(keyword.toLowerCase())
      );
      
      results[tactic] = {
        present: matches.length > 0,
        count: matches.length,
        matches: matches
      };
    });
    
    return results;
  };

  const runClassification = () => {
    if (data.length === 0) return;
    
    const statementColumn = data[0].Statement !== undefined ? 'Statement' : 
                           data[0].statement !== undefined ? 'statement' :
                           Object.keys(data[0])[1]; // Fallback to second column
    
    const classified = data.map(row => {
      const classification = classifyStatement(row[statementColumn], dictionaries);
      return {
        ...row,
        classification
      };
    });
    
    setResults(classified);
  };

  const addTactic = () => {
    if (newTactic && !dictionaries[newTactic]) {
      setDictionaries({
        ...dictionaries,
        [newTactic]: []
      });
      setNewTactic('');
    }
  };

  const removeTactic = (tactic) => {
    const updated = { ...dictionaries };
    delete updated[tactic];
    setDictionaries(updated);
  };

  const addKeyword = (tactic) => {
    const keyword = newKeyword[tactic];
    if (keyword && keyword.trim()) {
      setDictionaries({
        ...dictionaries,
        [tactic]: [...dictionaries[tactic], keyword.trim()]
      });
      setNewKeyword({ ...newKeyword, [tactic]: '' });
    }
  };

  const removeKeyword = (tactic, keyword) => {
    setDictionaries({
      ...dictionaries,
      [tactic]: dictionaries[tactic].filter(k => k !== keyword)
    });
  };

  const downloadResults = () => {
    if (!results) return;
    
    const statementColumn = results[0].Statement !== undefined ? 'Statement' : 
                           results[0].statement !== undefined ? 'statement' :
                           Object.keys(results[0])[1];
    
    const headers = ['ID', statementColumn];
    Object.keys(dictionaries).forEach(tactic => {
      headers.push(`${tactic}_present`, `${tactic}_count`, `${tactic}_matches`);
    });
    
    const rows = results.map(row => {
      const values = [row.ID || row.id || '', row[statementColumn]];
      Object.keys(dictionaries).forEach(tactic => {
        const cls = row.classification[tactic] || {};
        values.push(
          cls.present ? 'TRUE' : 'FALSE',
          cls.count || 0,
          (cls.matches || []).join('; ')
        );
      });
      return values.map(v => `"${v}"`).join(',');
    });
    
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'classified_data.csv';
    a.click();
  };

  const getStatementColumn = () => {
    if (data.length === 0) return 'Statement';
    return data[0].Statement !== undefined ? 'Statement' : 
           data[0].statement !== undefined ? 'statement' :
           Object.keys(data[0])[1];
  };

  const calculateStats = () => {
    if (!results) return null;
    
    const stats = {};
    Object.keys(dictionaries).forEach(tactic => {
      const count = results.filter(r => r.classification[tactic]?.present).length;
      stats[tactic] = {
        count,
        percentage: ((count / results.length) * 100).toFixed(1)
      };
    });
    
    const anyTactic = results.filter(r => 
      Object.values(r.classification).some(c => c.present)
    ).length;
    
    return { tactics: stats, anyTactic, total: results.length };
  };

  const stats = calculateStats();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Marketing Tactic Classifier</h1>
        <p className="text-gray-600 mb-8">Upload your dataset and classify statements using customizable marketing tactic dictionaries</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* File Upload */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Upload Dataset
            </h2>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {data.length > 0 && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">✓ Loaded {data.length} rows</p>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-3">
              <button
                onClick={runClassification}
                disabled={data.length === 0}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
              >
                Run Classification
              </button>
              <button
                onClick={downloadResults}
                disabled={!results}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Results
              </button>
            </div>
          </div>
        </div>

        {/* Dictionary Manager */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Marketing Tactic Dictionaries</h2>
          
          <div className="mb-4 flex gap-2">
            <input
              type="text"
              value={newTactic}
              onChange={(e) => setNewTactic(e.target.value)}
              placeholder="New tactic name (e.g., scarcity_marketing)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={addTactic}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Tactic
            </button>
          </div>

          <div className="space-y-4">
            {Object.entries(dictionaries).map(([tactic, keywords]) => (
              <div key={tactic} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-lg">{tactic}</h3>
                  <button
                    onClick={() => removeTactic(tactic)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={newKeyword[tactic] || ''}
                    onChange={(e) => setNewKeyword({ ...newKeyword, [tactic]: e.target.value })}
                    placeholder="Add keyword..."
                    className="flex-1 px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && addKeyword(tactic)}
                  />
                  <button
                    onClick={() => addKeyword(tactic)}
                    className="bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700 text-sm"
                  >
                    Add
                  </button>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  {keywords.map(keyword => (
                    <span
                      key={keyword}
                      className="bg-gray-100 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                    >
                      {keyword}
                      <button
                        onClick={() => removeKeyword(tactic, keyword)}
                        className="text-gray-500 hover:text-red-600"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Results */}
        {stats && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Classification Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Statements</p>
                <p className="text-2xl font-bold text-blue-700">{stats.total}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">With Any Tactic</p>
                <p className="text-2xl font-bold text-green-700">{stats.anyTactic}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Match Rate</p>
                <p className="text-2xl font-bold text-purple-700">
                  {((stats.anyTactic / stats.total) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            
            <div className="space-y-2">
              {Object.entries(stats.tactics).map(([tactic, data]) => (
                <div key={tactic} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <span className="font-medium">{tactic}</span>
                  <span className="text-sm text-gray-600">
                    {data.count}/{stats.total} ({data.percentage}%)
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {results && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Detailed Results</h2>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {results.map((row, idx) => {
                const statementCol = getStatementColumn();
                const hasMatch = Object.values(row.classification).some(c => c.present);
                
                return (
                  <div key={idx} className={`border rounded-lg p-4 ${hasMatch ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
                    <div className="mb-2">
                      <span className="font-semibold">ID:</span> {row.ID || row.id || idx + 1}
                    </div>
                    <div className="mb-3 text-gray-700">
                      <span className="font-semibold">Statement:</span> {row[statementCol]}
                    </div>
                    <div className="space-y-1">
                      {Object.entries(row.classification).map(([tactic, result]) => (
                        <div key={tactic} className="text-sm">
                          {result.present ? (
                            <span className="text-green-700">
                              ✓ {tactic}: {result.matches.join(', ')}
                            </span>
                          ) : (
                            <span className="text-gray-500">
                              ✗ {tactic}: No matches
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
