"use client";

interface TimeSlotProps {
  time: string;
  onSelect: (time: string) => void;
  isSelected?: boolean;
}

export default function TimeSlot({ time, onSelect, isSelected }: TimeSlotProps) {
  return (
    <button
      onClick={() => onSelect(time)}
      className={`px-4 py-2 rounded-lg border transition-all text-sm font-medium ${
        isSelected
          ? "bg-primary-teal border-primary-teal text-white"
          : "glass-card border-white/10 hover:border-primary-teal/50 hover:bg-white/5"
      }`}
    >
      {time}
    </button>
  );
}
