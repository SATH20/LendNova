import AnimatedValue from "./AnimatedValue";

type StatCardProps = {
  label: string;
  value: number | string;
  animated?: boolean;
  suffix?: string;
  decimals?: number;
};

export default function StatCard({ label, value, animated, suffix, decimals }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-[10px] uppercase tracking-[0.25em] text-muted">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-white">
        {animated && typeof value === "number" ? (
          <AnimatedValue value={value} suffix={suffix} decimals={decimals} className="text-3xl font-semibold text-white" />
        ) : (
          value
        )}
      </p>
    </div>
  );
}
