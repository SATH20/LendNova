"use client";

import { motion } from "framer-motion";

type Chip = {
  label: string;
  value: string;
};

type Props = {
  chips: Chip[];
  onSelect: (value: string) => void;
};

export default function QuickChips({ chips, onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {chips.map((chip, index) => (
        <motion.button
          key={chip.label}
          onClick={() => onSelect(chip.value)}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.04 }}
          className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted transition hover:border-white/30 hover:bg-white/10 hover:text-white"
        >
          {chip.label}
        </motion.button>
      ))}
    </div>
  );
}
