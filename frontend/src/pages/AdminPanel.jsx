import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const ROLES = ['EMPLOYEE', 'MANAGER', 'HR', 'ADMIN'];

const Input = ({ label, ...props }) => (
    <div>
        <label className="text-xs uppercase text-gray-500 font-bold">{label}</label>
        <input className="w-full border rounded p-2 mt-1 text-sm" {...props} />
    </div>
);

const Select = ({ label, children, ...props }) => (
    <div>
        <label className="text-xs uppercase text-gray-500 font-bold">{label}</label>
        <select className="w-full border rounded p-2 mt-1 text-sm" {...props}>{children}</select>
    </div>
);

const Msg = ({ text, error }) => text
    ? <p className={`mt-3 text-sm ${error ? 'text-red-600' : 'text-green-600'}`}>{text}</p>
    : null;

const AdminPanel = () => {
    const [activeTab, setActiveTab] = useState('users');

    const [users, setUsers]           = useState([]);
    const [departments, setDepartments] = useState([]);
    const [leaveTypes, setLeaveTypes]  = useState([]);

    // ── users ─────────────────────────────────────────────────────────────────
    const emptyUserForm = {
        email: '', password: '', first_name: '', last_name: '',
        role: 'EMPLOYEE', manager_id: '', department_id: '',
    };
    const [newUserForm, setNewUserForm]   = useState(emptyUserForm);
    const [editingUser, setEditingUser]   = useState(null);
    const [editUserForm, setEditUserForm] = useState({ role: '', manager_id: '', department_id: '' });
    const [userMsg, setUserMsg]           = useState({ text: '', error: false });

    // ── departments ───────────────────────────────────────────────────────────
    const [newDeptName, setNewDeptName] = useState('');
    const [deptMsg, setDeptMsg]         = useState({ text: '', error: false });

    // ── leave types ───────────────────────────────────────────────────────────
    const [newLeaveType, setNewLeaveType] = useState({ name: '', requires_approval: true });
    const [ltMsg, setLtMsg]               = useState({ text: '', error: false });

    // ── balances ──────────────────────────────────────────────────────────────
    const [balances, setBalances]         = useState([]);
    const [balanceForm, setBalanceForm]   = useState({
        user_id: '', leave_type_id: '', year: new Date().getFullYear(), total_days: '',
    });
    const [editingBalance, setEditingBalance] = useState(null);
    const [editTotalDays, setEditTotalDays]   = useState('');
    const [balanceMsg, setBalanceMsg]         = useState({ text: '', error: false });

    // ── helpers ───────────────────────────────────────────────────────────────
    const flash = (setter, text, error = false) => {
        setter({ text, error });
        setTimeout(() => setter({ text: '', error: false }), 3500);
    };

    const fetchCore = async () => {
        const [uRes, dRes, ltRes] = await Promise.all([
            api.get('/admin/users'),
            api.get('/admin/departments'),
            api.get('/admin/leave-types'),
        ]);
        setUsers(uRes.data);
        setDepartments(dRes.data);
        setLeaveTypes(ltRes.data);
        setBalanceForm(f => ({
            ...f,
            user_id: f.user_id || (uRes.data[0]?.id ?? ''),
            leave_type_id: f.leave_type_id || (ltRes.data[0]?.id ?? ''),
        }));
    };

    const fetchBalances = async () => {
        const res = await api.get('/hr/balances');
        setBalances(res.data);
    };

    useEffect(() => { fetchCore(); }, []);
    useEffect(() => { if (activeTab === 'balances') fetchBalances(); }, [activeTab]);

    const managerName = (id) => {
        if (!id) return '—';
        const u = users.find(u => u.id === id);
        return u ? `${u.first_name} ${u.last_name}` : `#${id}`;
    };

    // ── user CRUD ─────────────────────────────────────────────────────────────
    const submitNewUser = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/users', {
                ...newUserForm,
                manager_id: newUserForm.manager_id || null,
                department_id: newUserForm.department_id || null,
            });
            setNewUserForm(emptyUserForm);
            await fetchCore();
            flash(setUserMsg, 'Użytkownik dodany pomyślnie.');
        } catch (err) {
            flash(setUserMsg, err.response?.data?.msg || 'Błąd.', true);
        }
    };

    const openEditUser = (u) => {
        setEditingUser(u);
        setEditUserForm({
            role: u.role,
            manager_id: u.manager_id ?? '',
            department_id: u.department_id ?? '',
        });
    };

    const submitEditUser = async (e) => {
        e.preventDefault();
        try {
            await api.patch(`/admin/users/${editingUser.id}`, {
                role: editUserForm.role,
                manager_id: editUserForm.manager_id || null,
                department_id: editUserForm.department_id || null,
            });
            setEditingUser(null);
            await fetchCore();
            flash(setUserMsg, 'Użytkownik zaktualizowany.');
        } catch (err) {
            flash(setUserMsg, err.response?.data?.msg || 'Błąd.', true);
        }
    };

    // ── department CRUD ───────────────────────────────────────────────────────
    const submitNewDept = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/departments', { name: newDeptName });
            setNewDeptName('');
            await fetchCore();
            flash(setDeptMsg, 'Dział dodany pomyślnie.');
        } catch (err) {
            flash(setDeptMsg, err.response?.data?.msg || 'Błąd.', true);
        }
    };

    // ── leave type CRUD ───────────────────────────────────────────────────────
    const submitNewLeaveType = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/leave-types', newLeaveType);
            setNewLeaveType({ name: '', requires_approval: true });
            await fetchCore();
            flash(setLtMsg, 'Typ urlopu dodany pomyślnie.');
        } catch (err) {
            flash(setLtMsg, err.response?.data?.msg || 'Błąd.', true);
        }
    };

    // ── balance CRUD ──────────────────────────────────────────────────────────
    const submitBalance = async (e) => {
        e.preventDefault();
        try {
            await api.post('/hr/balances', {
                user_id: Number(balanceForm.user_id),
                leave_type_id: Number(balanceForm.leave_type_id),
                year: Number(balanceForm.year),
                total_days: Number(balanceForm.total_days),
            });
            setBalanceForm(f => ({ ...f, total_days: '' }));
            await fetchBalances();
            flash(setBalanceMsg, 'Limit dodany pomyślnie.');
        } catch (err) {
            flash(setBalanceMsg, err.response?.data?.msg || 'Błąd.', true);
        }
    };

    const submitEditBalance = async (e) => {
        e.preventDefault();
        try {
            await api.patch(`/hr/balances/${editingBalance.id}`, {
                total_days: Number(editTotalDays),
            });
            setEditingBalance(null);
            await fetchBalances();
            flash(setBalanceMsg, 'Limit zaktualizowany.');
        } catch (err) {
            flash(setBalanceMsg, err.response?.data?.msg || 'Błąd.', true);
        }
    };

    // ── render ─────────────────────────────────────────────────────────────────
    const TABS = [
        { key: 'users',       label: 'Użytkownicy' },
        { key: 'departments', label: 'Działy' },
        { key: 'leave-types', label: 'Typy urlopów' },
        { key: 'balances',    label: 'Limity urlopowe' },
    ];

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto space-y-6">

                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-800">Panel Administratora</h1>
                        <p className="text-sm text-gray-400 mt-0.5">Zarządzanie użytkownikami, działami i parametrami systemu</p>
                    </div>
                    <button
                        onClick={() => { localStorage.clear(); window.location.href = '/login'; }}
                        className="text-red-500 font-medium text-sm hover:underline"
                    >
                        Wyloguj
                    </button>
                </div>

                {/* tab bar */}
                <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
                    {TABS.map(t => (
                        <button
                            key={t.key}
                            onClick={() => setActiveTab(t.key)}
                            className={`px-5 py-2 rounded-md text-sm font-medium transition ${
                                activeTab === t.key
                                    ? 'bg-white shadow text-blue-600'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>

                {/* ── USERS ───────────────────────────────────────────────── */}
                {activeTab === 'users' && (
                    <>
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-lg font-semibold text-gray-700 mb-4">Dodaj użytkownika</h2>
                            <form onSubmit={submitNewUser} className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                <Input label="Imię" value={newUserForm.first_name} required
                                    onChange={e => setNewUserForm({ ...newUserForm, first_name: e.target.value })} />
                                <Input label="Nazwisko" value={newUserForm.last_name} required
                                    onChange={e => setNewUserForm({ ...newUserForm, last_name: e.target.value })} />
                                <Input label="Email" type="email" value={newUserForm.email} required
                                    onChange={e => setNewUserForm({ ...newUserForm, email: e.target.value })} />
                                <Input label="Hasło" type="password" value={newUserForm.password} required
                                    onChange={e => setNewUserForm({ ...newUserForm, password: e.target.value })} />
                                <Select label="Rola" value={newUserForm.role}
                                    onChange={e => setNewUserForm({ ...newUserForm, role: e.target.value })}>
                                    {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                                </Select>
                                <Select label="Menadżer (opcjonalnie)" value={newUserForm.manager_id}
                                    onChange={e => setNewUserForm({ ...newUserForm, manager_id: e.target.value })}>
                                    <option value="">— brak —</option>
                                    {users.filter(u => u.role === 'MANAGER').map(u => (
                                        <option key={u.id} value={u.id}>{u.first_name} {u.last_name}</option>
                                    ))}
                                </Select>
                                <Select label="Dział (opcjonalnie)" value={newUserForm.department_id}
                                    onChange={e => setNewUserForm({ ...newUserForm, department_id: e.target.value })}>
                                    <option value="">— brak —</option>
                                    {departments.map(d => (
                                        <option key={d.id} value={d.id}>{d.name}</option>
                                    ))}
                                </Select>
                                <div className="md:col-span-3">
                                    <button type="submit"
                                        className="bg-blue-600 text-white font-bold py-2 px-6 rounded hover:bg-blue-700 text-sm">
                                        Dodaj użytkownika
                                    </button>
                                </div>
                            </form>
                            <Msg text={userMsg.text} error={userMsg.error} />
                        </div>

                        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                            <div className="p-4 border-b">
                                <h2 className="text-lg font-semibold text-gray-700">
                                    Lista użytkowników ({users.length})
                                </h2>
                            </div>
                            <table className="w-full text-left text-sm">
                                <thead className="bg-gray-50 border-b">
                                    <tr>
                                        {['Imię i nazwisko', 'Email', 'Rola', 'Menadżer', 'Dział', ''].map(h => (
                                            <th key={h} className="p-3 text-gray-500 font-medium">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.length === 0 && (
                                        <tr><td colSpan={6} className="p-8 text-center text-gray-400">Brak użytkowników</td></tr>
                                    )}
                                    {users.map(u => (
                                        <tr key={u.id} className="border-b last:border-0 hover:bg-gray-50">
                                            <td className="p-3 font-medium">{u.first_name} {u.last_name}</td>
                                            <td className="p-3 text-gray-600">{u.email}</td>
                                            <td className="p-3">
                                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                                    u.role === 'ADMIN'    ? 'bg-purple-100 text-purple-700' :
                                                    u.role === 'MANAGER'  ? 'bg-blue-100 text-blue-700' :
                                                    u.role === 'HR'       ? 'bg-teal-100 text-teal-700' :
                                                                            'bg-gray-100 text-gray-600'
                                                }`}>{u.role}</span>
                                            </td>
                                            <td className="p-3 text-gray-500 text-xs">{managerName(u.manager_id)}</td>
                                            <td className="p-3 text-gray-500 text-xs">{u.department_name || '—'}</td>
                                            <td className="p-3 text-right">
                                                <button
                                                    onClick={() => openEditUser(u)}
                                                    className="text-blue-500 text-xs hover:underline"
                                                >
                                                    Edytuj
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}

                {/* ── DEPARTMENTS ─────────────────────────────────────────── */}
                {activeTab === 'departments' && (
                    <>
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-lg font-semibold text-gray-700 mb-4">Dodaj dział</h2>
                            <form onSubmit={submitNewDept} className="flex gap-3 items-end">
                                <div className="flex-1">
                                    <Input label="Nazwa działu" value={newDeptName} required
                                        onChange={e => setNewDeptName(e.target.value)} />
                                </div>
                                <button type="submit"
                                    className="bg-blue-600 text-white font-bold py-2 px-6 rounded hover:bg-blue-700 text-sm h-[38px]">
                                    Dodaj dział
                                </button>
                            </form>
                            <Msg text={deptMsg.text} error={deptMsg.error} />
                        </div>

                        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                            <div className="p-4 border-b">
                                <h2 className="text-lg font-semibold text-gray-700">
                                    Lista działów ({departments.length})
                                </h2>
                            </div>
                            <table className="w-full text-left text-sm">
                                <thead className="bg-gray-50 border-b">
                                    <tr>
                                        <th className="p-3 text-gray-500">ID</th>
                                        <th className="p-3 text-gray-500">Nazwa</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {departments.length === 0 && (
                                        <tr><td colSpan={2} className="p-8 text-center text-gray-400">Brak działów</td></tr>
                                    )}
                                    {departments.map(d => (
                                        <tr key={d.id} className="border-b last:border-0 hover:bg-gray-50">
                                            <td className="p-3 text-gray-400">#{d.id}</td>
                                            <td className="p-3 font-medium">{d.name}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}

                {/* ── LEAVE TYPES ─────────────────────────────────────────── */}
                {activeTab === 'leave-types' && (
                    <>
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-lg font-semibold text-gray-700 mb-4">Dodaj typ urlopu</h2>
                            <form onSubmit={submitNewLeaveType} className="flex flex-wrap gap-3 items-end">
                                <div className="flex-1 min-w-48">
                                    <Input label="Nazwa" value={newLeaveType.name} required
                                        onChange={e => setNewLeaveType({ ...newLeaveType, name: e.target.value })} />
                                </div>
                                <div className="flex items-center gap-2 pb-2">
                                    <input
                                        type="checkbox"
                                        id="requires_approval"
                                        checked={newLeaveType.requires_approval}
                                        onChange={e => setNewLeaveType({ ...newLeaveType, requires_approval: e.target.checked })}
                                        className="w-4 h-4"
                                    />
                                    <label htmlFor="requires_approval" className="text-sm text-gray-600">
                                        Wymaga akceptacji menadżera
                                    </label>
                                </div>
                                <button type="submit"
                                    className="bg-blue-600 text-white font-bold py-2 px-6 rounded hover:bg-blue-700 text-sm h-[38px]">
                                    Dodaj typ
                                </button>
                            </form>
                            <Msg text={ltMsg.text} error={ltMsg.error} />
                        </div>

                        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                            <div className="p-4 border-b">
                                <h2 className="text-lg font-semibold text-gray-700">
                                    Typy urlopów ({leaveTypes.length})
                                </h2>
                            </div>
                            <table className="w-full text-left text-sm">
                                <thead className="bg-gray-50 border-b">
                                    <tr>
                                        <th className="p-3 text-gray-500">ID</th>
                                        <th className="p-3 text-gray-500">Nazwa</th>
                                        <th className="p-3 text-gray-500">Wymaga akceptacji</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {leaveTypes.length === 0 && (
                                        <tr><td colSpan={3} className="p-8 text-center text-gray-400">Brak typów urlopów</td></tr>
                                    )}
                                    {leaveTypes.map(t => (
                                        <tr key={t.id} className="border-b last:border-0 hover:bg-gray-50">
                                            <td className="p-3 text-gray-400">#{t.id}</td>
                                            <td className="p-3 font-medium">{t.name}</td>
                                            <td className="p-3">
                                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                                    t.requires_approval
                                                        ? 'bg-yellow-100 text-yellow-700'
                                                        : 'bg-green-100 text-green-700'
                                                }`}>
                                                    {t.requires_approval ? 'Tak' : 'Nie'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}

                {/* ── BALANCES ────────────────────────────────────────────── */}
                {activeTab === 'balances' && (
                    <>
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-lg font-semibold text-gray-700 mb-4">Dodaj limit urlopowy</h2>
                            <form onSubmit={submitBalance} className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
                                <Select label="Pracownik" value={balanceForm.user_id} required
                                    onChange={e => setBalanceForm({ ...balanceForm, user_id: e.target.value })}>
                                    {users.map(u => (
                                        <option key={u.id} value={u.id}>{u.first_name} {u.last_name}</option>
                                    ))}
                                </Select>
                                <Select label="Typ urlopu" value={balanceForm.leave_type_id} required
                                    onChange={e => setBalanceForm({ ...balanceForm, leave_type_id: e.target.value })}>
                                    {leaveTypes.map(t => (
                                        <option key={t.id} value={t.id}>{t.name}</option>
                                    ))}
                                </Select>
                                <Input label="Rok" type="number" min="2020" max="2099" value={balanceForm.year} required
                                    onChange={e => setBalanceForm({ ...balanceForm, year: e.target.value })} />
                                <Input label="Liczba dni" type="number" min="1" value={balanceForm.total_days} required
                                    onChange={e => setBalanceForm({ ...balanceForm, total_days: e.target.value })} />
                                <button type="submit"
                                    className="bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 text-sm h-[38px]">
                                    Dodaj limit
                                </button>
                            </form>
                            <Msg text={balanceMsg.text} error={balanceMsg.error} />
                        </div>

                        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                            <div className="p-4 border-b">
                                <h2 className="text-lg font-semibold text-gray-700">Limity urlopowe pracowników</h2>
                            </div>
                            <table className="w-full text-left text-sm">
                                <thead className="bg-gray-50 border-b">
                                    <tr>
                                        {['Pracownik', 'Typ urlopu', 'Rok', 'Przyznane', 'Wykorzystane', 'Pozostało', ''].map(h => (
                                            <th key={h} className="p-3 text-gray-500 font-medium">{h}</th>
                                        ))}
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
                                                            type="number" min={b.used_days} required autoFocus
                                                            value={editTotalDays}
                                                            onChange={e => setEditTotalDays(e.target.value)}
                                                            className="border rounded p-1 w-16 text-center text-sm"
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
                                                        onClick={() => { setEditingBalance(b); setEditTotalDays(String(b.total_days)); }}
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
                        </div>
                    </>
                )}
            </div>

            {/* ── edit user modal ──────────────────────────────────────────── */}
            {editingUser && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
                        <h3 className="text-lg font-bold text-gray-800 mb-1">Edytuj użytkownika</h3>
                        <p className="text-sm text-gray-500 mb-4">
                            {editingUser.first_name} {editingUser.last_name} · {editingUser.email}
                        </p>
                        <form onSubmit={submitEditUser} className="space-y-4">
                            <Select label="Rola" value={editUserForm.role}
                                onChange={e => setEditUserForm({ ...editUserForm, role: e.target.value })}>
                                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                            </Select>
                            <Select label="Menadżer" value={editUserForm.manager_id}
                                onChange={e => setEditUserForm({ ...editUserForm, manager_id: e.target.value })}>
                                <option value="">— brak —</option>
                                {users
                                    .filter(u => u.id !== editingUser.id && u.role === 'MANAGER')
                                    .map(u => (
                                        <option key={u.id} value={u.id}>{u.first_name} {u.last_name}</option>
                                    ))}
                            </Select>
                            <Select label="Dział" value={editUserForm.department_id}
                                onChange={e => setEditUserForm({ ...editUserForm, department_id: e.target.value })}>
                                <option value="">— brak —</option>
                                {departments.map(d => (
                                    <option key={d.id} value={d.id}>{d.name}</option>
                                ))}
                            </Select>
                            <div className="flex gap-3 justify-end pt-2">
                                <button type="button" onClick={() => setEditingUser(null)}
                                    className="px-4 py-2 border rounded text-gray-600 hover:bg-gray-50 text-sm">
                                    Anuluj
                                </button>
                                <button type="submit"
                                    className="px-4 py-2 bg-blue-600 text-white font-bold rounded hover:bg-blue-700 text-sm">
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

export default AdminPanel;
