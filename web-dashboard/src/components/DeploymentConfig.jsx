/**
 * Deployment Configuration Component
 * Handles SaaS vs OnPrem deployment differences
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

// Deployment modes
export const DEPLOYMENT_MODES = {
  SAAS: 'SaaS',
  ONPREM: 'OnPrem'
};

// Deployment context
const DeploymentContext = createContext();

export const useDeployment = () => {
  const context = useContext(DeploymentContext);
  if (!context) {
    throw new Error('useDeployment must be used within a DeploymentProvider');
  }
  return context;
};

export const DeploymentProvider = ({ children }) => {
  const [deploymentMode, setDeploymentMode] = useState(DEPLOYMENT_MODES.SAAS);
  const [features, setFeatures] = useState({});
  const [branding, setBranding] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Detect deployment mode from environment or API
    const detectDeploymentMode = async () => {
      try {
        // Check environment variable first
        const envMode = import.meta.env.VITE_DEPLOYMENT_MODE;
        if (envMode) {
          setDeploymentMode(envMode);
        }

        // Fetch system info from API
        const response = await fetch('/api/system/info', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (response.ok) {
          const systemInfo = await response.json();
          setDeploymentMode(systemInfo.deployment_mode);
          setFeatures(systemInfo.features_enabled || {});
        }
      } catch (error) {
        console.warn('Could not detect deployment mode:', error);
        // Default to SaaS mode
        setDeploymentMode(DEPLOYMENT_MODES.SAAS);
      } finally {
        setLoading(false);
      }
    };

    detectDeploymentMode();
  }, []);

  useEffect(() => {
    // Set deployment-specific features and branding
    if (deploymentMode === DEPLOYMENT_MODES.SAAS) {
      setFeatures({
        billing: true,
        userRegistration: true,
        multiTenant: true,
        subscriptionPlans: true,
        publicSignup: true,
        marketingPages: true,
        usageAnalytics: true,
        cloudIntegrations: true,
        autoScaling: true,
        globalCDN: true
      });

      setBranding({
        title: 'AI Test Automation Platform',
        subtitle: 'Enterprise-grade test automation powered by AI',
        logo: '/logo-saas.svg',
        primaryColor: '#3b82f6',
        secondaryColor: '#1e40af',
        theme: 'modern',
        showPoweredBy: false,
        customDomain: true,
        whiteLabel: false
      });
    } else {
      setFeatures({
        billing: false,
        userRegistration: false,
        multiTenant: false,
        subscriptionPlans: false,
        publicSignup: false,
        marketingPages: false,
        usageAnalytics: true,
        cloudIntegrations: false,
        autoScaling: false,
        globalCDN: false,
        ldapIntegration: true,
        customBranding: true,
        airGappedMode: true,
        enterpriseSecurity: true,
        auditCompliance: true,
        customReports: true
      });

      setBranding({
        title: 'Enterprise Test Automation',
        subtitle: 'On-premises AI-powered quality engineering',
        logo: '/logo-enterprise.svg',
        primaryColor: '#059669',
        secondaryColor: '#047857',
        theme: 'enterprise',
        showPoweredBy: true,
        customDomain: false,
        whiteLabel: true
      });
    }
  }, [deploymentMode]);

  const value = {
    deploymentMode,
    features,
    branding,
    loading,
    isSaaS: deploymentMode === DEPLOYMENT_MODES.SAAS,
    isOnPrem: deploymentMode === DEPLOYMENT_MODES.ONPREM
  };

  return (
    <DeploymentContext.Provider value={value}>
      {children}
    </DeploymentContext.Provider>
  );
};

// Feature gate component
export const FeatureGate = ({ feature, children, fallback = null }) => {
  const { features } = useDeployment();
  
  if (features[feature]) {
    return children;
  }
  
  return fallback;
};

// Deployment-specific styling hook
export const useDeploymentStyles = () => {
  const { branding, deploymentMode } = useDeployment();
  
  return {
    primaryColor: branding.primaryColor,
    secondaryColor: branding.secondaryColor,
    theme: branding.theme,
    cssVariables: {
      '--primary-color': branding.primaryColor,
      '--secondary-color': branding.secondaryColor,
      '--deployment-mode': deploymentMode.toLowerCase()
    }
  };
};

// Deployment-aware navigation items
export const getNavigationItems = (features) => {
  const baseItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'LayoutDashboard',
      path: '/dashboard'
    },
    {
      id: 'applications',
      label: 'Applications',
      icon: 'Globe',
      path: '/applications'
    },
    {
      id: 'create-test',
      label: 'Create Tests',
      icon: 'Plus',
      path: '/create-test'
    },
    {
      id: 'test-results',
      label: 'Test Results',
      icon: 'BarChart3',
      path: '/test-results'
    }
  ];

  const conditionalItems = [];

  // SaaS-specific items
  if (features.billing) {
    conditionalItems.push({
      id: 'billing',
      label: 'Billing',
      icon: 'CreditCard',
      path: '/billing'
    });
  }

  if (features.subscriptionPlans) {
    conditionalItems.push({
      id: 'subscription',
      label: 'Subscription',
      icon: 'Crown',
      path: '/subscription'
    });
  }

  // OnPrem-specific items
  if (features.ldapIntegration) {
    conditionalItems.push({
      id: 'user-management',
      label: 'User Management',
      icon: 'Users',
      path: '/users'
    });
  }

  if (features.auditCompliance) {
    conditionalItems.push({
      id: 'audit-logs',
      label: 'Audit Logs',
      icon: 'Shield',
      path: '/audit'
    });
  }

  // Common admin items
  conditionalItems.push({
    id: 'settings',
    label: 'Settings',
    icon: 'Settings',
    path: '/settings'
  });

  return [...baseItems, ...conditionalItems];
};

export default DeploymentProvider;
