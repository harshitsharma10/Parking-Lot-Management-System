import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import type { ParkingSession } from '../../types'

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    dateStyle: 'short',
    timeStyle: 'short',
  })
}

export default function MySessions() {
  const [sessions, setSessions] = useState<ParkingSession[]>([])
  const [loading, setLoading] = useState(true)
  const [exiting, setExiting] = useState<number | null>(null)
  const navigate = useNavigate()

  const fetchSessions = async () => {
    try {
      const res = await api.get('/parking/my-sessions')
      // Sort: ACTIVE first, then by created date desc
      const sorted = [...res.data].sort((a, b) => {
        if (a.status === 'ACTIVE' && b.status !== 'ACTIVE') return -1
        if (a.status !== 'ACTIVE' && b.status === 'ACTIVE') return 1
        return b.id - a.id
      })
      setSessions(sorted)
    } catch {
      // handle silently
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchSessions() }, [])

  const handleExit = async (sessionId: number) => {
    setExiting(sessionId)
    try {
      const res = await api.post(`/parking/exit/${sessionId}`)
      if (res.data.warning) {
        alert(res.data.warning)   
      }
      await fetchSessions()
    } catch (err: any) {
      alert(err.response?.data?.detail ?? 'Exit failed')
    } finally {
      setExiting(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <span className="text-white/20 font-mono text-sm tracking-widest uppercase">Loading...</span>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">

      <div className="mb-10">
        <Link to="/dashboard" className="text-white/20 hover:text-white/50 font-mono text-xs tracking-widest uppercase transition-colors">
          ← Back
        </Link>
        <p className="text-white/20 font-mono text-xs tracking-widest uppercase mt-6 mb-3">
          All sessions
        </p>
        <h1 className="text-white text-4xl font-light">My Sessions</h1>
        <div className="w-12 h-px bg-[#e8ff47] mt-4" />
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-16 border border-white/8 rounded-xl">
          <p className="text-white/20 font-mono text-sm">No sessions yet</p>
          <Link to="/dashboard" className="text-[#e8ff47]/60 hover:text-[#e8ff47] font-mono text-xs mt-3 inline-block transition-colors">
            Start parking →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map(session => (
            <div
              key={session.id}
              className="bg-white/3 border border-white/8 rounded-xl p-5"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-white font-mono tracking-widest text-sm">
                      {session.vehicle_number}
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full
                      ${session.status === 'ACTIVE'
                        ? 'bg-[#e8ff47] text-[#0f0f0f] font-bold'
                        : 'bg-white/10 text-white/40'
                      }`}>
                      {session.status}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 text-white/30">
                      {session.parking_type}
                    </span>
                  </div>
                  <p className="text-white/30 text-xs font-mono">
                    {session.vehicle_type} · Slot #{session.slot_id}
                  </p>
                </div>

                {session.amount_charged !== null && (
                  <span className="text-white font-light text-xl">
                    ₹{session.amount_charged}
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <p className="text-white/20 text-[10px] font-mono uppercase tracking-widest mb-1">Entry</p>
                  <p className="text-white/60 text-xs font-mono">{formatTime(session.entry_time)}</p>
                </div>
                {session.actual_exit_time && (
                  <div>
                    <p className="text-white/20 text-[10px] font-mono uppercase tracking-widest mb-1">Exit</p>
                    <p className="text-white/60 text-xs font-mono">{formatTime(session.actual_exit_time)}</p>
                  </div>
                )}
                {session.expected_exit_time && session.status === 'ACTIVE' && (
                  <div>
                    <p className="text-white/20 text-[10px] font-mono uppercase tracking-widest mb-1">Expected Exit</p>
                    <p className="text-white/60 text-xs font-mono">{formatTime(session.expected_exit_time)}</p>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => navigate(`/ticket/${session.id}?from=user`)}
                  className="text-xs font-mono tracking-widest uppercase px-4 py-2 rounded-lg
                             bg-white/5 border border-white/10 text-white/40
                             hover:border-white/20 hover:text-white/70 transition-all"
                >
                  View Ticket
                </button>

                {session.status === 'ACTIVE' && (
                  <button
                    onClick={() => handleExit(session.id)}
                    disabled={exiting === session.id}
                    className="text-xs font-mono tracking-widest uppercase px-4 py-2 rounded-lg
                               bg-[#e8ff47] text-[#0f0f0f] font-bold
                               hover:bg-[#d4eb3a] active:scale-[0.98]
                               disabled:opacity-50 disabled:cursor-not-allowed
                               transition-all duration-150"
                  >
                    {exiting === session.id ? 'Exiting...' : 'Exit Now'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}