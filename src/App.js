import React, { useState } from 'react';
import './App.css';
import Map from './components/Map';
import ProjectDetails from './components/projectDetails.js';

function App() {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [noRouteFound, setNoRouteFound] = useState(false); // State to track if no route was found

  const fetchRouteData = async (params) => {
    try {
      setLoading(true);
      setError(null);
      setNoRouteFound(false); // Reset no route found state

      const response = await fetch('http://localhost:5000/api/route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();

      // Check if no valid route was found
      if (!data.success) {
        setNoRouteFound(true); // Set state if no route is found
        return;
      }

      setRouteData(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching route data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>Ship Route Planner</h1>
      </header>

      {/* Main content */}
      <div className="main-content">
        {/* Sidebar */}
        <div className="sidebar">
          <ProjectDetails 
            onSubmit={fetchRouteData}
            loading={loading}
          />
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {noRouteFound && ( // Display message if no route is found
            <div className="no-route-message">
              No valid route found with the given fuel constraint.
            </div>
          )}

          {routeData && (
            <div className="route-summary">
              <h2>Route Summary</h2>
              <div className="summary-content">
                <p>Total Ports: {routeData.path.length}</p>
                <p>Start: {routeData.ports[0].name}</p>
                <p>End: {routeData.ports[routeData.ports.length - 1].name}</p>
              </div>
            </div>
          )}
        </div>

        {/* Map Section */}
        <div className="map-section">
          {loading ? (
            <div className="loading-spinner-container">
              <div className="loading-spinner"></div>
            </div>
          ) : (
            <Map routeData={routeData} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;