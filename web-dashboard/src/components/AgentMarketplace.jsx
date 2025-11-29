/**
 * AgentMarketplace.jsx - AI Agent Selection and Hiring Interface
 *
 * This component provides a marketplace where users can browse, select,
 * and hire AI agents for their test automation needs.
 */

import { useState, useEffect } from 'react'

// Agent categories and their descriptions
const AGENT_CATEGORIES = {
  discovery: {
    name: 'Discovery Agents',
    description: 'Analyze web applications and discover testable elements',
    icon: '🔍'
  },
  creation: {
    name: 'Test Creation Agents',
    description: 'Generate comprehensive test suites from requirements',
    icon: '✍️'
  },
  execution: {
    name: 'Execution Agents',
    description: 'Run tests across different environments and browsers',
    icon: '🚀'
  },
  review: {
    name: 'Review Agents',
    description: 'Review and optimize test quality',
    icon: '📋'
  },
  specialized: {
    name: 'Specialized Agents',
    description: 'Performance, security, and accessibility testing',
    icon: '⚡'
  }
}

// Available agents with their capabilities and pricing
const AVAILABLE_AGENTS = [
  {
    id: 'enhanced-discovery',
    name: 'Enhanced Discovery Agent',
    category: 'discovery',
    description: 'Advanced application analysis using real browser automation. Discovers elements, user journeys, and business logic patterns.',
    capabilities: [
      'Real browser element discovery',
      'Technology stack detection',
      'User journey mapping',
      'Accessibility analysis',
      'Performance indicators'
    ],
    tier: 'professional',
    popularity: 95,
    successRate: 98.5,
    avgResponseTime: '2.5s'
  },
  {
    id: 'real-browser-discovery',
    name: 'Real Browser Discovery Agent',
    category: 'discovery',
    description: 'Playwright-based discovery for accurate DOM element extraction and selector generation.',
    capabilities: [
      'Playwright browser automation',
      'XPath and CSS selector generation',
      'Screenshot capture',
      'Form analysis'
    ],
    tier: 'starter',
    popularity: 88,
    successRate: 96.2,
    avgResponseTime: '3.2s'
  },
  {
    id: 'integrated-generator',
    name: 'Integrated Test Generator',
    category: 'creation',
    description: 'Three-tier test generation with AutoGen collaboration. Creates comprehensive test suites.',
    capabilities: [
      'Three-tier test architecture',
      'AutoGen collaboration',
      'Intelligent flow analysis',
      'Quality assessment',
      'Multiple framework support'
    ],
    tier: 'enterprise',
    popularity: 92,
    successRate: 97.8,
    avgResponseTime: '5.0s'
  },
  {
    id: 'test-creation',
    name: 'Test Creation Agent',
    category: 'creation',
    description: 'Creates test cases from requirements and discovered elements.',
    capabilities: [
      'Requirements analysis',
      'Test case generation',
      'Page object model',
      'Test data generation'
    ],
    tier: 'starter',
    popularity: 90,
    successRate: 95.5,
    avgResponseTime: '3.8s'
  },
  {
    id: 'execution-agent',
    name: 'Test Execution Agent',
    category: 'execution',
    description: 'Runs tests with real-time monitoring and result collection.',
    capabilities: [
      'Parallel execution',
      'Real-time monitoring',
      'Screenshot on failure',
      'Result aggregation'
    ],
    tier: 'professional',
    popularity: 85,
    successRate: 99.1,
    avgResponseTime: '1.2s'
  },
  {
    id: 'review-agent',
    name: 'Test Review Agent',
    category: 'review',
    description: 'Reviews generated tests for quality, coverage, and best practices.',
    capabilities: [
      'Code quality analysis',
      'Coverage assessment',
      'Best practices check',
      'Improvement suggestions'
    ],
    tier: 'professional',
    popularity: 78,
    successRate: 94.5,
    avgResponseTime: '2.1s'
  },
  {
    id: 'self-healing',
    name: 'Self-Healing Agent',
    category: 'specialized',
    description: 'Automatically fixes broken selectors and adapts tests to UI changes.',
    capabilities: [
      'Selector self-healing',
      'UI change detection',
      'Automatic test updates',
      'Change history tracking'
    ],
    tier: 'enterprise',
    popularity: 82,
    successRate: 91.2,
    avgResponseTime: '4.5s'
  },
  {
    id: 'performance-agent',
    name: 'Performance Testing Agent',
    category: 'specialized',
    description: 'Analyzes and generates performance tests.',
    capabilities: [
      'Load testing',
      'Response time analysis',
      'Resource monitoring',
      'Performance recommendations'
    ],
    tier: 'enterprise',
    popularity: 75,
    successRate: 93.0,
    avgResponseTime: '6.0s'
  },
  {
    id: 'cross-browser',
    name: 'Cross-Browser Agent',
    category: 'specialized',
    description: 'Manages cross-browser test execution and compatibility.',
    capabilities: [
      'Multi-browser support',
      'Browser matrix planning',
      'Compatibility analysis',
      'Visual regression'
    ],
    tier: 'professional',
    popularity: 80,
    successRate: 97.2,
    avgResponseTime: '3.5s'
  }
]

const TIER_BADGES = {
  free: { label: 'Free', className: 'bg-gray-100 text-gray-800' },
  starter: { label: 'Starter', className: 'bg-blue-100 text-blue-800' },
  professional: { label: 'Pro', className: 'bg-purple-100 text-purple-800' },
  enterprise: { label: 'Enterprise', className: 'bg-amber-100 text-amber-800' }
}

const AgentMarketplace = ({ user, onHireAgent, currentSubscription = 'trial' }) => {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAgents, setSelectedAgents] = useState([])
  const [showHireModal, setShowHireModal] = useState(false)
  const [agentToHire, setAgentToHire] = useState(null)

  // Filter agents based on category and search
  const filteredAgents = AVAILABLE_AGENTS.filter(agent => {
    const matchesCategory = selectedCategory === 'all' || agent.category === selectedCategory
    const matchesSearch = searchQuery === '' ||
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  // Check if user can access agent based on subscription
  const canAccessAgent = (agent) => {
    const tierOrder = ['free', 'starter', 'professional', 'enterprise']
    const userTierIndex = tierOrder.indexOf(currentSubscription)
    const agentTierIndex = tierOrder.indexOf(agent.tier)
    return userTierIndex >= agentTierIndex
  }

  const handleHireAgent = (agent) => {
    if (!canAccessAgent(agent)) {
      alert(`Upgrade to ${agent.tier} plan to access this agent.`)
      return
    }
    setAgentToHire(agent)
    setShowHireModal(true)
  }

  const confirmHire = () => {
    if (agentToHire) {
      setSelectedAgents([...selectedAgents, agentToHire.id])
      if (onHireAgent) {
        onHireAgent(agentToHire)
      }
      setShowHireModal(false)
      setAgentToHire(null)
    }
  }

  const toggleAgentSelection = (agentId) => {
    if (selectedAgents.includes(agentId)) {
      setSelectedAgents(selectedAgents.filter(id => id !== agentId))
    } else {
      setSelectedAgents([...selectedAgents, agentId])
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Agent Marketplace</h1>
          <p className="text-gray-600">
            Browse and hire AI agents for your test automation needs.
            Select agents that match your requirements and subscription tier.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search agents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedCategory === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All Agents
              </button>
              {Object.entries(AGENT_CATEGORIES).map(([key, cat]) => (
                <button
                  key={key}
                  onClick={() => setSelectedCategory(key)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    selectedCategory === key
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat.icon} {cat.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Selected Agents Summary */}
        {selectedAgents.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-semibold text-blue-800">
                  {selectedAgents.length} agent(s) selected
                </span>
                <span className="text-blue-600 ml-2">
                  Ready to configure your test workflow
                </span>
              </div>
              <button
                onClick={() => setSelectedAgents([])}
                className="text-blue-600 hover:text-blue-800"
              >
                Clear selection
              </button>
            </div>
          </div>
        )}

        {/* Agent Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map(agent => (
            <div
              key={agent.id}
              className={`bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-[1.02] ${
                selectedAgents.includes(agent.id) ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {/* Agent Header */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 text-white">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-2xl">
                      {AGENT_CATEGORIES[agent.category]?.icon}
                    </span>
                    <h3 className="text-lg font-semibold mt-1">{agent.name}</h3>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${TIER_BADGES[agent.tier].className}`}>
                    {TIER_BADGES[agent.tier].label}
                  </span>
                </div>
              </div>

              {/* Agent Body */}
              <div className="p-4">
                <p className="text-gray-600 text-sm mb-4">{agent.description}</p>

                {/* Capabilities */}
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Capabilities</h4>
                  <ul className="space-y-1">
                    {agent.capabilities.slice(0, 3).map((cap, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-center">
                        <span className="text-green-500 mr-2">✓</span>
                        {cap}
                      </li>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <li className="text-sm text-blue-600">
                        +{agent.capabilities.length - 3} more
                      </li>
                    )}
                  </ul>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 mb-4 text-center">
                  <div className="bg-gray-50 rounded p-2">
                    <div className="text-lg font-bold text-blue-600">{agent.successRate}%</div>
                    <div className="text-xs text-gray-500">Success</div>
                  </div>
                  <div className="bg-gray-50 rounded p-2">
                    <div className="text-lg font-bold text-green-600">{agent.popularity}</div>
                    <div className="text-xs text-gray-500">Popularity</div>
                  </div>
                  <div className="bg-gray-50 rounded p-2">
                    <div className="text-lg font-bold text-purple-600">{agent.avgResponseTime}</div>
                    <div className="text-xs text-gray-500">Avg Time</div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={() => toggleAgentSelection(agent.id)}
                    className={`flex-1 py-2 rounded-lg transition-colors ${
                      selectedAgents.includes(agent.id)
                        ? 'bg-blue-100 text-blue-700 border border-blue-300'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {selectedAgents.includes(agent.id) ? 'Selected' : 'Select'}
                  </button>
                  <button
                    onClick={() => handleHireAgent(agent)}
                    disabled={!canAccessAgent(agent)}
                    className={`flex-1 py-2 rounded-lg transition-colors ${
                      canAccessAgent(agent)
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    {canAccessAgent(agent) ? 'Hire Agent' : 'Upgrade Required'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredAgents.length === 0 && (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">No agents found</h3>
            <p className="text-gray-500">Try adjusting your search or filter criteria.</p>
          </div>
        )}

        {/* Hire Modal */}
        {showHireModal && agentToHire && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Hire {agentToHire.name}?
              </h3>
              <p className="text-gray-600 mb-4">
                This agent will be added to your workspace and available for test automation tasks.
              </p>
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-gray-700 mb-2">Agent will handle:</h4>
                <ul className="space-y-1">
                  {agentToHire.capabilities.map((cap, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-center">
                      <span className="text-green-500 mr-2">✓</span>
                      {cap}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowHireModal(false)}
                  className="flex-1 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmHire}
                  className="flex-1 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Confirm Hire
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AgentMarketplace
