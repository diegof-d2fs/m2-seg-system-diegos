// Validação das invariantes. Roda com ?check na URL. Escreve no console.
import { SLIDES } from "./slides/index.js";
import { SECTION_LABELS, JOURNEY, SHORT_ROUTE_HIDDEN } from "./meta.js";

(function check() {
  const errors = [];

  // primeiro slide de cada seção
  const firstOf = {};
  let prev = null;
  for (const s of SLIDES) {
    if (s.section !== prev) { firstOf[s.section] = s.id; prev = s.section; }
    if (!SECTION_LABELS[s.section]) errors.push(`Seção "${s.section}" (slide ${s.id}) não existe em SECTION_LABELS.`);
  }

  for (const j of JOURNEY) {
    const target = SLIDES[j.target - 1];
    if (!target) { errors.push(`JOURNEY target ${j.target} não existe.`); continue; }
    if (firstOf[target.section] !== j.target)
      errors.push(`JOURNEY "${j.label}" aponta para ${j.target}, que não é o primeiro slide da seção "${target.section}".`);
    if (SECTION_LABELS[target.section] !== j.label)
      errors.push(`JOURNEY "${j.label}" não bate com SECTION_LABELS["${target.section}"] = "${SECTION_LABELS[target.section]}".`);
  }

  for (const n of SHORT_ROUTE_HIDDEN)
    if (!SLIDES[n - 1]) errors.push(`SHORT_ROUTE_HIDDEN contém ${n}, que não existe.`);

  if (errors.length) { console.error("check FALHOU:"); errors.forEach(e => console.error(" - " + e)); }
  else console.info("check OK");
})();
