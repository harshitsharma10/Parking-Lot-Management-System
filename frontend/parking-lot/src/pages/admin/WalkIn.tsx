import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import type { ParkingSlot, WalkInRequest } from '../../types'

const VEHICLE_TYPES = ['CAR', 'BIKE', 'TRUCK'] as const

export default function WalkIn() {
  const [form, setForm] = useState<WalkInRequest>({
    vehicle_number: '',
    vehicle_type: 'CAR',
    slot_id: undefined,
  })
  const [slots, setSlots] = useState<ParkingSlot[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchSlots = async () => {
      try {
        const res = await api.get('/admin/slots')
        const available = res.data.filter(
          (s: ParkingSlot) => s.slot_type === 'DYNAMIC' && s.status === 'AVAILABLE'
        )
        setSlots(available)
      } catch {
      }
    }
    fetchSlots()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload: WalkInRequest = {
        vehicle_number: form.vehicle_number.toUpperCase(),
        vehicle_type: form.vehicle_type,
      }
      if (form.slot_id) payload.slot_id = form.slot_id

      const res = await api.post('/admin/parking/walk-in', payload)
      navigate(`/ticket/${res.data.session_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto py-12 px-4">

      <div className="mb-10">
        <Link
          to="/admin/slots"
          className="text-white hover:text-white/50 font-mono text-xs tracking-widest uppercase transition-colors"
        >
          ← Slot Manager
        </Link>
        <p className="text-white font-mono text-xs tracking-widest uppercase mt-6 mb-3">
          Admin · Dynamic pool
        </p>
        <h1 className="text-white text-4xl font-light">Walk-in Entry</h1>
        <div className="w-12 h-px bg-[#e8ff47] mt-4" />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        <div>
          <label className="block text-white text-xs font-mono tracking-widest uppercase mb-2">
            Vehicle Number
          </label>
          <input
            type="text"
            value={form.vehicle_number}
            onChange={e => setForm(f => ({ ...f, vehicle_number: e.target.value.toUpperCase() }))}
            required
            className="w-full bg-white/5 border border-white/10 text-white text-sm px-4 py-3
                       rounded-lg focus:outline-none focus:border-[#e8ff47]/60
                       placeholder:text-white/20 transition-colors font-mono tracking-widest uppercase"
            placeholder="TN01AB1234"
          />
        </div>

        <div>
          <label className="block text-white text-xs font-mono tracking-widest uppercase mb-3">
            Vehicle Type
          </label>
          <div className="grid grid-cols-3 gap-2">
            {VEHICLE_TYPES.map(type => (
              <button
                key={type}
                type="button"
                onClick={() => setForm(f => ({ ...f, vehicle_type: type }))}
                className={`py-3 rounded-lg text-xs font-mono tracking-widest uppercase transition-all
                  ${form.vehicle_type === type
                    ? 'bg-[#e8ff47] text-[#0f0f0f] font-bold'
                    : 'bg-white/5 border border-white/10 text-white hover:border-white/20 hover:text-white/70'
                  }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-white text-xs font-mono tracking-widest uppercase mb-2">
            Specific Slot
            <span className="text-white ml-2 normal-case tracking-normal">(optional — auto-assigns if empty)</span>
          </label>
          <select
            value={form.slot_id ?? ''}
            onChange={e => setForm(f => ({
              ...f,
              slot_id: e.target.value ? Number(e.target.value) : undefined
            }))}
            className="w-full bg-white/5 border border-white/10 text-white text-sm px-4 py-3
                       rounded-lg focus:outline-none focus:border-[#e8ff47]/60
                       transition-colors font-mono scheme-dark"
          >
            <option value="">Auto-assign</option>
            {slots.map(slot => (
              <option key={slot.id} value={slot.id}>
                {slot.slot_number} — Floor {slot.floor}
              </option>
            ))}
          </select>
          {slots.length === 0 && (
            <p className="text-white text-xs font-mono mt-2">
              No dynamic slots available right now
            </p>
          )}
        </div>

        <div className="flex gap-3 bg-white/3 border border-white/8 rounded-lg px-4 py-3">
          <span className="w-1 h-1 bg-[#e8ff47] rounded-full mt-1.5 shrink-0" />
          <p className="text-white text-xs font-mono leading-relaxed">
            Walk-in vehicles are assigned to the dynamic pool. No user account required. Slot is marked occupied immediately.
          </p>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-red-400 text-xs font-mono
                          bg-red-400/10 px-4 py-3 rounded-lg border border-red-400/20">
            <span className="w-1 h-1 bg-red-400 rounded-full shrink-0" />
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || slots.length === 0}
          className="w-full bg-[#e8ff47] text-[#0f0f0f] text-sm font-mono font-bold
                     tracking-widest uppercase py-3 rounded-lg
                     hover:bg-[#d4eb3a] active:scale-[0.98]
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-150"
        >
          {loading ? 'Registering...' : 'Register Walk-in →'}
        </button>

      </form>
    </div>
  )
}