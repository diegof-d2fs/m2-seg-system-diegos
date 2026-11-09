// Metadados de navegação. NÃO importa slides/index.js (evita import circular).

/** Rótulos dos blocos. Slides consecutivos com a mesma `section` formam um bloco. */
export const SECTION_LABELS = {
  abertura: "Abertura",
  contexto: "Contexto e método",
  modelo: "Modelo e DFD",
  fluxos: "Análise dos fluxos",
  consolidacao: "Visão consolidada",
  validacao: "Validação",
  fecho: "Conclusão",
};

/** Itens do slide "O que veremos". target = número do primeiro slide do bloco. */
export const JOURNEY = [
  { label: "Contexto e método", sub: "Juice Shop, DFD, STRIDE, DREAD", accent: "turquoise", target: 3 },
  { label: "Modelo e DFD", sub: "Processos, dados e fronteiras de confiança", accent: "violet", target: 5 },
  { label: "Análise dos fluxos", sub: "FX1 a FX4, elemento por elemento", accent: "pink", target: 6 },
  { label: "Visão consolidada", sub: "Top 10 por DREAD e plano de mitigação", accent: "turquoise", target: 11 },
  { label: "Validação", sub: "Reprodução no laboratório e comparação com a M1", accent: "violet", target: 13 },
  { label: "Conclusão", sub: "Lições aprendidas e próximos passos", accent: "orange", target: 14 },
];

/** Slides ocultos na rota curta da cola (derivados dos opcionais em slides/index.js). */
export const SHORT_ROUTE_HIDDEN = [];
