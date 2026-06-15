import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const Dashboard = () => {
    const [leaves, setLeaves] = useState([]);
    const [leaveTypes, setLeaveTypes] = useState([]);
    const [balances, setBalances] = useState([]);
    const [formData, setFormData] = useState({ start_date: '', end_date: '', leave_type_id: '', reason: '' });
    const [profile, setProfile] = useState(null);
    const [profileForm, setProfileForm] = useState({ first_name: '', last_name: '', email: '' });
    const [showProfile, setShowProfile] = useState(false);
    const [profileMsg, setProfileMsg] = useState('');

    const [editingLeave, setEditingLeave] = useState(null);
    const [editForm, setEditForm] = useState({ start_date: '', end_date: '', leave_type_id: '', reason: '' });

    useEffect(() => {
        Promise.all([
            api.get('/leaves/my'),
            api.get('/leaves/types'),
            api.get('/leaves/balance'),
            api.get('/auth/me'),
        ]).then(([leavesRes, typesRes, balanceRes, profileRes]) => {
            setLeaves(leavesRes.data);
            setLeaveTypes(typesRes.data);
            setBalances(balanceRes.data);
            setProfile(profileRes.data);
            setProfileForm({
                first_name: profileRes.data.first_name,
                last_name: profileRes.data.last_name,
                email: profileRes.data.email,
            });
            if (typesRes.data.length > 0) {
                setFormData(f => ({ ...f, leave_type_id: typesRes.data[0].id }));
            }
        });
    }, []);

    const refreshLeaves = async () => {
        const [leavesRes, balanceRes] = await Promise.all([
            api.get('/leaves/my'),
            api.get('/leaves/balance'),
        ]);
        setLeaves(leavesRes.data);
        setBalances(balanceRes.data);
    };

    const submitRequest = async (e) => {
        e.preventDefault();
        try {
            await api.post('/leaves', formData);
            await refreshLeaves();
            alert('Wniosek przesłany do akceptacji!');
        } catch (err) {
            alert(err.response?.data?.msg || 'Błąd podczas składania wniosku');
        }
    };

    const cancelLeave = async (id) => {
        if (!confirm('Czy na pewno chcesz anulować ten wniosek?')) return;
        try {
            await api.patch(`/leaves/${id}/cancel`);
            await refreshLeaves();
        } catch (err) {
            alert(err.response?.data?.msg || 'Błąd podczas anulowania');
        }
    };

    const openEdit = (leave) => {
        setEditingLeave(leave);
        setEditForm({
            start_date: leave.start,
            end_date: leave.end,
            leave_type_id: leave.leave_type_id,
            reason: leave.reason || '',
        });
    };

    const closeEdit = () => setEditingLeave(null);

    const submitEdit = async (e) => {
        e.preventDefault();
        try {
            await api.patch(`/leaves/${editingLeave.id}`, editForm);
            await refreshLeaves();
            closeEdit();
        } catch (err) {
            alert(err.response?.data?.msg || 'Błąd podczas edycji wniosku');
        }
    };

    const saveProfile = async (e) => {
        e.preventDefault();
        try {
            const res = await api.patch('/auth/me', profileForm);
            setProfile(prev => ({ ...prev, ...res.data }));
            setProfileMsg('Dane zapisane pomyślnie.');
            setTimeout(() => setProfileMsg(''), 3000);
        } catch (err) {
            setProfileMsg(err.response?.data?.msg || 'Błąd zapisu danych.');
        }
    };

    const statusBadge = (status) => {
        const map = {
            APPROVED: 'bg-green-100 text-green-700',
            PENDING: 'bg-yellow-100 text-yellow-700',
            REJECTED: 'bg-red-100 text-red-700',
            CANCELLED: 'bg-gray-100 text-gray-500',
        };
        return map[status] || 'bg-gray-100 text-gray-600';
    };

    const selectedTypeBalance = balances.find(b => b.leave_type_id === Number(formData.leave_type_id));

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-5xl mx-auto space-y-6">

                <header className="flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-800">Panel Pracownika</h1>
                        {profile && (
                            <p className="text-sm text-gray-500">{profile.first_name} {profile.last_name} · {profile.role}</p>
                        )}
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={() => setShowProfile(!showProfile)}
                            className="text-blue-600 font-medium text-sm hover:underline"
                        >
                            {showProfile ? 'Ukryj profil' : 'Mój profil'}
                        </button>
                        <button
                            onClick={() => { localStorage.clear(); window.location.href = '/login'; }}
                            className="text-red-500 font-medium text-sm hover:underline"
                        >
                            Wyloguj
                        </button>
                    </div>
                </header>

                {/* WF-02: Limity urlopowe */}
                {balances.length > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {balances.map(b => (
                            <div key={b.leave_type_id} className="bg-white rounded-xl shadow-sm p-4">
                                <p className="text-xs text-gray-500 uppercase font-semibold">{b.leave_type_name}</p>
                                <p className="text-2xl font-bold text-blue-600 mt-1">{b.remaining_days}</p>
                                <p className="text-xs text-gray-400">pozostało z {b.total_days} dni</p>
                                <div className="mt-2 bg-gray-100 rounded-full h-1.5">
                                    <div
                                        className="bg-blue-400 h-1.5 rounded-full"
                                        style={{ width: `${b.total_days > 0 ? Math.round((b.remaining_days / b.total_days) * 100) : 0}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* WF-01: Edycja profilu */}
                {showProfile && (
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <h3 className="text-lg font-semibold text-gray-700 mb-4">Moje dane kontaktowe</h3>
                        <form onSubmit={saveProfile} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="text-xs uppercase text-gray-500 font-bold">Imię</label>
                                <input
                                    type="text"
                                    value={profileForm.first_name}
                                    onChange={e => setProfileForm({ ...profileForm, first_name: e.target.value })}
                                    className="w-full border rounded p-2 mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-xs uppercase text-gray-500 font-bold">Nazwisko</label>
                                <input
                                    type="text"
                                    value={profileForm.last_name}
                                    onChange={e => setProfileForm({ ...profileForm, last_name: e.target.value })}
                                    className="w-full border rounded p-2 mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-xs uppercase text-gray-500 font-bold">Email</label>
                                <input
                                    type="email"
                                    value={profileForm.email}
                                    onChange={e => setProfileForm({ ...profileForm, email: e.target.value })}
                                    className="w-full border rounded p-2 mt-1"
                                />
                            </div>
                            <div className="md:col-span-3 flex items-center gap-4">
                                <button
                                    type="submit"
                                    className="bg-blue-600 text-white font-bold py-2 px-6 rounded hover:bg-blue-700"
                                >
                                    Zapisz zmiany
                                </button>
                                {profileMsg && (
                                    <span className="text-sm text-green-600">{profileMsg}</span>
                                )}
                            </div>
                        </form>
                    </div>
                )}

                {/* WF-03: Formularz + lista wniosków */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        <h3 className="text-lg font-semibold mb-4 text-blue-600">Nowy Wniosek</h3>
                        <form onSubmit={submitRequest} className="space-y-3">
                            <div className="flex gap-3">
                                <div className="flex-1">
                                    <label className="text-xs uppercase text-gray-500 font-bold">Od</label>
                                    <input
                                        type="date"
                                        className="w-full border rounded p-2 mt-1"
                                        onChange={e => setFormData({ ...formData, start_date: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="flex-1">
                                    <label className="text-xs uppercase text-gray-500 font-bold">Do</label>
                                    <input
                                        type="date"
                                        className="w-full border rounded p-2 mt-1"
                                        onChange={e => setFormData({ ...formData, end_date: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="text-xs uppercase text-gray-500 font-bold">Typ urlopu</label>
                                <select
                                    className="w-full border rounded p-2 mt-1"
                                    value={formData.leave_type_id}
                                    onChange={e => setFormData({ ...formData, leave_type_id: Number(e.target.value) })}
                                    required
                                >
                                    {leaveTypes.map(t => (
                                        <option key={t.id} value={t.id}>{t.name}</option>
                                    ))}
                                </select>
                                {selectedTypeBalance && (
                                    <p className="text-xs text-gray-400 mt-1">
                                        Dostępne: <span className="font-semibold text-blue-600">{selectedTypeBalance.remaining_days}</span> dni
                                    </p>
                                )}
                            </div>

                            <textarea
                                className="w-full border rounded p-2"
                                placeholder="Powód (opcjonalnie)"
                                onChange={e => setFormData({ ...formData, reason: e.target.value })}
                            />
                            <button className="w-full bg-green-500 text-white font-bold py-2 rounded hover:bg-green-600">
                                Złóż wniosek
                            </button>
                        </form>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        <h3 className="text-lg font-semibold mb-4 text-blue-600">Moje Urlopy</h3>
                        <div className="overflow-auto max-h-72">
                            {leaves.length === 0 ? (
                                <p className="text-gray-400 text-sm text-center py-8">Brak złożonych wniosków</p>
                            ) : (
                                <table className="w-full text-left text-sm">
                                    <thead className="border-b">
                                        <tr>
                                            <th className="py-2 text-gray-500">Termin</th>
                                            <th className="py-2 text-gray-500">Status</th>
                                            <th className="py-2"></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {leaves.map(l => (
                                            <tr key={l.id} className="border-b last:border-0">
                                                <td className="py-2">{l.start} – {l.end}</td>
                                                <td className="py-2">
                                                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${statusBadge(l.status)}`}>
                                                        {l.status}
                                                    </span>
                                                </td>
                                                <td className="py-2 text-right space-x-2">
                                                    {l.status === 'PENDING' && (
                                                        <button
                                                            onClick={() => openEdit(l)}
                                                            className="text-blue-500 text-xs hover:underline"
                                                        >
                                                            Edytuj
                                                        </button>
                                                    )}
                                                    {(l.status === 'PENDING' || l.status === 'APPROVED') && (
                                                        <button
                                                            onClick={() => cancelLeave(l.id)}
                                                            className="text-red-400 text-xs hover:underline"
                                                        >
                                                            Anuluj
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </div>
                </div>

            </div>

            {/* Modal edycji wniosku */}
            {editingLeave && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
                        <h3 className="text-lg font-bold text-gray-800 mb-1">Edytuj wniosek urlopowy</h3>
                        <p className="text-sm text-gray-500 mb-4">
                            Możesz zmienić daty lub typ wyłącznie wniosków ze statusem PENDING.
                        </p>
                        <form onSubmit={submitEdit} className="space-y-4">
                            <div className="flex gap-3">
                                <div className="flex-1">
                                    <label className="text-xs uppercase text-gray-500 font-bold">Od</label>
                                    <input
                                        type="date"
                                        value={editForm.start_date}
                                        onChange={e => setEditForm({ ...editForm, start_date: e.target.value })}
                                        className="w-full border rounded p-2 mt-1"
                                        required
                                    />
                                </div>
                                <div className="flex-1">
                                    <label className="text-xs uppercase text-gray-500 font-bold">Do</label>
                                    <input
                                        type="date"
                                        value={editForm.end_date}
                                        onChange={e => setEditForm({ ...editForm, end_date: e.target.value })}
                                        className="w-full border rounded p-2 mt-1"
                                        required
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="text-xs uppercase text-gray-500 font-bold">Typ urlopu</label>
                                <select
                                    value={editForm.leave_type_id}
                                    onChange={e => setEditForm({ ...editForm, leave_type_id: Number(e.target.value) })}
                                    className="w-full border rounded p-2 mt-1"
                                    required
                                >
                                    {leaveTypes.map(t => (
                                        <option key={t.id} value={t.id}>{t.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="text-xs uppercase text-gray-500 font-bold">Powód (opcjonalnie)</label>
                                <textarea
                                    className="w-full border rounded p-2 mt-1 text-sm resize-none"
                                    rows={2}
                                    value={editForm.reason}
                                    onChange={e => setEditForm({ ...editForm, reason: e.target.value })}
                                    placeholder="Opis powodu urlopu..."
                                />
                            </div>
                            <div className="flex gap-3 justify-end pt-2">
                                <button
                                    type="button"
                                    onClick={closeEdit}
                                    className="px-4 py-2 border rounded text-gray-600 hover:bg-gray-50"
                                >
                                    Anuluj
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-blue-600 text-white font-bold rounded hover:bg-blue-700"
                                >
                                    Zapisz zmiany
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
