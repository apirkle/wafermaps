import React, { useState, useEffect, useCallback } from 'react';

interface Defect {
  defect_id: string;
  x_coordinate: string;
  y_coordinate: string;
  defect_type: string;
  severity_level: string | null;
  defect_size: string | null;
  analysis_status: string | null;
}

interface WaferMapProps {
  waferId: string;
  diameter: string;
  onClose: () => void;
}

const WaferMap: React.FC<WaferMapProps> = ({ waferId, diameter, onClose }) => {
  const [defects, setDefects] = useState<Defect[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);

  const fetchWaferDefects = useCallback(async () => {
    try {
      // First get inspections for this wafer
      const inspectionsResponse = await fetch(`http://localhost:18080/api/v1/inspections/?wafer_id=${waferId}`);
      if (!inspectionsResponse.ok) {
        throw new Error('Failed to fetch inspections');
      }
      const inspectionsData = await inspectionsResponse.json();
      const inspections = inspectionsData.items || [];

      // Then get defects for all inspections of this wafer
      const allDefects: Defect[] = [];
      for (const inspection of inspections) {
        const defectsResponse = await fetch(`http://localhost:18080/api/v1/defects/?inspection_id=${inspection.inspection_id}`);
        if (defectsResponse.ok) {
          const defectsData = await defectsResponse.json();
          allDefects.push(...(defectsData.items || []));
        }
      }
      
      setDefects(allDefects);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [waferId]);

  useEffect(() => {
    fetchWaferDefects();
  }, [fetchWaferDefects]);

  const getDiameterInPixels = () => {
    const diameterValue = parseInt(diameter.replace('mm', ''));
    // Scale the diameter to fit nicely in the container
    return Math.min(400, Math.max(200, diameterValue * 2));
  };

  const getSeverityColor = (severity: string | null) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getDefectSize = (size: string | null) => {
    if (!size) return 4;
    const sizeValue = parseFloat(size);
    return Math.max(2, Math.min(8, sizeValue / 2));
  };

  const renderDefect = (defect: Defect) => {
    const x = parseFloat(defect.x_coordinate);
    const y = parseFloat(defect.y_coordinate);
    const diameterPx = getDiameterInPixels();
    const radius = diameterPx / 2;
    
    // Convert wafer coordinates to SVG coordinates
    // Wafer coordinates are typically in mm from center
    const diameterValue = parseInt(diameter.replace('mm', ''));
    const scaleFactor = diameterValue / 2; // Scale based on actual wafer diameter
    const svgX = radius + (x / scaleFactor) * radius;
    const svgY = radius - (y / scaleFactor) * radius;
    
    const defectSize = getDefectSize(defect.defect_size);
    const color = getSeverityColor(defect.severity_level);

    return (
      <circle
        key={defect.defect_id}
        cx={svgX}
        cy={svgY}
        r={defectSize}
        fill={color}
        stroke="#fff"
        strokeWidth="1"
        opacity="0.8"
        onMouseEnter={() => setSelectedDefect(defect)}
        onMouseLeave={() => setSelectedDefect(null)}
        style={{ cursor: 'pointer' }}
      />
    );
  };

  if (loading) {
    return (
      <div className="wafer-map-modal">
        <div className="wafer-map-content">
          <div className="wafer-map-header">
            <h2>Wafer Map - {waferId}</h2>
            <button className="btn btn-secondary" onClick={onClose}>×</button>
          </div>
          <div className="wafer-map-body">
            <div>Loading wafer map...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="wafer-map-modal">
        <div className="wafer-map-content">
          <div className="wafer-map-header">
            <h2>Wafer Map - {waferId}</h2>
            <button className="btn btn-secondary" onClick={onClose}>×</button>
          </div>
          <div className="wafer-map-body">
            <div style={{ color: 'red' }}>Error: {error}</div>
          </div>
        </div>
      </div>
    );
  }

  const diameterPx = getDiameterInPixels();
  const radius = diameterPx / 2;

  return (
    <div className="wafer-map-modal">
      <div className="wafer-map-content">
        <div className="wafer-map-header">
          <h2>Wafer Map - {waferId}</h2>
          <button className="btn btn-secondary" onClick={onClose}>×</button>
        </div>
        <div className="wafer-map-body">
          <div className="wafer-map-container">
            <svg width={diameterPx} height={diameterPx} className="wafer-svg">
              {/* Wafer outline */}
              <circle
                cx={radius}
                cy={radius}
                r={radius}
                fill="none"
                stroke="#333"
                strokeWidth="2"
              />
              
              {/* Center crosshair */}
              <line
                x1={radius - 10}
                y1={radius}
                x2={radius + 10}
                y2={radius}
                stroke="#ccc"
                strokeWidth="1"
              />
              <line
                x1={radius}
                y1={radius - 10}
                x2={radius}
                y2={radius + 10}
                stroke="#ccc"
                strokeWidth="1"
              />
              
              {/* Wafer zones (optional grid lines) */}
              <circle
                cx={radius}
                cy={radius}
                r={radius * 0.33}
                fill="none"
                stroke="#e9ecef"
                strokeWidth="1"
                strokeDasharray="5,5"
              />
              <circle
                cx={radius}
                cy={radius}
                r={radius * 0.67}
                fill="none"
                stroke="#e9ecef"
                strokeWidth="1"
                strokeDasharray="5,5"
              />
              
                             {/* Defects */}
               {defects.length > 0 ? (
                 defects.map(renderDefect)
               ) : (
                 <text
                   x={radius}
                   y={radius}
                   textAnchor="middle"
                   dominantBaseline="middle"
                   fill="#6c757d"
                   fontSize="14"
                 >
                   No defects found
                 </text>
               )}
            </svg>
            
            {/* Defect information panel */}
            <div className="defect-info-panel">
              <h3>Defect Information</h3>
              {selectedDefect ? (
                <div className="defect-details">
                  <p><strong>Type:</strong> {selectedDefect.defect_type}</p>
                  <p><strong>Severity:</strong> {selectedDefect.severity_level || 'Unknown'}</p>
                  <p><strong>Size:</strong> {selectedDefect.defect_size || 'Unknown'} μm</p>
                  <p><strong>Status:</strong> {selectedDefect.analysis_status || 'Unknown'}</p>
                  <p><strong>Location:</strong> ({selectedDefect.x_coordinate}, {selectedDefect.y_coordinate})</p>
                </div>
                             ) : (
                 <div className="defect-summary">
                   <p><strong>Total Defects:</strong> {defects.length}</p>
                   <p><strong>Diameter:</strong> {diameter}</p>
                   <p><strong>Critical:</strong> {defects.filter(d => d.severity_level?.toLowerCase() === 'critical').length}</p>
                   <p><strong>High:</strong> {defects.filter(d => d.severity_level?.toLowerCase() === 'high').length}</p>
                   <p><strong>Medium:</strong> {defects.filter(d => d.severity_level?.toLowerCase() === 'medium').length}</p>
                   <p><strong>Low:</strong> {defects.filter(d => d.severity_level?.toLowerCase() === 'low').length}</p>
                   <div className="severity-legend">
                    <h4>Severity Legend:</h4>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#dc3545' }}></span>
                      <span>Critical</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#fd7e14' }}></span>
                      <span>High</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#ffc107' }}></span>
                      <span>Medium</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#28a745' }}></span>
                      <span>Low</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WaferMap;
