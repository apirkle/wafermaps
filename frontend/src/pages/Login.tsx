import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import { loginStart, loginSuccess, loginFailure } from '../store/slices/authSlice';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state: RootState) => state.auth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    dispatch(loginStart());
    
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        dispatch(loginSuccess({
          user: {
            user_id: '1',
            username: username,
            email: `${username}@wafermaps.com`,
            role: 'admin'
          },
          token: data.access_token
        }));
        navigate('/dashboard');
      } else {
        const errorData = await response.json();
        dispatch(loginFailure(errorData.detail || 'Login failed'));
      }
    } catch (err) {
      dispatch(loginFailure('Network error. Please try again.'));
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Login to WaferMaps</h2>
        
        {error && (
          <div style={{ color: 'red', marginBottom: '20px' }}>
            {error}
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
        
        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <p>Demo credentials:</p>
          <p>Username: admin</p>
          <p>Password: password123</p>
        </div>
      </form>
    </div>
  );
};

export default Login;
