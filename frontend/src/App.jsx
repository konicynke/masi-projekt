import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ManagerPanel from './pages/ManagerPanel';

function App() {
  const isAuthenticated = () => !!localStorage.getItem('token');
  const getUserRole = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    return user?.role;
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/dashboard" 
          element={isAuthenticated() ? <Dashboard /> : <Navigate to="/login" />} 
        />
        <Route path="/" element={<Navigate to="/login" />} />
        <Route 
          path="/manager" 
          element={
            isAuthenticated() && getUserRole() === 'MANAGER' 
            ? <ManagerPanel /> 
            : <Navigate to="/dashboard" />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;