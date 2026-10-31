import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LoginPage } from './pages/LoginPage';
import { OverviewPage } from './pages/OverviewPage';
import { PlaygroundPage } from './pages/PlaygroundPage';
import { RoutingDecisionsPage } from './pages/RoutingDecisionsPage';
import { ModelRegistryPage } from './pages/ModelRegistryPage';
import { LiveArenaPage } from './pages/LiveArenaPage';
import { FinOpsAnalyticsPage } from './pages/FinOpsAnalyticsPage';
import { PolicySimulatorPage } from './pages/PolicySimulatorPage';
import { AdaptiveLearningPage } from './pages/AdaptiveLearningPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { AuditHistoryPage } from './pages/AuditHistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';
import { SystemHealth } from './types';

export const App: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [activeRecCount, setActiveRecCount] = useState<number>(0);
  // Default to true so demo presentation is seamless; allows logging out to test login
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return localStorage.getItem('astraroute_demo_auth') !== 'false';
  });

  const fetchActiveRecommendations = async () => {
    try {
      const recs = await api.getRecommendations();
      const pendingCount = (recs || []).filter((r: any) => r.status === 'pending').length;
      setActiveRecCount(pendingCount);
    } catch (e) {
      console.error('Failed to fetch recommendation count:', e);
    }
  };

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch((err) => console.error('Health fetch error:', err));
    fetchActiveRecommendations();

    const handleUpdate = () => {
      fetchActiveRecommendations();
    };
    window.addEventListener('recommendations-updated', handleUpdate);
    return () => window.removeEventListener('recommendations-updated', handleUpdate);
  }, []);

  const handleLogin = () => {
    localStorage.setItem('astraroute_demo_auth', 'true');
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.setItem('astraroute_demo_auth', 'false');
    setIsAuthenticated(false);
  };

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      {!isAuthenticated ? (
        <LoginPage onLogin={handleLogin} />
      ) : (
        <div className="min-h-screen bg-surface-ground flex flex-col font-sans">
          
          {/* Stationary Top Navbar */}
          <Navbar 
            health={health} 
            onLogout={handleLogout}
            isAuthenticated={isAuthenticated}
          />

          {/* Main Layout Area with Fixed Sidebar */}
          <div className="flex flex-1">
            {/* Fixed Stationary Sidebar */}
            <Sidebar recommendationCount={activeRecCount} />

            {/* Main Content Area - Full Available Viewport Width */}
            <main className="ml-0 md:ml-64 mt-16 p-6 md:p-8 min-h-[calc(100vh-4rem)] w-full md:w-[calc(100%-16rem)]">
              <Routes>
                <Route path="/" element={<OverviewPage />} />
                <Route path="/playground" element={<PlaygroundPage />} />
                <Route path="/decisions" element={<RoutingDecisionsPage />} />
                <Route path="/models" element={<ModelRegistryPage />} />
                <Route path="/arena" element={<LiveArenaPage />} />
                <Route path="/finops" element={<FinOpsAnalyticsPage />} />
                <Route path="/simulator" element={<PolicySimulatorPage />} />
                <Route path="/adaptation" element={<AdaptiveLearningPage />} />
                <Route path="/recommendations" element={<RecommendationsPage />} />
                <Route path="/audit" element={<AuditHistoryPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>

        </div>
      )}
    </BrowserRouter>
  );
};

export default App;
