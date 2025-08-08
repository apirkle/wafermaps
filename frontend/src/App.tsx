import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import './App.css';

// Components
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Wafers from './pages/Wafers';
import Inspections from './pages/Inspections';
import Defects from './pages/Defects';
import Analytics from './pages/Analytics';
import Equipment from './pages/Equipment';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          <Header />
          <div className="main-content">
            <Sidebar />
            <div className="content">
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/wafers" element={<Wafers />} />
                <Route path="/inspections" element={<Inspections />} />
                <Route path="/defects" element={<Defects />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/equipment" element={<Equipment />} />
              </Routes>
            </div>
          </div>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
