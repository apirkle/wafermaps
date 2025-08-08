import React from 'react';
import { Link } from 'react-router-dom';

const Sidebar: React.FC = () => {
  return (
    <nav className="sidebar">
      <h3>Navigation</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        <li style={{ marginBottom: '10px' }}>
          <Link to="/dashboard" style={{ textDecoration: 'none', color: '#333' }}>
            Dashboard
          </Link>
        </li>
        <li style={{ marginBottom: '10px' }}>
          <Link to="/wafers" style={{ textDecoration: 'none', color: '#333' }}>
            Wafers
          </Link>
        </li>
        <li style={{ marginBottom: '10px' }}>
          <Link to="/inspections" style={{ textDecoration: 'none', color: '#333' }}>
            Inspections
          </Link>
        </li>
        <li style={{ marginBottom: '10px' }}>
          <Link to="/defects" style={{ textDecoration: 'none', color: '#333' }}>
            Defects
          </Link>
        </li>
        <li style={{ marginBottom: '10px' }}>
          <Link to="/analytics" style={{ textDecoration: 'none', color: '#333' }}>
            Analytics
          </Link>
        </li>
        <li style={{ marginBottom: '10px' }}>
          <Link to="/equipment" style={{ textDecoration: 'none', color: '#333' }}>
            Equipment
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default Sidebar;
