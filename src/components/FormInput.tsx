type FormInputProps = {
  label: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  min?: number;
  step?: number;
};

export default function FormInput({ label, type = "text", value, onChange, placeholder, min, step }: FormInputProps) {
  return (
    <div>
      <label className="text-xs uppercase tracking-[0.25em] text-muted">{label}</label>
      <input
        type={type}
        min={min}
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
      />
    </div>
  );
}
