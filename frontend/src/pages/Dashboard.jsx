import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const Dashboard = () => {
    const [leaves, setLeaves] = useState([]);
    const [formData, setFormData] = useState({ start_date: '', end_date: '', leave_type_id: 1, reason: '' });

    useEffect(() => {
        api.get('/leaves/my').then(res => setLeaves(res.data));
    }, []);

    const submitRequest = async (e) => {
        e.preventDefault();
        try {
            await api.post('/leaves', formData);
            const res = await api.get('/leaves/my');
            setLeaves(res.data);
            alert("Wniosek przesłany do akceptacji!");
        } catch (err) {
            alert(err.response?.data?.msg);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-4xl mx-auto">
                <header className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800">Panel Pracownika</h1>
                    <button onClick={() => {localStorage.clear(); window.location.href='/login'}} className="text-red-500 font-semibold">Wyloguj</button>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        <h3 className="text-lg font-semibold mb-4 text-blue-600">Nowy Wniosek</h3>
                        <form onSubmit={submitRequest} className="space-y-4">
                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <label className="text-xs uppercase text-gray-500 font-bold">Od</label>
                                    <input type="date" className="w-full border rounded p-2" onChange={e => setFormData({...formData, start_date: e.target.value})} required />
                                </div>
                                <div className="flex-1">
                                    <label className="text-xs uppercase text-gray-500 font-bold">Do</label>
                                    <input type="date" className="w-full border rounded p-2" onChange={e => setFormData({...formData, end_date: e.target.value})} required />
                                </div>
                            </div>
                            <textarea className="w-full border rounded p-2" placeholder="Powód (opcjonalnie)" onChange={e => setFormData({...formData, reason: e.target.value})} />
                            <button className="w-full bg-green-500 text-white font-bold py-2 rounded hover:bg-green-600">Złóż wniosek</button>
                        </form>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        <h3 className="text-lg font-semibold mb-4 text-blue-600">Moje Urlopy</h3>
                        <div className="overflow-auto max-h-64">
                            <table className="w-full text-left">
                                <thead className="border-b">
                                    <tr>
                                        <th className="py-2 text-gray-600">Termin</th>
                                        <th className="py-2 text-gray-600">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                {leaves.map(l => (
    <tr key={l.id} className="border-b last:border-0">
        <td className="py-3 text-sm">{l.start} do {l.end}</td>
        <td className="py-3">
            <span className={`px-2 py-1 rounded text-xs font-bold ${l.status === 'APPROVED' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                {l.status}
            </span>
        </td>
        <td className="py-3 text-right">
            {(l.status === 'PENDING' || l.status === 'APPROVED') && (
                <button 
                    onClick={async () => {
                        if(confirm("Czy na pewno chcesz anulować?")) {
                            await api.patch(`/leaves/${l.id}/cancel`);
                            window.location.reload();
                        }
                    }}
                    className="text-red-500 text-xs hover:underline"
                >
                    Anuluj
                </button>
            )}
        </td>
    </tr>
))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;