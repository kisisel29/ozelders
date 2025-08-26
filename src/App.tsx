import React from 'react'
import { Calculator } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <div className="flex items-center justify-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Calculator className="w-8 h-8 text-white" />
            </div>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Math Tutor Platform
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            A comprehensive tutoring platform designed for grades 5-8. The backend API is running on FastAPI with Firebase integration.
          </p>
          
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Platform Features</h2>
            <div className="grid md:grid-cols-2 gap-6 text-left">
              <div>
                <h3 className="font-semibold text-blue-600 mb-2">For Teachers</h3>
                <ul className="text-gray-600 space-y-1">
                  <li>• Create and manage classes</li>
                  <li>• Upload assignments (PDF/images)</li>
                  <li>• Automatic scoring system</li>
                  <li>• Student progress analytics</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-purple-600 mb-2">For Students</h3>
                <ul className="text-gray-600 space-y-1">
                  <li>• Interactive assignments</li>
                  <li>• Math games and challenges</li>
                  <li>• Progress tracking</li>
                  <li>• Instant feedback</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <p className="text-blue-800">
                <strong>Note:</strong> This is the React frontend placeholder. The main application runs on FastAPI with server-rendered templates at the API endpoints.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App