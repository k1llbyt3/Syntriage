"use client";
import { useEffect, useState } from "react";
import { 
  Users, 
  Calendar, 
  Activity, 
  ArrowLeft, 
  MoreVertical, 
  Search, 
  Filter, 
  Clock, 
  Clipboard,
  Trash2,
  X,
  User as UserIcon,
  ChevronRight
} from "lucide-react";
import Link from "next/link";
import NextImage from "next/image";
import { motion, AnimatePresence } from "framer-motion";

export default function Dashboard() {
  const [patients, setPatients] = useState<any[]>([]);
  const [debatedCases, setDebatedCases] = useState<any[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [patientDetail, setPatientDetail] = useState<any>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE = "http://127.0.0.1:8000/api";

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [patientsRes, casesRes] = await Promise.all([
          fetch(`${API_BASE}/patients`),
          fetch(`${API_BASE}/debated-cases`)
        ]);

        if (!patientsRes.ok || !casesRes.ok) {
          throw new Error("Failed to fetch initial dashboard data");
        }

        const [patientsData, casesData] = await Promise.all([
          patientsRes.json(),
          casesRes.json()
        ]);

        setPatients(Array.isArray(patientsData) ? patientsData : []);
        setDebatedCases(Array.isArray(casesData) ? casesData : []);
      } catch (err) {
        console.error("Dashboard Load Error:", err);
        setError("Unable to connect to the clinical server. Please ensure the backend is running at :8000");
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const handleOverride = async (noteId: number, currentUrgency: string) => {
    const doctorName = "Dr. Masterpiece"; // Mock doctor name
    const newUrgency = currentUrgency === "High" ? "Low" : "High"; // Toggle for demo
    try {
      const res = await fetch(`${API_BASE}/override-note/${noteId}?new_urgency=${newUrgency}&doctor_name=${doctorName}`, {
        method: 'POST'
      });
      if (res.ok) {
        // Refresh debated cases
        const updatedRes = await fetch(`${API_BASE}/debated-cases`);
        if (updatedRes.ok) {
          const updated = await updatedRes.json();
          setDebatedCases(updated);
        }
      }
    } catch (err) {
      console.error(err);
      setError("Failed to perform override operation.");
    }
  };

  const handleDeletePatient = async (id: number, name: string) => {
    if (!window.confirm(`Are you sure you want to PERMANENTLY remove clinical records for ${name}? This action cannot be undone.`)) {
      return;
    }
    
    try {
      const res = await fetch(`${API_BASE}/patients/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setPatients(patients.filter(p => p.id !== id));
        // Clear detail if it was the deleted patient
        if (selectedPatientId === id) setSelectedPatientId(null);
      } else {
        const errorData = await res.json().catch(() => ({ detail: "Unknown server error" }));
        console.error("Deletion failed:", errorData);
        throw new Error(errorData.detail || "Deletion failed on server");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Could not delete the patient record.");
    }
  };

  const fetchPatientDetail = async (id: number) => {
    setLoadingDetail(true);
    setSelectedPatientId(id);
    try {
      const res = await fetch(`${API_BASE}/patients/${id}`);
      if (!res.ok) throw new Error("Patient not found");
      const data = await res.json();
      setPatientDetail(data);
    } catch (err) {
      console.error(err);
      setError("Could not retrieve patient details.");
    } finally {
      setLoadingDetail(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 p-4 md:p-12 text-foreground font-sans relative overflow-hidden">
      {/* MOLECULAR BACKGROUND IMAGE LAYER (WARM SYNC) */}
      <div 
        className="absolute inset-0 z-0 opacity-30 pointer-events-none transition-opacity duration-1000 bg-[position:center_calc(50%+4px)] bg-no-repeat bg-[size:64%] blur-[3.5px]"
        style={{ 
          backgroundImage: 'url("/warm.png")'
        }} 
      />

      {/* ATMOSPHERE ORBS (Warm Amber Balance) */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-amber-950/10 blur-[120px] rounded-full pointer-events-none z-10 opacity-70" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-orange-950/5 blur-[150px] rounded-full pointer-events-none z-10 opacity-40" />

      <div className="max-w-7xl mx-auto relative z-30">
        
        {/* Top Header */}
        <header className="flex flex-col md:flex-row items-start md:items-center justify-between mb-12 gap-8">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex flex-col md:flex-row md:items-center gap-4 md:gap-8"
          >
            <Link href="/" className="group flex items-center gap-6 text-primary-teal-light hover:text-white transition-all shrink-0">
              <NextImage src="/logo.png" alt="Logo" width={80} height={80} className="object-contain" />
              <span className="text-3xl font-black italic tracking-[0.2em] text-white">SYNTRIAGE</span>
            </Link>
            
            <div className="hidden md:block w-px h-8 bg-white/10" />
            
            <div>
              <h1 className="text-4xl font-black italic tracking-tight text-white mb-1 uppercase">Physician Hub</h1>
              <p className="text-[10px] uppercase font-black tracking-[0.4em] text-primary-teal-light">Syntriage Clinical Registry</p>
            </div>
          </motion.div>
          
          <div className="flex flex-wrap gap-4">
            <StatCard icon={<Users />} label="Active Patients" value={patients.length} color="teal" />
            <StatCard icon={<Calendar />} label="Debated Cases" value={debatedCases.length} color="coral" />
          </div>
        </header>

        {/* Connection Error Alert */}
        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-8 p-4 bg-vibrant-coral/10 border border-vibrant-coral/20 rounded-2xl flex items-center gap-4 text-vibrant-coral"
            >
              <Activity className="w-5 h-5 shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-bold">Clinical Server Connection Error</p>
                <p className="text-xs opacity-70 font-medium">{error}</p>
              </div>
              <button onClick={() => setError(null)} className="p-2 hover:bg-vibrant-coral/10 rounded-lg">
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {isLoading && !error && (
          <div className="flex items-center justify-center py-20 grayscale opacity-20">
            <div className="w-12 h-12 border-4 border-primary-teal border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Debated Cases Feed */}
        {debatedCases.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-vibrant-coral/10 rounded-lg">
                <Activity className="w-5 h-5 text-vibrant-coral" />
              </div>
              <h2 className="text-xl font-bold text-white">Clinical Consensus Feed</h2>
              <span className="px-2 py-0.5 bg-vibrant-coral/20 text-vibrant-coral text-[10px] font-bold uppercase tracking-widest rounded-full">Requires Review</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {debatedCases.map((c) => (
                <motion.div 
                  key={c.note_id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="glass-card p-6 border-l-4 border-vibrant-coral relative overflow-hidden"
                >
                  <div className="flex justify-between items-start mb-4 relative z-10">
                    <div>
                      <h3 className="font-bold text-white mb-1">{c.patient_name}</h3>
                      <p className="text-[10px] font-medium text-white/40 uppercase tracking-widest">Digital Note #{c.note_id}</p>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${c.urgency === 'High' ? 'bg-vibrant-coral/20 text-vibrant-coral' : 'bg-primary-teal/20 text-primary-teal-light'}`}>
                        {c.urgency} Urgency
                      </span>
                      {c.override_by && (
                        <span className="text-[8px] font-bold text-emerald-success mt-1 uppercase tracking-normal italic">Overridden by {c.override_by}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="bg-black/20 p-4 rounded-xl mb-4 relative z-10">
                    <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest mb-2 italic">Agent Debate Transcript</p>
                    <p className="text-xs text-white/60 leading-relaxed font-mono">
                      {c.transcript}
                    </p>
                  </div>

                  <div className="flex gap-3 relative z-10">
                    <button 
                      onClick={() => handleOverride(c.note_id, c.urgency)}
                      className="flex-1 bg-white/5 hover:bg-white/10 py-3 rounded-xl text-[10px] font-bold uppercase tracking-[0.2em] transition-all border border-white/5"
                    >
                      {c.override_by ? 'Modify Override' : 'Override Consensus'}
                    </button>
                    <button className="px-4 bg-primary-teal hover:bg-primary-teal-light text-white rounded-xl transition-all">
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                  </motion.div>
                  ))}
            </div>
          </section>
        )}

        {/* Action Bar */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1 relative glass-3d overflow-hidden group">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30 group-focus-within:text-primary-teal-light transition-colors" />
            <input 
              type="text" 
              placeholder="Search registry files..." 
              className="w-full bg-transparent py-5 pl-14 pr-4 text-sm outline-none text-white placeholder:text-white/20"
            />
          </div>
          <button className="glass-3d px-10 flex items-center gap-2 hover:bg-white/10 active:scale-95 transition-all cursor-pointer">
            <Filter className="w-4 h-4" /> <span className="text-sm font-bold uppercase tracking-normal">Filter</span>
          </button>
        </div>

        {/* Registry Table */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-container overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white/5 border-b border-white/5">
                  <th className="p-6 text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">Patient Profile</th>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">Patient ID</th>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">Digital ID</th>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">Status</th>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">Encounters</th>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-[0.2em] text-white/40">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {patients.map((p, i) => (
                  <motion.tr 
                    key={p.id}
                    onClick={() => fetchPatientDetail(p.id)}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className={`border-b border-white/5 hover:bg-white/[0.02] transition-colors group cursor-pointer ${selectedPatientId === p.id ? 'bg-white/5' : ''}`}
                  >
                    <td className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary-teal to-primary-teal-light flex items-center justify-center font-bold text-white text-xs">
                          {p.name.charAt(0)}
                        </div>
                        <span className="font-bold text-white group-hover:text-primary-teal-light transition-colors">{p.name}</span>
                      </div>
                    </td>
                    <td className="p-6 font-mono text-xs text-primary-teal-light font-bold">#{p.id}</td>
                    <td className="p-6 font-mono text-xs text-white/30">{p.email}</td>
                    <td className="p-6">
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-success animate-pulse" />
                        <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-success bg-emerald-success/10 px-2 py-1 rounded">Active</span>
                      </div>
                    </td>
                    <td className="p-6">
                      <div className="flex items-center gap-2 text-white/60">
                        <Activity className="w-3 h-3" />
                        <span className="text-xs font-bold">{p.appointments} Registered</span>
                      </div>
                    </td>
                    <td className="p-6">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeletePatient(p.id, p.name);
                        }}
                        className="p-2 hover:bg-vibrant-coral/10 text-white/20 hover:text-vibrant-coral rounded-lg transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>

      {/* DETAIL SIDE PANEL */}
      <AnimatePresence>
        {selectedPatientId && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-full md:w-[450px] bg-black/40 backdrop-blur-2xl border-l border-white/10 z-50 p-8 overflow-y-auto shadow-2xl shadow-black/50"
          >
            <div className="flex items-center justify-between mb-12">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center">
                  <UserIcon className="w-6 h-6 text-primary-teal-light" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white tracking-normal">Clinical Record</h2>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-white/20">Registry File #{selectedPatientId}</p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedPatientId(null)}
                className="p-3 hover:bg-white/5 rounded-xl transition-all cursor-pointer"
              >
                <X className="w-5 h-5 text-white/40" />
              </button>
            </div>

            {loadingDetail ? (
              <div className="space-y-6">
                <div className="h-24 glass-card animate-pulse" />
                <div className="h-64 glass-card animate-pulse" />
              </div>
            ) : patientDetail && (
              <div className="space-y-10">
                {/* Contact Section */}
                <section>
                  <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/20 mb-4 block">Personal Information</label>
                  <div className="glass-card p-6 space-y-4">
                    <div className="flex justify-between">
                      <span className="text-xs font-medium text-white/40">Full Name</span>
                      <span className="text-sm font-bold text-white">{patientDetail.first_name} {patientDetail.last_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs font-medium text-white/40">Email Address</span>
                      <span className="text-sm font-mono text-white/60">{patientDetail.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs font-medium text-white/40">Registry Entry</span>
                      <span className="text-sm font-bold text-white">{new Date(patientDetail.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </section>

                {/* Encounter Timeline */}
                <section>
                  <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/20 mb-4 block">Encounter Timeline</label>
                  <div className="space-y-4">
                    {patientDetail.appointments.length === 0 ? (
                      <p className="text-xs text-white/20 italic p-6 border border-dashed border-white/5 rounded-2xl text-center">No digital encounters registered yet.</p>
                    ) : patientDetail.appointments.map((apt: any) => (
                      <div key={apt.id} className="glass-card p-6 border-l-4 border-primary-teal">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-2">
                            <Clock className="w-3 h-3 text-primary-teal-light" />
                            <span className="text-xs font-bold text-white">{new Date(apt.time).toLocaleString()}</span>
                          </div>
                          <span className="text-[10px] font-bold uppercase tracking-widest text-primary-teal-light bg-primary-teal/10 px-2 py-1 rounded">{apt.status}</span>
                        </div>
                        <div className="flex items-start gap-3 p-4 bg-white/5 rounded-xl">
                          <Clipboard className="w-4 h-4 text-white/20 mt-1 shrink-0" />
                          <p className="text-xs text-white/60 leading-relaxed font-medium">
                            AI-generated encounter summary pending sync from clinical notes table.
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function StatCard({ icon, label, value, color }: any) {
  const isCoral = color === 'coral';
  return (
    <div className="glass-card p-6 flex items-center gap-6 min-w-[240px] relative overflow-hidden group">
      <div className={`p-4 ${isCoral ? 'bg-vibrant-coral/20 text-vibrant-coral' : 'bg-primary-teal/20 text-primary-teal-light'} rounded-2xl group-hover:scale-110 transition-transform`}>
        {icon}
      </div>
      <div className="relative z-10">
        <p className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mb-1">{label}</p>
        <p className="text-3xl font-bold text-white tracking-normal">{value}</p>
      </div>
    </div>
  );
}
