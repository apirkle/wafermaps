import React, { useState, useEffect } from 'react';
import WaferMap from '../components/WaferMap';

interface Wafer {
  wafer_id: string;
  diameter: string;
  thickness: string;
  material: string;
  orientation: string;
  resistivity: string;
  dopant_type: string | null;
  dopant_concentration: string | null;
  creation_date: string;
  updated_at: string;
}

const Wafers: React.FC = () => {
  const [wafers, setWafers] = useState<Wafer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWafer, setSelectedWafer] = useState<Wafer | null>(null);
  const [showWaferMap, setShowWaferMap] = useState(false);

  useEffect(() => {
    fetchWafers();
  }, []);

  const fetchWafers = async () => {
    try {
      const response = await fetch('http://localhost:18080/api/v1/wafers');
      if (!response.ok) {
        throw new Error('Failed to fetch wafers');
      }
      const data = await response.json();
      setWafers(data.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <h1>Wafers</h1>
        <div>Loading wafers...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h1>Wafers</h1>
        <div style={{ color: 'red' }}>Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Wafers</h1>
      <div className="content-section">
        <div className="section-header">
          <h2>Wafer Management</h2>
          <button className="btn btn-primary">Add New Wafer</button>
        </div>
        
        {wafers.length === 0 ? (
          <div className="empty-state">
            <p>No wafers found. Create your first wafer to get started.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Wafer ID</th>
                  <th>Diameter</th>
                  <th>Material</th>
                  <th>Orientation</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {wafers.map((wafer) => (
                  <tr key={wafer.wafer_id}>
                    <td>{wafer.wafer_id}</td>
                    <td>{wafer.diameter}</td>
                    <td>{wafer.material}</td>
                    <td>{wafer.orientation}</td>
                    <td>{new Date(wafer.creation_date).toLocaleDateString()}</td>
                    <td>
                      <button 
                        className="btn btn-sm btn-secondary"
                        onClick={() => {
                          setSelectedWafer(wafer);
                          setShowWaferMap(true);
                        }}
                      >
                        View
                      </button>
                      <button className="btn btn-sm btn-primary">Edit</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* Wafer Map Modal */}
      {showWaferMap && selectedWafer && (
        <WaferMap
          waferId={selectedWafer.wafer_id}
          diameter={selectedWafer.diameter}
          onClose={() => {
            setShowWaferMap(false);
            setSelectedWafer(null);
          }}
        />
      )}
    </div>
  );
};

export default Wafers;
