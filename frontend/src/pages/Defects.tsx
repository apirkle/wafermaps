import React, { useState, useEffect } from 'react';

interface Defect {
  defect_id: string;
  inspection_id: string;
  x_coordinate: string;
  y_coordinate: string;
  defect_type: string;
  defect_size: string | null;
  defect_classification: string | null;
  confidence_score: string | null;
  severity_level: string | null;
  defect_category: string | null;
  defect_subcategory: string | null;
  detection_method: string | null;
  analysis_status: string | null;
  sem_image_url: string | null;
  edx_spectra_url: string | null;
  review_notes: string | null;
  created_at: string;
  updated_at: string;
}

const Defects: React.FC = () => {
  const [defects, setDefects] = useState<Defect[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDefects();
  }, []);

  const fetchDefects = async () => {
    try {
      const response = await fetch('http://localhost:18080/api/v1/defects');
      if (!response.ok) {
        throw new Error('Failed to fetch defects');
      }
      const data = await response.json();
      setDefects(data.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      case 'low': return 'green';
      default: return 'gray';
    }
  };

  if (loading) {
    return (
      <div className="page">
        <h1>Defects</h1>
        <div>Loading defects...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h1>Defects</h1>
        <div style={{ color: 'red' }}>Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Defects</h1>
      <div className="content-section">
        <div className="section-header">
          <h2>Defect Management</h2>
          <button className="btn btn-primary">Add New Defect</button>
        </div>
        
        {defects.length === 0 ? (
          <div className="empty-state">
            <p>No defects found. Defects will appear here when detected during inspections.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Inspection ID</th>
                  <th>Defect Type</th>
                  <th>Severity</th>
                  <th>Location</th>
                  <th>Size</th>
                  <th>Status</th>
                  <th>Detected</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {defects.map((defect) => (
                  <tr key={defect.defect_id}>
                    <td>{defect.inspection_id}</td>
                    <td>{defect.defect_type}</td>
                    <td>
                      <span 
                        className="severity-badge"
                        style={{ 
                          backgroundColor: getSeverityColor(defect.severity_level || 'unknown'),
                          color: 'white',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '12px'
                        }}
                      >
                        {defect.severity_level || 'unknown'}
                      </span>
                    </td>
                    <td>({defect.x_coordinate}, {defect.y_coordinate})</td>
                    <td>{defect.defect_size || '-'}</td>
                    <td>
                      <span className={`status-badge status-${(defect.analysis_status || 'unknown').toLowerCase()}`}>
                        {defect.analysis_status || 'unknown'}
                      </span>
                    </td>
                    <td>{new Date(defect.created_at).toLocaleDateString()}</td>
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

export default Defects;
