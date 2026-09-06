const FIELDS = [
  { key: "study_hours_delta", label: "Study Hours / day", min: -4, max: 4, step: 0.5 },
  { key: "sleep_hours_delta", label: "Sleep Hours / day", min: -3, max: 3, step: 0.5 },
  { key: "screen_time_delta", label: "Screen Time / day", min: -4, max: 4, step: 0.5 },
  { key: "fitness_minutes_delta", label: "Fitness (min/day)", min: -60, max: 60, step: 5 },
  { key: "consistency_delta", label: "Consistency", min: -30, max: 30, step: 2 },
];

export default function AdjustmentSliders({ value, onChange }) {
  return (
    <div className="flex flex-col gap-4">
      {FIELDS.map(({ key, label, min, max, step }) => (
        <div key={key}>
          <div className="mb-1 flex justify-between text-xs text-white/50">
            <span>{label}</span>
            <span className="text-cyan-300">{value[key] > 0 ? `+${value[key]}` : value[key]}</span>
          </div>
          <input
            type="range"
            min={min}
            max={max}
            step={step}
            value={value[key]}
            onChange={(e) => onChange({ ...value, [key]: Number(e.target.value) })}
            className="w-full accent-cyan-400"
          />
        </div>
      ))}
    </div>
  );
}

export const EMPTY_ADJUSTMENTS = {
  study_hours_delta: 0,
  sleep_hours_delta: 0,
  screen_time_delta: 0,
  fitness_minutes_delta: 0,
  consistency_delta: 0,
};
