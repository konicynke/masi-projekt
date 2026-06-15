import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const STATUS_BADGE = {
    APPROVED: 'bg-green-100 text-green-700',
    PENDING:  'bg-yellow-100 text-yellow-700',
    REJECTED: 'bg-red-100 text-red-700',
    CANCELLED:'bg-gray-100 text-gray-500',
};

const HRPanel = () => {
    const [activeTab, setActiveTab] = useState('urlopy');

    // --- Urlopy ---
    const [leaves, setLeaves] = useState([]);
    const [leavesLoading, setLeavesLoading] = useState(true);
    const [filter, setFilter] = useState('');

    // --- Limity ---
    const [balances, setBalances] = useState([]);
    const [users, setUsers] = useState([]);
    const [leaveTypes, setLeaveTypes] = useState([]);
    const [balancesLoading, setBalancesLoading] = useState(false);
    const [balanceForm, setBalanceForm] = useState({
        user_id: '',
        leave_type_id: '',
        year: new Date().getFullYear(),
        total_days: '',
    });
    const [editingBalance, setEditingBalance] = useState(null);
    const [editTotalDays, setEditTotalDays] = useState('');
    const [balanceMsg, setBalanceMsg] = useState('');

    useEffect(() => {
        api.get('/hr/leaves')
            .then(res => setLeaves(res.data))
            .finally(() => setLeavesLoading(false));

        Promise.all([api.get('/hr/users'), api.get('/hr/leave-types')])
            .then(([usersRes, typesRes]) => {
                setUsers(usersRes.data);
                setLeaveTypes(typesRes.data);
                if (usersRes.data.length > 0) setBalanceForm(f => ({ ...f, user_id: usersRes.data[0].id }));
                if (typesRes.data.length > 0) setBalanceForm(f => ({ ...f, leave_type_id: typesRes.data[0].id }));
            });
    }, []);

    useEffect(() => {
        if (activeTab === 'limity') fetchBalances();
    }, [activeTab]);

    const fetchBalances = async () => {
        setBalancesLoading(true);
        try {
            const res = await api.get('/hr/balances');
            setBalances(res.data);
        } finally {
            setBalancesLoading(false);
        }
    };

    const showMsg = (msg) => {
        setBalanceMsg(msg);
        setTimeout(() => setBalanceMsg(''), 3000);
    };

    const submitBalance = async (e) => {
        e.preventDefault();
        try {
            await api.post('/hr/balances', {
                user_id: Number(balanceForm.user_id),
                leave_type_id: Number(balanceForm.leave_type_id),
                year: Number(balanceForm.year),
                total_days: Number(balanceForm.total_days),
            });
            await fetchBalances();
            setBalanceForm(f => ({ ...f, total_days: '' }));
            showMsg('Limit dodany pomyślnie.');
        } catch (err) {
            showMsg(err.response?.data?.msg || 'Błąd podczas dodawania limitu.');
        }
    };

    const openEditBalance = (b) => {
        setEditingBalance(b);
        setEditTotalDays(String(b.total_days));
    };

    const submitEditBalance = async (e) => {
        e.preventDefault();
        try {
            await api.patch(`/hr/balances/${editingBalance.id}`, {
                total_days: Number(editTotalDays),
            });
            await fetchBalances();
            setEditingBalance(null);
            showMsg('Limit zaktualizowany.');
        } catch (err) {
            showMsg(err.response?.data?.msg || 'Błąd podczas aktualizacji limitu.');
        }
    };

    const downloadReport = async (format) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/hr/reports/${format}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error('Błąd pobierania raportu');
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `raport_urlopowy.${format === 'xls' ? 'xlsx' : format}`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            alert(err.message);
        }
    };

    const filtered = leaves.filter(l =>
        !filter || l.user_name.toLowerCase().includes(filter.toLowerCase()) || l.status === filter
    );

    const stats = {
        total: leaves.length,
        approved: leaves.filter(l => l.status === 'APPROVED').length,
        pending: leaves.filter(l => l.status === 'PENDING').length,
        rejected: leaves.filter(l => l.status === 'REJECTED').length,
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-6xl mx-auto space-y-6">

                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-800">Panel HR</h1>
                    <button
                        onClick={() => { localStorage.clear(); window.location.href = '/login'; }}
                        className="text-red-500 font-medium text-sm hover:underline"
                    >
                        Wyloguj
                    </button>
                </div>

                {/* Statystyki */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {[
                        { label: 'Wszystkich wniosków', value: stats.total,    color: 'text-gray-700' },
                        { label: 'Zaakceptowanych',     value: stats.approved, color: 'text-green-600' },
                        { label: 'Oczekujących',        value: stats.pending,  color: 'text-yellow-600' },
                        { label: 'Odrzuconych',         value: stats.rejected, color: 'text-red-500' },
                    ].map(s => (
                        <div key={s.label} className="bg-white rounded-xl shadow-sm p-4">
                            <p className="text-xs text-gray-400 uppercase">{s.label}</p>
                            <p className={`text-3xl font-bold mt-1 ${s.color}`}>{s.value}</p>
                        </div>
                    ))}
                </div>

                {/* Zakładki */}
                <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
                    {[
                        { key: 'urlopy', label: 'Wnioski urlopowe' },
                        { key: 'limity', label: 'Zarządzanie limitami' },
                    ].map(tab => (
                        <button
                            key={tab.key}
                            onClick={() => setActiveTab(tab.key)}
                            className={`px-5 py-2 rounded-md text-sm font-medium transition ${
                                activeTab === tab.key
                                    ? 'bg-white shadow text-blue-600'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* === ZAKŁADKA: URLOPY === */}
                {activeTab === 'urlopy' && (
                    <>
                        {/* WF-07: Raporty */}
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-lg font-semibold text-gray-700 mb-4">Generowanie raportów</h2>
                            <div className="flex flex-wrap gap-3">
                                <button
                                    onClick={() => downloadReport('csv')}
                                    className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium px-5 py-2.5 rounded-lg transition"
                                >
                                    Pobierz CSV
                                </button>
                                <button
                                    onClick={() => downloadReport('xls')}
                                    className="flex items-center gap-2 bg-green-50 hover:bg-green-100 text-green-700 font-medium px-5 py-2.5 rounded-lg transition"
                                >
                                    Pobierz XLS
                                </button>
                                <button
                                    onClick={() => downloadReport('pdf')}
                                    className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-700 font-medium px-5 py-2.5 rounded-lg transition"
                                >
                                    Pobierz PDF
                                </button>
                            </div>
                        </div>

                        {/* Tabela wniosków */}
                        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                            <div className="p-4 border-b flex items-center gap-3">
                                <h2 className="text-lg font-semibold text-gray-700">Wszystkie wnioski urlopowe</h2>
                                <input
                                    type="text"
                                    placeholder="Szukaj pracownika..."
                                    value={filter}
                                    onChange={e => setFilter(e.target.value)}
                                    className="ml-auto border rounded px-3 py-1.5 text-sm w-56"
                                />
                            </div>
                            {leavesLoading ? (
                                <div className="p-8 text-center text-gray-400">Ładowanie...</div>
                            ) : (
                                <table className="w-full text-left text-sm">
                                    <thead className="bg-gray-50 border-b">
                                        <tr>
                                            <th className="p-3 text-gray-500">ID</th>
                                            <th className="p-3 text-gray-500">Pracownik</th>
                                            <th className="p-3 text-gray-500">Typ urlopu</th>
                                            <th className="p-3 text-gray-500">Od</th>
                                            <th className="p-3 text-gray-500">Do</th>
                                            <th className="p-3 text-gray-500">Status</th>
                                            <th className="p-3 text-gray-500">Powód</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filtered.length === 0 && (
                                            <tr><td colSpan={7} className="p-8 text-center text-gray-400">Brak wyników</td></tr>
                                        )}
                                        {filtered.map(l => (
                                            <tr key={l.id} className="border-b last:border-0 hover:bg-gray-50">
                                                <td className="p-3 text-gray-400">#{l.id}</td>
                                                <td className="p-3 font-medium">{l.user_name}</td>
                                                <td className="p-3 text-gray-600">{l.leave_type}</td>
                                                <td className="p-3">{l.start_date}</td>
                                                <td className="p-3">{l.end_date}</td>
                                                <td className="p-3">
                                                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${STATUS_BADGE[l.status] || 'bg-gray-100'}`}>
                                                        {l.status}
                                                    </span>
                                                </td>
                                                <td className="p-3 text-gray-400 text-xs">{l.reason || '—'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </>
                )}

                {/* === ZAKŁADKA: LIMITY === */}
                {activeTab === 'limity' && (
                    <>
                        {/* Formularz dodawania limitu */}
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-lg font-semibold text-gray-700 mb-4">Dodaj limit urlopowy</h2>
                            <form onSubmit={submitBalance} className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
                                <div>
                                    <label className="text-xs uppercase text-gray-500 font-bold">Pracownik</label>
                                    <select
                                        value={balanceForm.user_id}
                                        onChange={e => setBalanceForm({ ...balanceForm, user_id: e.target.value })}
                                        className="w-full border rounded p-2 mt-1 text-sm"
                                        required
                                    >
                                        {users.map(u => (
                                            <option key={u.id} value={u.id}>{u.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="text-xs uppercase text-gray-500 font-bold">Typ urlopu</label>
                                    <select
                                        value={balanceForm.leave_type_id}
                                        onChange={e => setBalanceForm({ ...balanceForm, leave_type_id: e.target.value })}
                                        className="w-full border rounded p-2 mt-1 text-sm"
                                        required
                                    >
                                        {leaveTypes.map(t => (
                                            <option key={t.id} value={t.id}>{t.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="text-xs uppercase text-gray-500 font-bold">Rok</label>
                                    <input
                                        type="number"
                                        value={balanceForm.year}
                                        onChange={e => setBalanceForm({ ...balanceForm, year: e.target.value })}
                                        className="w-full border rounded p-2 mt-1 text-sm"
                                        required
                                        min="2020"
                                        max="2099"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs uppercase text-gray-500 font-bold">Liczba dni</label>
                                    <input
                                        type="number"
                                        value={balanceForm.total_days}
                                        onChange={e => setBalanceForm({ ...balanceForm, total_days: e.target.value })}
                                        className="w-full border rounded p-2 mt-1 text-sm"
                                        required
                                        min="1"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    className="bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 text-sm"
                                >
                                    Dodaj limit
                                </button>
                            </form>
                            {balanceMsg && (
                                <p className="mt-3 text-sm text-green-600">{balanceMsg}</p>
                            )}
                        </div>

                        {/* Tabela limitów */}
                        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                            <div className="p-4 border-b">
                                <h2 className="text-lg font-semibold text-gray-700">Limity urlopowe pracowników</h2>
                            </div>
                            {balancesLoading ? (
                                <div className="p-8 text-center text-gray-400">Ładowanie...</div>
                            ) : (
                                <table className="w-full text-left text-sm">
                                    <thead className="bg-gray-50 border-b">
                                        <tr>
                                            <th className="p-3 text-gray-500">Pracownik</th>
                                            <th className="p-3 text-gray-500">Typ urlopu</th>
                                            <th className="p-3 text-gray-500">Rok</th>
                                            <th className="p-3 text-gray-500">Przyznane</th>
                                            <th className="p-3 text-gray-500">Wykorzystane</th>
                                            <th className="p-3 text-gray-500">Pozostało</th>
                                            <th className="p-3 text-right text-gray-500">Akcje</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {balances.length === 0 && (
                                            <tr><td colSpan={7} className="p-8 text-center text-gray-400">Brak zdefiniowanych limitów</td></tr>
                                        )}
                                        {balances.map(b => (
                                            <tr key={b.id} className="border-b last:border-0 hover:bg-gray-50">
                                                <td className="p-3 font-medium">{b.user_name}</td>
                                                <td className="p-3 text-gray-600">{b.leave_type_name}</td>
                                                <td className="p-3">{b.year}</td>
                                                <td className="p-3">
                                                    {editingBalance?.id === b.id ? (
                                                        <form onSubmit={submitEditBalance} className="flex items-center gap-2">
                                                            <input
                                                                type="number"
                                                                value={editTotalDays}
                                                                onChange={e => setEditTotalDays(e.target.value)}
                                                                className="border rounded p-1 w-16 text-center text-sm"
                                                                min={b.used_days}
                                                                required
                                                                autoFocus
                                                            />
                                                            <button type="submit" className="text-blue-600 text-xs font-bold hover:underline">Zapisz</button>
                                                            <button type="button" onClick={() => setEditingBalance(null)} className="text-gray-400 text-xs hover:underline">Anuluj</button>
                                                        </form>
                                                    ) : (
                                                        <span className="font-semibold">{b.total_days}</span>
                                                    )}
                                                </td>
                                                <td className="p-3 text-orange-600">{b.used_days}</td>
                                                <td className="p-3">
                                                    <span className={`font-semibold ${b.remaining_days > 0 ? 'text-green-600' : 'text-red-500'}`}>
                                                        {b.remaining_days}
                                                    </span>
                                                </td>
                                                <td className="p-3 text-right">
                                                    {editingBalance?.id !== b.id && (
                                                        <button
                                                            onClick={() => openEditBalance(b)}
                                                            className="text-blue-500 text-xs hover:underline"
                                                        >
                                                            Edytuj
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default HRPanel;
