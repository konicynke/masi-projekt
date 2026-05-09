import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const ManagerPanel = () => {
    const [teamLeaves, setTeamLeaves] = useState([]);

    useEffect(() => {
        fetchTeamLeaves();
    }, []);

    const fetchTeamLeaves = async () => {
        const res = await api.get('/manager/team-leaves');
        setTeamLeaves(res.data);
    };

    const handleAction = async (id, status) => {
        const comment = prompt("Dodaj komentarz (opcjonalnie):");
        try {
            await api.patch(`/manager/leaves/${id}/status`, { status, manager_comment: comment });
            fetchTeamLeaves();
            alert(`Wniosek został ${status === 'APPROVED' ? 'zaakceptowany' : 'odrzucony'}`);
        } catch (err) {
            alert(err.response?.data?.msg);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-6xl mx-auto">
                <div className="flex justify-between mb-8">
                    <h1 className="text-3xl font-bold text-gray-800">Panel Menedżera</h1>
                    <button onClick={() => window.location.href='/dashboard'} className="bg-gray-200 px-4 py-2 rounded">Mój Panel</button>
                </div>

                <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-gray-100">
                            <tr>
                                <th className="p-4">Pracownik</th>
                                <th className="p-4">Termin</th>
                                <th className="p-4">Typ</th>
                                <th className="p-4">Status</th>
                                <th className="p-4 text-right">Akcje</th>
                            </tr>
                        </thead>
                        <tbody>
                            {teamLeaves.map(l => (
                                <tr key={l.id} className="border-b">
                                    <td className="p-4 font-medium">{l.user_id}</td>
                                    <td className="p-4">{l.start} - {l.end}</td>
                                    <td className="p-4">{l.leave_type_id}</td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs ${l.status === 'PENDING' ? 'bg-yellow-100' : 'bg-blue-100'}`}>
                                            {l.status}
                                        </span>
                                    </td>
                                    <td className="p-4 text-right space-x-2">
                                        {l.status === 'PENDING' && (
                                            <>
                                                <button onClick={() => handleAction(l.id, 'APPROVED')} className="bg-green-500 text-white px-3 py-1 rounded text-sm">Akceptuj</button>
                                                <button onClick={() => handleAction(l.id, 'REJECTED')} className="bg-red-500 text-white px-3 py-1 rounded text-sm">Odrzuć</button>
                                            </>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default ManagerPanel;