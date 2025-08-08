import React, { useState, useEffect } from 'react';

interface EquipmentItem {
  equipment_id: string;
  equipment_name: string;
  equipment_type: string;
  manufacturer: string | null;
  model: string | null;
  serial_number: string | null;
  location: string | null;
  status: string | null;
  operator: string | null;
  last_maintenance: string | null;
  next_maintenance: string | null;
  created_at: string;
  updated_at: string;
}

const Equipment: React.FC = () => {
  const [equipment, setEquipment] = useState<EquipmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEquipment();
  }, []);

  const fetchEquipment = async () => {
    try {
      const response = await fetch('http://localhost:18080/api/v1/equipment');
      if (!response.ok) {
        throw new Error('Failed to fetch equipment');
      }
      const data = await response.json();
      setEquipment(data.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'operational': return 'green';
      case 'maintenance': return 'orange';
      case 'offline': return 'red';
      case 'standby': return 'blue';
      default: return 'gray';
    }
  };

  const isMaintenanceDue = (nextMaintenance: string) => {
    const nextDate = new Date(nextMaintenance);
    const today = new Date();
    const daysUntil = Math.ceil((nextDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntil <= 7;
  };

  if (loading) {
    return (
      <div className="page">
        <h1>Equipment</h1>
        <div>Loading equipment data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h1>Equipment</h1>
        <div style={{ color: 'red' }}>Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Equipment Management</h1>
      
      <div className="content-section">
        <div className="section-header">
          <h2>Equipment Status</h2>
          <button className="btn btn-primary">Add New Equipment</button>
        </div>
        
        {equipment.length === 0 ? (
          <div className="empty-state">
            <p>No equipment found. Add your first piece of equipment to get started.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Equipment ID</th>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Location</th>
                  <th>Operator</th>
                  <th>Last Maintenance</th>
                  <th>Next Maintenance</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {equipment.map((item) => (
                  <tr key={item.equipment_id}>
                    <td>{item.equipment_id}</td>
                    <td>{item.equipment_name}</td>
                    <td>{item.equipment_type}</td>
                    <td>
                      <span 
                        className="status-badge"
                        style={{ 
                          backgroundColor: getStatusColor(item.status || 'unknown'),
                          color: 'white',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '12px'
                        }}
                      >
                        {item.status || 'unknown'}
                      </span>
                    </td>
                    <td>{item.location || '-'}</td>
                    <td>{item.operator || '-'}</td>
                    <td>{item.last_maintenance ? new Date(item.last_maintenance).toLocaleDateString() : '-'}</td>
                    <td>
                      {item.next_maintenance ? (
                        <span 
                          style={{ 
                            color: isMaintenanceDue(item.next_maintenance) ? 'red' : 'inherit',
                            fontWeight: isMaintenanceDue(item.next_maintenance) ? 'bold' : 'normal'
                          }}
                        >
                          {new Date(item.next_maintenance).toLocaleDateString()}
                        </span>
                      ) : '-'}
                    </td>
                    <td>
                      <button className="btn btn-sm btn-secondary">View</button>
                      <button className="btn btn-sm btn-primary">Edit</button>
                      <button className="btn btn-sm btn-warning">Maintenance</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Equipment Summary */}
      <div className="summary-section">
        <h2>Equipment Summary</h2>
        <div className="summary-grid">
          <div className="summary-card">
            <h3>Total Equipment</h3>
            <div className="summary-value">{equipment.length}</div>
          </div>
          <div className="summary-card">
            <h3>Operational</h3>
            <div className="summary-value">
              {equipment.filter(e => e.status?.toLowerCase() === 'operational').length}
            </div>
          </div>
          <div className="summary-card">
            <h3>Under Maintenance</h3>
            <div className="summary-value">
              {equipment.filter(e => e.status?.toLowerCase() === 'maintenance').length}
            </div>
          </div>
          <div className="summary-card">
            <h3>Maintenance Due</h3>
            <div className="summary-value">
              {equipment.filter(e => e.next_maintenance && isMaintenanceDue(e.next_maintenance)).length}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Equipment;
