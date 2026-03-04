import { useEffect, useRef } from "react";
import { animate } from "framer-motion";

type AnimatedValueProps = {
  value: number;
  suffix?: string;
  decimals?: number;
  className?: string;
};

export default function AnimatedValue({ value, suffix, decimals = 0, className }: AnimatedValueProps) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const controls = animate(0, value, {
      duration: 1,
      ease: "easeOut",
      onUpdate(latest) {
        if (ref.current) {
          ref.current.textContent = `${latest.toFixed(decimals)}${suffix ?? ""}`;
        }
      },
    });
    return () => controls.stop();
  }, [value, suffix, decimals]);

  return <span ref={ref} className={className} />;
}
