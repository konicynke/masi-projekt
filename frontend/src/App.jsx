import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ManagerPanel from './pages/ManagerPanel';
import HRPanel from './pages/HRPanel';
import AdminPanel from './pages/AdminPanel';

function App() {
    const isAuthenticated = () => !!localStorage.getItem('token');
    const getUserRole = () => {
        const user = JSON.parse(localStorage.getItem('user'));
        return user?.role;
    };

    const defaultRedirect = () => {
        const role = getUserRole();
        if (role === 'ADMIN') return '/admin';
        if (role === 'MANAGER') return '/manager';
        if (role === 'HR') return '/hr';
        return '/dashboard';
    };

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                    path="/dashboard"
                    element={isAuthenticated() ? <Dashboard /> : <Navigate to="/login" />}
                />
                <Route
                    path="/manager"
                    element={
                        isAuthenticated() && getUserRole() === 'MANAGER'
                            ? <ManagerPanel />
                            : <Navigate to="/dashboard" />
                    }
                />
                <Route
                    path="/hr"
                    element={
                        isAuthenticated() && getUserRole() === 'HR'
                            ? <HRPanel />
                            : <Navigate to="/dashboard" />
                    }
                />
                <Route
                    path="/admin"
                    element={
                        isAuthenticated() && getUserRole() === 'ADMIN'
                            ? <AdminPanel />
                            : <Navigate to="/login" />
                    }
                />
                <Route
                    path="/"
                    element={<Navigate to={isAuthenticated() ? defaultRedirect() : '/login'} />}
                />
            </Routes>
        </Router>
    );
}

export default App;
