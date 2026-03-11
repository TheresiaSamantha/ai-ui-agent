import { useState, useEffect, useRef } from "react";
import "./App.css";

const ACTION_COLORS = {
  NAVIGATE: "bg-blue-100 text-blue-800 border-blue-300",
  CLICK: "bg-green-100 text-green-800 border-green-300",
  INPUT: "bg-yellow-100 text-yellow-800 border-yellow-300",
  SUBMIT: "bg-purple-100 text-purple-800 border-purple-300",
  VERIFY: "bg-orange-100 text-orange-800 border-orange-300",
  LOCATE: "bg-pink-100 text-pink-800 border-pink-300",
  COMPLETE: "bg-teal-100 text-teal-800 border-teal-300",
};

function App() {
  const [prompt, setPrompt] = useState("");
  const [selectedFile, setSelectedFile] = useState("");
  const [files, setFiles] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [steps, setSteps] = useState([]);
  const [taskTitle, setTaskTitle] = useState("");
  const [error, setError] = useState("");
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const wsRef = useRef(null);

  // Fetch available files on mount
  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/files");
      if (!response.ok) {
        throw new Error("Backend not running");
      }
      const data = await response.json();
      setFiles(data.files || []);
      if (data.files && data.files.length > 0) {
        setSelectedFile(data.files[0]);
      }
      setConnectionStatus("connected");
      setError("");
    } catch (err) {
      console.log("Error fetching files:", err);
      setConnectionStatus("error");
      setError(
        "⚠️ Backend server is not running. Please start the FastAPI server at http://localhost:8000",
      );
      // Use mock data for development
      const mockFiles = [
        "login_context.json",
        "login.json",
        "login.xml",
        "login_context.md",
      ];
      setFiles(mockFiles);
      setSelectedFile(mockFiles[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsThinking(true);
    setSteps([]);
    setTaskTitle("");
    setError("");

    // If backend not available, use mock data
    if (connectionStatus === "error") {
      showMockResponse();
      return;
    }

    try {
      // Connect to WebSocket for streaming
      const ws = new WebSocket("ws://localhost:8000/ws/task-stream");
      wsRef.current = ws;

      ws.onopen = () => {
        // Send task request
        ws.send(
          JSON.stringify({
            prompt: prompt,
            file: selectedFile,
          }),
        );
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.error) {
          setError(data.error);
          setIsThinking(false);
          return;
        }

        if (data.title) {
          setTaskTitle(data.title);
        }

        if (data.step) {
          setSteps((prev) => [...prev, data.step]);
        }

        if (data.done) {
          setIsThinking(false);
          ws.close();
        }
      };

      ws.onerror = () => {
        setError("WebSocket connection failed. Using REST API fallback...");
        fallbackToRestAPI();
      };

      ws.onclose = () => {
        wsRef.current = null;
      };
    } catch (err) {
      setError("Connection error: " + err.message);
      setIsThinking(false);
    }
  };

  const fallbackToRestAPI = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt,
          file: selectedFile,
        }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();
      setTaskTitle(data.title || "Task Instructions");
      setSteps(data.steps || []);
      setIsThinking(false);
    } catch (err) {
      setError("REST API failed: " + err.message);
      setIsThinking(false);
      showMockResponse();
    }
  };

  const showMockResponse = () => {
    setTaskTitle("Login to Application (Mock Data)");
    const mockSteps = [
      {
        step_number: 1,
        action: "NAVIGATE",
        description: "Open browser and navigate to https://www.saucedemo.com/",
        ui_element: null,
        expected_result: "Login page is displayed",
      },
      {
        step_number: 2,
        action: "LOCATE",
        description: "Find the username input field",
        ui_element: "input#user-name",
        expected_result: "Username field is visible",
      },
      {
        step_number: 3,
        action: "INPUT",
        description: "Enter username 'standard_user'",
        ui_element: "input#user-name",
        expected_result: "Username is entered",
      },
      {
        step_number: 4,
        action: "LOCATE",
        description: "Find the password input field",
        ui_element: "input#password",
        expected_result: "Password field is visible",
      },
      {
        step_number: 5,
        action: "INPUT",
        description: "Enter password 'secret_sauce'",
        ui_element: "input#password",
        expected_result: "Password is entered",
      },
      {
        step_number: 6,
        action: "SUBMIT",
        description: "Click the login button",
        ui_element: "input#login-button",
        expected_result: "Login form is submitted",
      },
      {
        step_number: 7,
        action: "VERIFY",
        description: "Verify successful login and dashboard is displayed",
        ui_element: null,
        expected_result: "User is logged in successfully",
      },
    ];

    mockSteps.forEach((step, index) => {
      setTimeout(() => {
        setSteps((prev) => [...prev, step]);
        if (index === mockSteps.length - 1) {
          setIsThinking(false);
        }
      }, index * 500);
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI UI Agent</h1>
              <p className="mt-1 text-sm text-gray-600">
                Intelligent task instruction generator powered by Gemini
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`w-3 h-3 rounded-full ${connectionStatus === "connected" ? "bg-green-500" : connectionStatus === "error" ? "bg-red-500" : "bg-gray-400"}`}
              ></div>
              <span className="text-sm text-gray-600">
                {connectionStatus === "connected"
                  ? "Connected"
                  : connectionStatus === "error"
                    ? "Offline"
                    : "Connecting..."}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What would you like to do?
              </label>
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g. How do I reset my password? or How do I login?"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                disabled={isThinking}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select UI Context File
              </label>
              <select
                value={selectedFile}
                onChange={(e) => setSelectedFile(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                disabled={isThinking}
              >
                {files.length === 0 ? (
                  <option>Loading files...</option>
                ) : (
                  files.map((file) => (
                    <option key={file} value={file}>
                      {file}
                    </option>
                  ))
                )}
              </select>
            </div>

            <button
              type="submit"
              disabled={isThinking || !prompt.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 transform hover:scale-[1.02] disabled:hover:scale-100"
            >
              {isThinking
                ? "Generating Instructions..."
                : "Generate Task Instructions"}
            </button>
          </form>
        </div>

        {/* Thinking Indicator */}
        {isThinking && steps.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-8 mb-8 text-center">
            <div className="inline-block">
              <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600 font-medium pulse-animation">
                AI is thinking and analyzing the UI context...
              </p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {(taskTitle || steps.length > 0) && (
          <div className="bg-white rounded-lg shadow-md p-6">
            {taskTitle && (
              <div className="mb-6 pb-4 border-b border-gray-200">
                <h2 className="text-2xl font-bold text-gray-900">
                  {taskTitle}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  {steps.length} of 7 steps {isThinking && "(generating...)"}
                </p>
              </div>
            )}

            <div className="space-y-4">
              {steps.map((step, index) => (
                <div
                  key={index}
                  className="fade-in-up border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow duration-200"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold">
                        {step.step_number}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold border ${ACTION_COLORS[step.action] || "bg-gray-100 text-gray-800 border-gray-300"}`}
                        >
                          {step.action}
                        </span>
                        {step.ui_element && (
                          <code className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-700">
                            {step.ui_element}
                          </code>
                        )}
                      </div>
                      <p className="text-gray-900 font-medium mb-1">
                        {step.description}
                      </p>
                      <p className="text-sm text-gray-600 italic">
                        Expected: {step.expected_result}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {isThinking && steps.length > 0 && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center space-x-2 text-gray-600">
                  <div className="w-5 h-5 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                  <span className="text-sm">Generating more steps...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-sm text-gray-600">
        <p>Powered by Gemini 2.5 Flash • Built with FastAPI & React</p>
      </footer>
    </div>
  );
}

export default App;
