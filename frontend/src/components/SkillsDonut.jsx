import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { useTheme } from "../context/ThemeContext";

export default function SkillsDonut({ foundCount, missingCount }) {
  const { theme } = useTheme();
  const total = foundCount + missingCount;
  const data = [
    { name: "Skills Found", value: foundCount, color: "var(--t-signal-500)" },
    { name: "Missing Skills", value: missingCount, color: "var(--t-rose-signal)" },
  ];

  if (total === 0) {
    return <p className="font-mono text-[12px] text-ink-500">No skill data available.</p>;
  }

  return (
    <div className="relative mx-auto h-44 w-44" key={theme}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius="68%"
            outerRadius="100%"
            paddingAngle={2}
            stroke="none"
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-2xl font-bold text-ink-100">
          {Math.round((foundCount / total) * 100)}%
        </span>
        <span className="font-mono text-[10px] uppercase tracking-wider text-ink-400">covered</span>
      </div>
    </div>
  );
}
