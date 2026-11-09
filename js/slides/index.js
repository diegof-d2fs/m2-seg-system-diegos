import capa from "./s01-capa.js";
import sumario from "./s02-sumario.js";
import contexto from "./s03-contexto.js";
import metodo from "./s04-metodo.js";
import dfd from "./s05-dfd.js";
import fluxos from "./s06-fluxos.js";
import fx1 from "./s07-fx1.js";
import fx2 from "./s08-fx2.js";
import fx3 from "./s09-fx3.js";
import fx4 from "./s10-fx4.js";
import top10 from "./s11-top10.js";
import mitigacao from "./s12-mitigacao.js";
import validacao from "./s13-validacao.js";
import conclusao from "./s14-conclusao.js";
import obrigado from "./s15-obrigado.js";

/** @typedef {{ id:number, title:string, render:() => string, section:string, optional?:boolean }} SlideDef */

const ORDER = [
  { title: "Capa", render: capa, section: "abertura" },
  { title: "O que veremos", render: sumario, section: "abertura" },
  { title: "Contexto do ambiente", render: contexto, section: "contexto" },
  { title: "Método: DFD, STRIDE e DREAD", render: metodo, section: "contexto" },
  { title: "Modelo do sistema e fronteiras", render: dfd, section: "modelo" },
  { title: "Os quatro fluxos", render: fluxos, section: "fluxos" },
  { title: "FX1 · Login e sessão", render: fx1, section: "fluxos" },
  { title: "FX2 · Cadastro e recuperação", render: fx2, section: "fluxos" },
  { title: "FX3 · Cesta, checkout e pedido", render: fx3, section: "fluxos" },
  { title: "FX4 · Administração e contabilidade", render: fx4, section: "fluxos" },
  { title: "Top 10 por DREAD", render: top10, section: "consolidacao" },
  { title: "Plano de mitigação", render: mitigacao, section: "consolidacao" },
  { title: "Validação no laboratório", render: validacao, section: "validacao" },
  { title: "Conclusão e lições", render: conclusao, section: "fecho" },
  { title: "Obrigado", render: obrigado, section: "fecho" },
];

/** @type {SlideDef[]} */
export const SLIDES = ORDER.map((s, i) => ({ ...s, id: i + 1 }));
