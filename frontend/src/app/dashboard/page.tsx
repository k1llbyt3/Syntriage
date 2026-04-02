"use client";
import { useEffect, useState } from "react";
import { Users, Calendar, Activity, ArrowLeft, MoreVertical, Search, Filter } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function Dashboard() {
  const [patients, setPatients] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/patients")
      .then(res => res.json())
      .then(data => setPatients(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="min-h-screen mesh-gradient p-4 md:p-12 text-foreground font-sans">
      <div className="max-w-7xl mx-auto">
        
        {/* Top Header */}
        <header className="flex flex-col md:flex-row items-start md:items-center justify-between mb-12 gap-6">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Link href="/" className="flex items-center gap-2 text-primary-teal-light mb-4 hover:gap-3 transition-all">
              <ArrowLeft className="w-4 h-4" /> <span className="text-xs font-bold uppercase tracking-widest">Return to Clinical Coordinator</span>
            </Link>
            <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white mb-2">Physician Hub</h1>
            <p className="text-white/40 font-medium italic">High-precision patient management system</p>
          </motion.div>
          
          <div className="flex flex-wrap gap-4">
            <StatCard icon={<Users />} label="Active Patients" value={patients.length} color="teal" />
            <StatCard icon={<Calendar />} label="Today's Caseload" value="4" color="coral" />
          </div>
        </header>

        {/* Action Bar */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
            <input 
              type="text" 
              placeholder="Search registry..." 
              className="w-full glass-input py-4 pl-12 pr-4 text-sm"
            />
          </div>
          <button className="glass-card px-6 py-4 flex items-center gap-2 hover:bg-white/10">
            <Filter className="w-4 h-4" /> <span className="text-sm font-bold uppercase tracking-tighter">Filter</span>
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
                  <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Patient Profile</th>
                  <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Digital ID</th>
                  <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Clinical Status</th>
                  <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Encounters</th>
                  <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-white/40">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {patients.map((p, i) => (
                  <motion.tr 
                    key={p.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.1 }}
                    className="hover:bg-primary-teal/5 transition-colors group"
                  >
                    <td className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary-teal to-primary-teal-light flex items-center justify-center font-black text-white text-xs">
                          {p.name.charAt(0)}
                        </div>
                        <span className="font-bold text-white group-hover:text-primary-teal-light transition-colors">{p.name}</span>
                      </div>
                    </td>
                    <td className="p-6 font-mono text-xs text-white/30">{p.email}</td>
                    <td className="p-6">
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-success animate-pulse" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-emerald-success bg-emerald-success/10 px-2 py-1 rounded">Stabilized</span>
                      </div>
                    </td>
                    <td className="p-6">
                      <div className="flex items-center gap-2 text-white/60">
                        <Activity className="w-3 h-3" />
                        <span className="text-xs font-bold">{p.appointments} Registered</span>
                      </div>
                    </td>
                    <td className="p-6">
                      <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <MoreVertical className="w-4 h-4 text-white/40" />
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
            {patients.length === 0 && (
              <div className="p-20 text-center">
                <div className="inline-block p-6 glass-card mb-4">
                  <Users className="w-10 h-10 text-white/10" />
                </div>
                <p className="text-white/20 font-bold uppercase tracking-widest text-xs">Registry Empty</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
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
        <p className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em] mb-1">{label}</p>
        <p className="text-3xl font-black text-white tracking-tighter">{value}</p>
      </div>
      {/* Decorative Blur */}
      <div className={`absolute -right-4 -bottom-4 w-24 h-24 blur-3xl opacity-20 ${isCoral ? 'bg-vibrant-coral' : 'bg-primary-teal'}`} />
    </div>
  );
}
