import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { logout } from '../store/slices/authSlice';

const Header: React.FC = () => {
  const dispatch = useDispatch();
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <header className="header">
      <div>
        <h1>WaferMaps</h1>
        <p>Semiconductor Fab Defect Data Exploration Platform</p>
      </div>
      <div>
        {isAuthenticated && user ? (
          <div>
            <span>Welcome, {user.username}</span>
            <button onClick={handleLogout} className="btn" style={{ marginLeft: '10px' }}>
              Logout
            </button>
          </div>
        ) : (
          <span>Please log in</span>
        )}
      </div>
    </header>
  );
};

export default Header;
