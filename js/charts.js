// Gráficos próprios em SVG inline, no estilo do deck. Tarefa = magnitude,
// então barras de UMA cor (turquesa), com rótulos diretos. Sem dependências.
import { esc } from "./kit.js";

const TURQ = "var(--apm-turquoise)";
const INK = "var(--apm-fg-2)";
const MUTED = "var(--apm-muted)";

/**
 * Barras horizontais de uma cor. rows = [{label, value, note?}].
 * Escala pela maior magnitude; rótulo de valor no fim da barra (direto).
 */
export function BarChart({ rows, max, unit = "", barH = 46, gap = 20, labelW = 300, valueFmt = v => v }) {
  const m = max || Math.max(...rows.map(r => r.value));
  const padR = 90, top = 8;
  const plotW = 1000 - labelW - padR;
  const H = top + rows.length * (barH + gap);
  const bars = rows.map((r, i) => {
    const y = top + i * (barH + gap);
    const w = Math.max(6, (r.value / m) * plotW);
    const x = labelW;
    return `
      <text x="${labelW - 16}" y="${y + barH / 2}" text-anchor="end" dominant-baseline="central"
            font-size="22" font-weight="600" fill="${INK}">${esc(r.label)}</text>
      ${r.note ? `<text x="${labelW - 16}" y="${y + barH / 2 + 24}" text-anchor="end" dominant-baseline="central" font-size="15" fill="${MUTED}">${esc(r.note)}</text>` : ""}
      <rect x="${x}" y="${y}" width="${w}" height="${barH}" rx="8" fill="${TURQ}"/>
      <text x="${x + w + 14}" y="${y + barH / 2}" dominant-baseline="central"
            font-size="24" font-weight="700" fill="${INK}" style="font-variant-numeric:tabular-nums">${valueFmt(r.value)}${unit}</text>`;
  }).join("");
  return `<svg viewBox="0 0 1000 ${H}" width="100%" role="img" preserveAspectRatio="xMidYMid meet"
    aria-label="Gráfico de barras">
      <line x1="${labelW}" y1="${top}" x2="${labelW}" y2="${H - gap + 8}" stroke="var(--apm-border)" stroke-width="2"/>
      ${bars}
    </svg>`;
}

/** Distribuição STRIDE (contagem por categoria). */
export function StrideChart() {
  return BarChart({
    labelW: 360, barH: 40, gap: 18,
    rows: [
      { label: "I · Information Disclosure", value: 5 },
      { label: "S · Spoofing", value: 4 },
      { label: "T · Tampering", value: 4 },
      { label: "R · Repudiation", value: 4 },
      { label: "D · Denial of Service", value: 4 },
      { label: "E · Elevation of Privilege", value: 4 },
    ],
    max: 6, unit: "",
  });
}

/** Top 10 por média DREAD. */
export function DreadChart() {
  return BarChart({
    labelW: 300, barH: 40, gap: 14,
    valueFmt: v => v.toFixed(1).replace(".", ","),
    rows: [
      { label: "T-FX1-02", note: "Injeção SQL no login", value: 9.8 },
      { label: "T-FX2-06", note: "Papel no cadastro", value: 9.0 },
      { label: "T-FX2-01", note: "Resposta previsível", value: 8.8 },
      { label: "T-FX1-04", note: "Hash no JWT", value: 8.6 },
      { label: "T-FX4-04", note: "Consulta de usuários", value: 8.6 },
      { label: "T-FX3-06", note: "Cesta de outro titular", value: 8.4 },
      { label: "T-FX1-06", note: "Chave distribuída", value: 8.4 },
      { label: "T-FX4-06", note: "Exclusão de feedback", value: 8.2 },
      { label: "T-FX1-01", note: "Força bruta", value: 8.0 },
      { label: "T-FX3-02", note: "Checkout alheio", value: 7.8 },
    ],
    max: 10,
  });
}
