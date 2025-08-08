import React, { useState, useEffect } from 'react';

interface Inspection {
  inspection_id: string;
  wafer_id: string;
  equipment_id: string;
  run_id: string;
  timestamp: string;
  defect_count: number;
  inspection_type: string;
  inspection_mode: string;
  operator_id: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const Inspections: React.FC = () => {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInspections();
  }, []);

  const fetchInspections = async () => {
    try {
      const response = await fetch('http://localhost:18080/api/v1/inspections');
      if (!response.ok) {
        throw new Error('Failed to fetch inspections');
      }
      const data = await response.json();
      setInspections(data.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <h1>Inspections</h1>
        <div>Loading inspections...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h1>Inspections</h1>
        <div style={{ color: 'red' }}>Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Inspections</h1>
      <div className="content-section">
        <div className="section-header">
          <h2>Inspection Management</h2>
          <button className="btn btn-primary">Schedule New Inspection</button>
        </div>
        
        {inspections.length === 0 ? (
          <div className="empty-state">
            <p>No inspections found. Schedule your first inspection to get started.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Wafer ID</th>
                  <th>Run ID</th>
                  <th>Inspection Type</th>
                  <th>Defect Count</th>
                  <th>Operator</th>
                  <th>Timestamp</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {inspections.map((inspection) => (
                  <tr key={inspection.inspection_id}>
                    <td>{inspection.wafer_id}</td>
                    <td>{inspection.run_id}</td>
                    <td>{inspection.inspection_type}</td>
                    <td>{inspection.defect_count}</td>
                    <td>{inspection.operator_id || '-'}</td>
                    <td>{new Date(inspection.timestamp).toLocaleDateString()}</td>
                    <td>
                      <button className="btn btn-sm btn-secondary">View</button>
                      <button className="btn btn-sm btn-primary">Edit</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Inspections;
