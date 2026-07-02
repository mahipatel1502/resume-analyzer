import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";
import { useTheme } from "../context/ThemeContext";

const toneByValue = (v) => {
  if (v >= 75) return "var(--t-signal-500)";
  if (v >= 50) return "var(--t-cyan-signal)";
  if (v >= 30) return "var(--t-amber-signal)";
  return "var(--t-rose-signal)";
};

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const { name, value } = payload[0].payload;
  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 px-3 py-2 shadow-lg">
      <p className="font-mono text-[11px] uppercase tracking-wider text-ink-300">{name}</p>
      <p className="font-mono text-sm font-semibold" style={{ color: toneByValue(value) }}>
        {value}/100
      </p>
    </div>
  );
}

export default function ScoreBreakdownChart({ breakdown }) {
  const { theme } = useTheme();

  const data = Object.entries(breakdown).map(([key, value]) => ({
    name: key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    value: Math.round(value),
  }));

  return (
    <div className="h-72 w-full" key={theme}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" horizontal={false} />
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fill: "var(--chart-tick)", fontSize: 11, fontFamily: "JetBrains Mono, monospace" }}
            axisLine={{ stroke: "var(--chart-grid)" }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={140}
            tick={{ fill: "var(--chart-label)", fontSize: 12, fontFamily: "Inter, sans-serif" }}
            axisLine={{ stroke: "var(--chart-grid)" }}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(128,128,128,0.06)" }} />
          <Bar dataKey="value" radius={[4, 4, 4, 4]} barSize={18}>
            {data.map((entry, index) => (
              <Cell key={index} fill={toneByValue(entry.value)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
