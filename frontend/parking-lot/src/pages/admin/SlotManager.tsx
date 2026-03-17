import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/axios";
import type { ParkingSlot } from "../../types";

export default function SlotManager() {
  const [slots, setSlots] = useState<ParkingSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"ALL" | "QUEUE" | "DYNAMIC">("ALL");

  const fetchSlots = async () => {
    try {
      const res = await api.get("/admin/slots");
      setSlots(res.data);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSlots();

    const interval = setInterval(fetchSlots, 30000);
    return () => clearInterval(interval);
  }, []);

  const filtered = slots.filter(
    (s) => filter === "ALL" || s.slot_type === filter,
  );
  const occupied = slots.filter((s) => s.status === "OCCUPIED").length;
  const available = slots.filter((s) => s.status === "AVAILABLE").length;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <span className="text-white font-mono text-sm tracking-widest uppercase">
          Loading...
        </span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <div className="mb-10">
        <p className="text-white font-mono text-xs tracking-widest uppercase mb-3">
          Admin
        </p>
        <h1 className="text-white text-4xl font-light">Slot Manager</h1>
        <div className="w-12 h-px bg-[#e8ff47] mt-4" />
      </div>

      <div className="grid grid-cols-3 gap-3 mb-8">
        {[
          { label: "Total", value: slots.length },
          { label: "Available", value: available, accent: true },
          { label: "Occupied", value: occupied },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white/3 border border-white/8 rounded-xl p-4"
          >
            <p className="text-white font-mono text-xs tracking-widest uppercase mb-2">
              {stat.label}
            </p>
            <p
              className={`text-3xl font-light ${stat.accent ? "text-[#e8ff47]" : "text-white"}`}
            >
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      <div className="flex gap-2 mb-6">
        {(["ALL", "QUEUE", "DYNAMIC"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-xs font-mono tracking-widest uppercase transition-all
              ${
                filter === f
                  ? "bg-[#e8ff47] text-[#0f0f0f] font-bold"
                  : "bg-white/5 border border-white/10 text-white hover:text-white/70"
              }`}
          >
            {f}
          </button>
        ))}
        <button
          onClick={fetchSlots}
          className="ml-auto px-4 py-2 rounded-lg text-xs font-mono tracking-widest uppercase
                     bg-white/5 border border-white/10 text-white hover:text-white/70 transition-all"
        >
          ↻ Refresh
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {filtered.map((slot) => (
          <div
            key={slot.id}
            className={`rounded-xl p-4 border transition-all
              ${
                slot.status === "OCCUPIED"
                  ? "bg-[#e8ff47]/5 border-[#e8ff47]/20"
                  : "bg-white/3 border-white/8"
              }`}
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-white font-mono text-sm tracking-widest">
                {slot.slot_number}
              </span>
              <span
                className={`w-2 h-2 rounded-full mt-1 shrink-0
                ${slot.status === "OCCUPIED" ? "bg-[#e8ff47]" : "bg-white/20"}`}
              />
            </div>
            <p className="text-white text-[10px] font-mono uppercase tracking-widest mb-1">
              {slot.slot_type}
            </p>
            <p className="text-white text-[10px] font-mono">
              Floor {slot.floor}
              {slot.lane !== null && ` · L${slot.lane}P${slot.position}`}
            </p>
            <p
              className={`text-[10px] font-mono mt-2 uppercase tracking-widest
              ${slot.status === "OCCUPIED" ? "text-[#e8ff47]" : "text-white"}`}
            >
              {slot.status}
            </p>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mt-8">
        <Link
          to="/admin/walk-in"
          className="text-xs font-mono tracking-widest uppercase px-4 py-2 rounded-lg
                     bg-[#e8ff47] text-[#0f0f0f] font-bold hover:bg-[#d4eb3a] transition-all"
        >
          Register Walk-in →
        </Link>
        <Link
          to="/admin/sessions"
          className="text-xs font-mono tracking-widest uppercase px-4 py-2 rounded-lg
                     bg-white/5 border border-white/10 text-white hover:text-white/70 transition-all"
        >
          View Sessions
        </Link>
      </div>
    </div>
  );
}
