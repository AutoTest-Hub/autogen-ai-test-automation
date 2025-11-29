import React, { useState, useEffect } from 'react'

function SimpleTest() {
  const [systemInfo, setSystemInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        console.log('Fetching system info...')
        const response = await fetch('http://localhost:8000/api/v1/system/info')
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('System info received:', data)
        setSystemInfo(data)
      } catch (err) {
        console.error('Error fetching system info:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchSystemInfo()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">AI Test Automation Platform</h1>
          <p className="text-gray-600">Loading system information...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4 text-red-600">Error</h1>
          <p className="text-gray-600">Failed to load system info: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center max-w-2xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-4">
          {systemInfo?.branding?.name || 'AI Test Automation Platform'}
        </h1>
        <p className="text-gray-600 mb-6">
          {systemInfo?.branding?.edition || 'Loading...'}
        </p>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">System Information</h2>
          <div className="grid grid-cols-2 gap-4 text-left">
            <div>
              <strong>Deployment Mode:</strong> {systemInfo?.deployment_mode}
            </div>
            <div>
              <strong>Version:</strong> {systemInfo?.version}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Available Features</h2>
          <div className="grid grid-cols-2 gap-2 text-left text-sm">
            {systemInfo?.features && Object.entries(systemInfo.features).map(([key, value]) => (
              <div key={key} className={`flex items-center ${value ? 'text-green-600' : 'text-gray-400'}`}>
                <span className="mr-2">{value ? '✓' : '✗'}</span>
                {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
          >
            Reload
          </button>
        </div>
      </div>
    </div>
  )
}

export default SimpleTest
