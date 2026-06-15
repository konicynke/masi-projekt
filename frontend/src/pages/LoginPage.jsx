import React, { useState } from 'react';
import api from '../api/axios';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/auth/login', { email, password });
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify(response.data.user));
            const role = response.data.user.role;
            if (role === 'ADMIN') {
                window.location.href = '/admin';
            } else if (role === 'MANAGER') {
                window.location.href = '/manager';
            } else if (role === 'HR') {
                window.location.href = '/hr';
            } else {
                window.location.href = '/dashboard';
            }
        } catch (error) {
            alert("Błąd: " + (error.response?.data?.msg || "Serwer nie odpowiada"));
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md w-96">
                <h2 className="text-2xl font-bold mb-6 text-center text-blue-600">System Urlopowy</h2>
                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Email</label>
                        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} 
                               className="mt-1 block w-full border rounded-md p-2" required />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Hasło</label>
                        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} 
                               className="mt-1 block w-full border rounded-md p-2" required />
                    </div>
                    <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 transition">
                        Zaloguj się
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;