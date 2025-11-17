import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function CategoryPieChart({ categories }) {
  if (!categories || Object.keys(categories).length === 0) {
    return <p>No category data available for visualization.</p>;
  }

  // Convert categories -> list for Recharts
  const pieData = Object.entries(categories).map(([key, val]) => ({
    name: key.replace("_", " "),
    // Slice size = absolute sentiment strength × count
    value: Math.abs(val.score) * (val.count || 1),
    sentiment: val.score,
  }));

  // Distinct color palette for different categories
  const COLOR_PALETTE = [
    "#4CAF50",
    "#2196F3",
    "#FF9800",
    "#9C27B0",
    "#00BCD4",
    "#E91E63",
    "#8BC34A",
    "#FFC107",
    "#F44336",
    "#795548",
  ];

  // Assign unique colors for each category (wrap if more than palette)
  const COLORS = pieData.map(
    (_, idx) => COLOR_PALETTE[idx % COLOR_PALETTE.length]
  );

  return (
    <div style={{ width: "100%", height: 400, marginTop: "2rem" }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            outerRadius={150}
            dataKey="value"
            labelLine={false}
            label={({ name, sentiment }) =>
              `${name}: ${sentiment > 0 ? "+" : ""}${sentiment.toFixed(2)}`
            }
            isAnimationActive={true}
            animationDuration={1400}
          >
            {pieData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index]}
                opacity={0.9}
                stroke="#fff"
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, name, props) => [
              `Score: ${props.payload.sentiment.toFixed(3)}`,
              props.payload.name,
            ]}
          />
          <Legend
            payload={pieData.map((entry, index) => ({
              id: entry.name,
              type: "circle",
              value: `${entry.name} (${entry.sentiment.toFixed(2)})`,
              color: COLORS[index],
            }))}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
