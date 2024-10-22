import React, { useState } from 'react';

const ProjectDetails = ({ onSubmit, loading }) => {
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const start = parseInt(formData.get('start'));
    const end = parseInt(formData.get('end'));
    const maxFuel = parseInt(formData.get('maxFuel'));

    // Basic validation
    if (isNaN(start) || isNaN(end) || isNaN(maxFuel)) {
      setError('Please enter valid numbers for all fields.');
      return;
    }

    if (start <= 0 || end <= 0 || maxFuel <= 0) {
      setError('Port IDs and Max Fuel must be positive numbers.');
      return;
    }

    setError(''); // Clear any previous errors
    onSubmit({ start, end, maxFuel });
  };

  return (
    <div className="form-container">
      <h2>Route Parameters</h2>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit} className="route-form">
        <div className="form-group">
          <label htmlFor="start">Start Port ID</label>
          <input
            id="start"
            name="start"
            type="number"
            required
            placeholder="e.g. 2"
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="end">End Port ID</label>
          <input
            id="end"
            name="end"
            type="number"
            required
            placeholder="e.g. 24"
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="maxFuel">Max Fuel (km)</label>
          <input
            id="maxFuel"
            name="maxFuel"
            type="number"
            required
            placeholder="e.g. 5000"
            className="form-input"
          />
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={loading}
        >
          {loading ? 'Calculating Route...' : 'Find Route'}
        </button>
      </form>
    </div>
  );
};

export default ProjectDetails;