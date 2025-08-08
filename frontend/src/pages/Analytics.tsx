import React, { useState, useEffect } from 'react';

interface AnalyticsData {
  total_wafers: number;
  total_inspections: number;
  total_defects: number;
  defect_rate: number;
  inspection_completion_rate: number;
  defects_by_type: { [key: string]: number };
  defects_by_severity: { [key: string]: number };
}

const Analytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:18080/api/v1/analytics');
      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <h1>Analytics</h1>
        <div>Loading analytics data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h1>Analytics</h1>
        <div style={{ color: 'red' }}>Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Analytics Dashboard</h1>
      
      <div className="analytics-grid">
        {/* Key Metrics */}
        <div className="metrics-section">
          <h2>Key Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Total Wafers</h3>
              <div className="metric-value">{analyticsData?.total_wafers || 0}</div>
            </div>
            <div className="metric-card">
              <h3>Total Inspections</h3>
              <div className="metric-value">{analyticsData?.total_inspections || 0}</div>
            </div>
            <div className="metric-card">
              <h3>Total Defects</h3>
              <div className="metric-value">{analyticsData?.total_defects || 0}</div>
            </div>
            <div className="metric-card">
              <h3>Defect Rate</h3>
              <div className="metric-value">{(analyticsData?.defect_rate || 0).toFixed(2)}%</div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="charts-section">
          <h2>Defect Analysis</h2>
          <div className="charts-grid">
            <div className="chart-card">
              <h3>Defects by Type</h3>
              <div className="chart-placeholder">
                <p>Chart visualization will be implemented here</p>
                <div className="chart-data">
                  {analyticsData?.defects_by_type && Object.entries(analyticsData.defects_by_type).map(([type, count]) => (
                    <div key={type} className="chart-item">
                      <span>{type}:</span>
                      <span>{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="chart-card">
              <h3>Defects by Severity</h3>
              <div className="chart-placeholder">
                <p>Chart visualization will be implemented here</p>
                <div className="chart-data">
                  {analyticsData?.defects_by_severity && Object.entries(analyticsData.defects_by_severity).map(([severity, count]) => (
                    <div key={severity} className="chart-item">
                      <span>{severity}:</span>
                      <span>{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Trends Section */}
        <div className="trends-section">
          <h2>Trends & Insights</h2>
          <div className="insights-grid">
            <div className="insight-card">
              <h3>Inspection Completion Rate</h3>
              <div className="insight-value">{(analyticsData?.inspection_completion_rate || 0).toFixed(1)}%</div>
              <p>Percentage of scheduled inspections that have been completed</p>
            </div>
            
            <div className="insight-card">
              <h3>Quality Score</h3>
              <div className="insight-value">
                {analyticsData?.defect_rate ? (100 - analyticsData.defect_rate).toFixed(1) : 100}%
              </div>
              <p>Overall quality score based on defect rate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
