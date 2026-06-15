import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const MONTH_NAMES = [
    'Styczeń','Luty','Marzec','Kwiecień','Maj','Czerwiec',
    'Lipiec','Sierpień','Wrzesień','Październik','Listopad','Grudzień'
];
const DAY_NAMES = ['Pn','Wt','Śr','Cz','Pt','Sb','Nd'];

const buildLeaveMap = (teamLeaves) => {
    const map = {};
    teamLeaves.forEach(leave => {
        const start = new Date(leave.start + 'T00:00:00');
        const end   = new Date(leave.end   + 'T00:00:00');
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            const key = d.toISOString().slice(0, 10);
            if (!map[key]) map[key] = [];
            map[key].push(leave);
        }
    });
    return map;
};

const Calendar = ({ teamLeaves }) => {
    const today = new Date();
    const [year, setYear]   = useState(today.getFullYear());
    const [month, setMonth] = useState(today.getMonth());
    const leaveMap  = buildLeaveMap(teamLeaves);
    const daysInMonth  = new Date(year, month + 1, 0).getDate();
    const firstDayOfWeek = (new Date(year, month, 1).getDay() + 6) % 7;
    const cells = [];
    for (let i = 0; i < firstDayOfWeek; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) cells.push(d);

    const prevMonth = () => { if (month === 0) { setMonth(11); setYear(y => y - 1); } else setMonth(m => m - 1); };
    const nextMonth = () => { if (month === 11) { setMonth(0); setYear(y => y + 1); } else setMonth(m => m + 1); };

    return (
        <div>
            <div className="flex items-center justify-between mb-4">
                <button onClick={prevMonth} className="p-2 rounded hover:bg-gray-100 text-lg font-bold">‹</button>
                <span className="text-lg font-semibold text-gray-700">{MONTH_NAMES[month]} {year}</span>
                <button onClick={nextMonth} className="p-2 rounded hover:bg-gray-100 text-lg font-bold">›</button>
            </div>
            <div className="grid grid-cols-7 mb-1">
                {DAY_NAMES.map(d => (
                    <div key={d} className="text-center text-xs font-bold text-gray-400 py-1">{d}</div>
                ))}
            </div>
            <div className="grid grid-cols-7 gap-1">
                {cells.map((day, i) => {
                    if (!day) return <div key={i} />;
                    const dateKey = `${year}-${String(month + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
                    const dayLeaves = leaveMap[dateKey] || [];
                    const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
                    return (
                        <div key={i} className={`min-h-16 p-1 rounded border text-xs
                            ${isToday ? 'border-blue-400 bg-blue-50' : 'border-gray-100 bg-white'}`}>
                            <div className={`font-semibold mb-1 ${isToday ? 'text-blue-600' : 'text-gray-500'}`}>{day}</div>
                            {dayLeaves.slice(0, 2).map((l, j) => (
                                <div key={j} title={`${l.user_name} – ${l.status}`}
                                    className={`rounded px-1 py-0.5 mb-0.5 truncate font-medium
                                        ${l.status === 'APPROVED' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                                    {l.user_name.split(' ')[0]}
                                </div>
                            ))}
                            {dayLeaves.length > 2 && (
                                <div className="text-gray-400 text-center">+{dayLeaves.length - 2}</div>
                            )}
                        </div>
                    );
                })}
            </div>
            <div className="mt-3 flex gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                    <span className="inline-block w-3 h-3 rounded bg-green-200" /> Zaakceptowany
                </span>
                <span className="flex items-center gap-1">
                    <span className="inline-block w-3 h-3 rounded bg-yellow-200" /> Oczekujący
                </span>
            </div>
        </div>
    );
};


const ManagerPanel = () => {
    const [teamLeaves, setTeamLeaves] = useState([]);
    const [view, setView] = useState('calendar');

    const [rejectionTexts, setRejectionTexts] = useState({});

    useEffect(() => { fetchTeamLeaves(); }, []);

    const fetchTeamLeaves = async () => {
        const res = await api.get('/manager/team-leaves');
        setTeamLeaves(res.data);
    };

    const setRejection = (id, value) =>
        setRejectionTexts(prev => ({ ...prev, [id]: value }));

    const handleAction = async (leave, action) => {
        const comment = rejectionTexts[leave.id] || '';

        if (action === 'REJECTED' && !comment.trim()) {
            alert('Uzasadnienie odrzucenia jest wymagane.');
            return;
        }

        try {
            await api.patch(`/manager/leaves/${leave.id}/status`, {
                status: action,
                comment: comment.trim() || null,
            });
            setRejectionTexts(prev => { const n = { ...prev }; delete n[leave.id]; return n; });
            await fetchTeamLeaves();
        } catch (err) {
            alert(err.response?.data?.msg || 'Błąd operacji');
        }
    };

    const pendingLeaves = teamLeaves.filter(l => l.status === 'PENDING');

  
    const PendingCard = ({ l }) => (
        <div className="p-4 rounded-lg bg-yellow-50 border border-yellow-100 space-y-3">
            <div className="flex items-start justify-between gap-4">
                <div>
                    <span className="font-semibold text-gray-800">{l.user_name}</span>
                    <span className="text-gray-500 text-sm ml-3">{l.start} – {l.end}</span>
                    {l.reason && (
                        <span className="text-gray-400 text-sm ml-3 italic">„{l.reason}"</span>
                    )}
                </div>
            </div>

          
            <div>
                <label className="text-xs font-bold text-gray-500 uppercase">
                    Uzasadnienie odrzucenia <span className="text-red-500">*</span>
                    <span className="normal-case font-normal text-gray-400 ml-1">(wymagane tylko przy odrzuceniu)</span>
                </label>
                <textarea
                    rows={2}
                    className="mt-1 w-full border rounded p-2 text-sm resize-none focus:ring-1 focus:ring-red-300"
                    placeholder="Wpisz powód odrzucenia wniosku..."
                    value={rejectionTexts[l.id] || ''}
                    onChange={e => setRejection(l.id, e.target.value)}
                />
            </div>

            <div className="flex gap-2">
                <button
                    onClick={() => handleAction(l, 'APPROVED')}
                    className="bg-green-500 hover:bg-green-600 text-white px-4 py-1.5 rounded text-sm font-semibold"
                >
                    Akceptuj
                </button>
                <button
                    onClick={() => handleAction(l, 'REJECTED')}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-1.5 rounded text-sm font-semibold"
                >
                    Odrzuć
                </button>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-6xl mx-auto space-y-6">

                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-800">Panel Menedżera</h1>
                    <div className="flex gap-3">
                        <button
                            onClick={() => setView(view === 'calendar' ? 'list' : 'calendar')}
                            className="bg-white border px-4 py-2 rounded text-sm font-medium text-gray-600 hover:bg-gray-50"
                        >
                            {view === 'calendar' ? 'Lista wniosków' : 'Kalendarz'}
                        </button>
                        <button
                            onClick={() => window.location.href = '/dashboard'}
                            className="bg-gray-200 px-4 py-2 rounded text-sm"
                        >
                            Mój Panel
                        </button>
                    </div>
                </div>

               
                {view === 'calendar' && (
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <h2 className="text-lg font-semibold text-gray-700 mb-4">Kalendarz nieobecności zespołu</h2>
                        <Calendar teamLeaves={teamLeaves} />
                    </div>
                )}

      
                {view === 'list' && (
                    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="p-4 text-gray-500">Pracownik</th>
                                    <th className="p-4 text-gray-500">Termin</th>
                                    <th className="p-4 text-gray-500">Status</th>
                                    <th className="p-4 text-gray-500">Uzasadnienie pracownika</th>
                                    <th className="p-4 text-gray-500">Komentarz menadżera</th>
                                    <th className="p-4 text-gray-500 min-w-64">
                                        Uzasadnienie odrzucenia
                                        <span className="text-red-500 ml-1">*</span>
                                    </th>
                                    <th className="p-4 text-right text-gray-500">Akcje</th>
                                </tr>
                            </thead>
                            <tbody>
                                {teamLeaves.length === 0 && (
                                    <tr><td colSpan={7} className="p-8 text-center text-gray-400">Brak wniosków</td></tr>
                                )}
                                {teamLeaves.map(l => (
                                    <tr key={l.id} className="border-b last:border-0 hover:bg-gray-50 align-top">
                                        <td className="p-4 font-medium">{l.user_name}</td>
                                        <td className="p-4 whitespace-nowrap">{l.start} – {l.end}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-0.5 rounded text-xs font-bold
                                                ${l.status === 'APPROVED' ? 'bg-green-100 text-green-700' :
                                                  l.status === 'PENDING'  ? 'bg-yellow-100 text-yellow-700' :
                                                  l.status === 'REJECTED' ? 'bg-red-100 text-red-700' :
                                                                            'bg-gray-100 text-gray-500'}`}>
                                                {l.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-500 text-xs">{l.reason || '—'}</td>
                                        <td className="p-4 text-gray-500 text-xs">{l.comment || '—'}</td>

                                       
                                        <td className="p-4">
                                            {l.status === 'PENDING' ? (
                                                <textarea
                                                    rows={2}
                                                    className="w-full border rounded p-2 text-xs resize-none focus:ring-1 focus:ring-red-300"
                                                    placeholder="Wymagane przy odrzuceniu..."
                                                    value={rejectionTexts[l.id] || ''}
                                                    onChange={e => setRejection(l.id, e.target.value)}
                                                />
                                            ) : (
                                                <span className="text-gray-300 text-xs">—</span>
                                            )}
                                        </td>

                                        <td className="p-4 text-right space-x-2 whitespace-nowrap">
                                            {l.status === 'PENDING' && (
                                                <>
                                                    <button
                                                        onClick={() => handleAction(l, 'APPROVED')}
                                                        className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                                                    >
                                                        Akceptuj
                                                    </button>
                                                    <button
                                                        onClick={() => handleAction(l, 'REJECTED')}
                                                        className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                                                    >
                                                        Odrzuć
                                                    </button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

               
                {view === 'calendar' && pendingLeaves.length > 0 && (
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <h2 className="text-lg font-semibold text-gray-700 mb-4">
                            Wnioski oczekujące na decyzję
                            <span className="ml-2 bg-yellow-100 text-yellow-700 text-sm px-2 py-0.5 rounded-full font-normal">
                                {pendingLeaves.length}
                            </span>
                        </h2>
                        <div className="space-y-3">
                            {pendingLeaves.map(l => <PendingCard key={l.id} l={l} />)}
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default ManagerPanel;
