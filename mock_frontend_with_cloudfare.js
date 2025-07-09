// Install the use-mcp hook
// npm install @cloudflare/use-mcp

import { useMCP } from '@cloudflare/use-mcp';
import { useState, useEffect } from 'react';

export default function EmailTelegramDashboard() {
  const [serverUrl, setServerUrl] = useState('http://localhost:3001/mcp');
  const [activeTab, setActiveTab] = useState('emails');
  
  // Connect to MCP server in 3 lines of code
  const { 
    isConnected, 
    tools, 
    resources, 
    prompts, 
    callTool, 
    error 
  } = useMCP(serverUrl);

  // State for various features
  const [emails, setEmails] = useState([]);
  const [telegramMessages, setTelegramMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});

  // Tool execution wrapper
  const executeTool = async (toolName, args = {}) => {
    setLoading(true);
    try {
      const result = await callTool(toolName, args);
      setResults(prev => ({ ...prev, [toolName]: result }));
      return result;
    } catch (err) {
      console.error(`Error calling ${toolName}:`, err);
      setResults(prev => ({ ...prev, [toolName]: { error: err.message } }));
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch data on connection
  useEffect(() => {
    if (isConnected) {
      executeTool('get_latest_emails').then(setEmails);
      executeTool('get_telegram_messages').then(setTelegramMessages);
    }
  }, [isConnected]);

  if (error) {
    return <ErrorView error={error} />;
  }

  if (!isConnected) {
    return <ConnectionView serverUrl={serverUrl} setServerUrl={setServerUrl} />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                📧 Email & Telegram Assistant
              </h1>
              <div className="ml-4 flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Connected to MCP</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {tools?.length || 0} tools available
              </span>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['emails', 'telegram', 'ai-chat', 'tools'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'emails' && (
          <EmailsTab 
            emails={emails} 
            executeTool={executeTool} 
            loading={loading}
            results={results}
          />
        )}
        
        {activeTab === 'telegram' && (
          <TelegramTab 
            messages={telegramMessages} 
            executeTool={executeTool} 
            loading={loading}
            results={results}
          />
        )}
        
        {activeTab === 'ai-chat' && (
          <AIChatTab 
            executeTool={executeTool} 
            loading={loading}
            results={results}
          />
        )}
        
        {activeTab === 'tools' && (
          <ToolsTab 
            tools={tools} 
            resources={resources} 
            prompts={prompts}
            executeTool={executeTool}
            loading={loading}
            results={results}
          />
        )}
      </main>

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="text-gray-700">Processing...</span>
          </div>
        </div>
      )}
    </div>
  );
}

// Tab Components
function EmailsTab({ emails, executeTool, loading, results }) {
  const [emailForm, setEmailForm] = useState({ subject: '', to: '', body: '' });
  const [classifySubject, setClassifySubject] = useState('');

  return (
    <div className="space-y-6">
      {/* Email Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Send Email */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Send Email</h2>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Subject"
              value={emailForm.subject}
              onChange={(e) => setEmailForm(prev => ({ ...prev, subject: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
            <input
              type="email"
              placeholder="To"
              value={emailForm.to}
              onChange={(e) => setEmailForm(prev => ({ ...prev, to: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
            <textarea
              placeholder="Email body"
              value={emailForm.body}
              onChange={(e) => setEmailForm(prev => ({ ...prev, body: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md h-32"
            />
            <button
              onClick={() => executeTool('send_emails', emailForm)}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Send Email
            </button>
          </div>
        </div>

        {/* Classify Subject */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Classify Email Subject</h2>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Enter email subject to classify"
              value={classifySubject}
              onChange={(e) => setClassifySubject(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
            <button
              onClick={() => executeTool('classify_subject', { subject: classifySubject })}
              disabled={loading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              Classify Subject
            </button>
            {results.classify_subject && (
              <div className="mt-4 p-3 bg-gray-50 rounded-md">
                <pre className="text-sm">{JSON.stringify(results.classify_subject, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Latest Emails */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Latest Emails</h2>
          <button
            onClick={() => executeTool('get_latest_emails')}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
        
        {results.get_latest_emails && (
          <div className="space-y-4">
            {Array.isArray(results.get_latest_emails) ? (
              results.get_latest_emails.map((email, index) => (
                <div key={index} className="border border-gray-200 rounded-md p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold">{email.subject}</h3>
                    <span className="text-sm text-gray-500">{email.date}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">From: {email.from}</p>
                  <p className="text-sm text-gray-700">{email.preview}</p>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No emails found or unexpected format</p>
                <pre className="mt-2 text-xs">{JSON.stringify(results.get_latest_emails, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function TelegramTab({ messages, executeTool, loading, results }) {
  const [messageForm, setMessageForm] = useState({ to: '', body: '' });

  return (
    <div className="space-y-6">
      {/* Send Telegram Message */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Send Telegram Message</h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="To (username or chat ID)"
            value={messageForm.to}
            onChange={(e) => setMessageForm(prev => ({ ...prev, to: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <textarea
            placeholder="Message"
            value={messageForm.body}
            onChange={(e) => setMessageForm(prev => ({ ...prev, body: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md h-32"
          />
          <button
            onClick={() => executeTool('send_telegram_messages', messageForm)}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            Send Message
          </button>
        </div>
      </div>

      {/* Recent Messages */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recent Messages</h2>
          <button
            onClick={() => executeTool('get_telegram_messages')}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
        
        {results.get_telegram_messages && (
          <div className="space-y-4">
            <pre className="text-sm bg-gray-50 p-4 rounded-md overflow-x-auto">
              {JSON.stringify(results.get_telegram_messages, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

function AIChatTab({ executeTool, loading, results }) {
  const [prompt, setPrompt] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const handleChat = async () => {
    if (!prompt.trim()) return;
    
    const userMessage = { role: 'user', content: prompt };
    setChatHistory(prev => [...prev, userMessage]);
    
    const response = await executeTool('message_groq', { prompt });
    
    if (response) {
      const assistantMessage = { role: 'assistant', content: response };
      setChatHistory(prev => [...prev, assistantMessage]);
    }
    
    setPrompt('');
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">AI Chat Assistant</h2>
      
      {/* Chat History */}
      <div className="h-96 overflow-y-auto mb-4 p-4 border border-gray-200 rounded-md">
        {chatHistory.map((message, index) => (
          <div key={index} className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-3 rounded-lg max-w-xs ${
              message.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {message.content}
            </div>
          </div>
        ))}
      </div>

      {/* Chat Input */}
      <div className="flex space-x-4">
        <input
          type="text"
          placeholder="Ask me anything about your emails or send messages..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleChat()}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
        />
        <button
          onClick={handleChat}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}

function ToolsTab({ tools, resources, prompts, executeTool, loading, results }) {
  return (
    <div className="space-y-6">
      {/* Available Tools */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Available Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tools?.map((tool, index) => (
            <div key={index} className="border border-gray-200 rounded-md p-4">
              <h3 className="font-medium text-gray-900">{tool.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{tool.description}</p>
              <button
                onClick={() => executeTool(tool.name)}
                disabled={loading}
                className="mt-2 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                Execute
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Resources */}
      {resources && resources.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Resources</h2>
          <div className="space-y-4">
            {resources.map((resource, index) => (
              <div key={index} className="border border-gray-200 rounded-md p-4">
                <h3 className="font-medium text-gray-900">{resource.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{resource.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Prompts */}
      {prompts && prompts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Available Prompts</h2>
          <div className="space-y-4">
            {prompts.map((prompt, index) => (
              <div key={index} className="border border-gray-200 rounded-md p-4">
                <h3 className="font-medium text-gray-900">{prompt.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{prompt.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Components
function ErrorView({ error }) {
  return (
    <div className="min-h-screen bg-red-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <div className="text-center">
          <div className="text-red-600 text-4xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Connection Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    </div>
  );
}

function ConnectionView({ serverUrl, setServerUrl }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <div className="text-center">
          <div className="text-blue-600 text-4xl mb-4">🔗</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Connect to MCP Server</h2>
          <div className="mb-6">
            <input
              type="text"
              value={serverUrl}
              onChange={(e) => setServerUrl(e.target.value)}
              placeholder="MCP Server URL"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Connecting to server...</p>
        </div>
      </div>
    </div>
  );
}
