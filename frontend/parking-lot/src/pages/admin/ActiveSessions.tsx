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

export default function ActiveSessions() {
  const [sessions, setSessions] = useState<ParkingSession[]>([])
  const [loading, setLoading] = useState(true)
  const [exiting, setExiting] = useState<number | null>(null)
  const navigate = useNavigate()

  const fetchSessions = async () => {
    try {
      const res = await api.get('/admin/sessions')
      setSessions(res.data)
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
      await api.post(`/parking/exit/${sessionId}`)
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
    <div className="max-w-4xl mx-auto py-12 px-4">

      {/* Header */}
      <div className="mb-10">
        <p className="text-white/20 font-mono text-xs tracking-widest uppercase mb-3">Admin</p>
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-white text-4xl font-light">Active Sessions</h1>
            <div className="w-12 h-px bg-[#e8ff47] mt-4" />
          </div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 bg-[#e8ff47] rounded-full animate-pulse" />
            <span className="text-white/30 font-mono text-xs uppercase tracking-widest">
              {sessions.length} active
            </span>
          </div>
        </div>
      </div>

      {/* Refresh + nav */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={fetchSessions}
          className="px-4 py-2 rounded-lg text-xs font-mono tracking-widest uppercase
                     bg-white/5 border border-white/10 text-white/40 hover:text-white/70 transition-all"
        >
          ↻ Refresh
        </button>
        <Link
          to="/admin/slots"
          className="px-4 py-2 rounded-lg text-xs font-mono tracking-widest uppercase
                     bg-white/5 border border-white/10 text-white/40 hover:text-white/70 transition-all"
        >
          View Slots
        </Link>
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-16 border border-white/8 rounded-xl">
          <p className="text-white/20 font-mono text-sm">No active sessions</p>
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
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#e8ff47] text-[#0f0f0f] font-bold">
                      ACTIVE
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 text-white/30">
                      {session.parking_type}
                    </span>
                    {session.user_id === null && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 text-white/30">
                        WALK-IN
                      </span>
                    )}
                  </div>
                  <p className="text-white/30 text-xs font-mono">
                    {session.vehicle_type} · Slot #{session.slot_id}
                    {session.user_id !== null && ` · User #${session.user_id}`}
                  </p>
                </div>
                <span className="text-white/20 font-mono text-xs">#{session.id}</span>
              </div>

              {/* Time info */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <p className="text-white/20 text-[10px] font-mono uppercase tracking-widest mb-1">Entry</p>
                  <p className="text-white/60 text-xs font-mono">{formatTime(session.entry_time)}</p>
                </div>
                {session.expected_exit_time && (
                  <div>
                    <p className="text-white/20 text-[10px] font-mono uppercase tracking-widest mb-1">Expected Exit</p>
                    <p className="text-white/60 text-xs font-mono">{formatTime(session.expected_exit_time)}</p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => navigate(`/ticket/${session.id}`)}
                  className="text-xs font-mono tracking-widest uppercase px-4 py-2 rounded-lg
                             bg-white/5 border border-white/10 text-white/40
                             hover:border-white/20 hover:text-white/70 transition-all"
                >
                  View Ticket
                </button>
                <button
                  onClick={() => handleExit(session.id)}
                  disabled={exiting === session.id}
                  className="text-xs font-mono tracking-widest uppercase px-4 py-2 rounded-lg
                             bg-[#e8ff47] text-[#0f0f0f] font-bold
                             hover:bg-[#d4eb3a] active:scale-[0.98]
                             disabled:opacity-50 disabled:cursor-not-allowed
                             transition-all duration-150"
                >
                  {exiting === session.id ? 'Exiting...' : 'Force Exit'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}