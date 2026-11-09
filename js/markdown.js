// Renderizador mínimo de Markdown, sem dependências. Escapa HTML ANTES das marcações.
const escHtml = s => s.replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function inline(text) {
  let t = escHtml(text);
  t = t.replace(/`([^`]+)`/g, (_, c) => `<code class="cola-code">${c}</code>`);
  t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, url) => {
    if (/^(https?:|#|\.|\/)/.test(url)) return `<a href="${url}" target="_blank" rel="noopener">${label}</a>`;
    return label;
  });
  return t;
}

export function renderMarkdown(md) {
  const lines = String(md).replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let para = [];
  let list = null; // { tag, items }

  const flushPara = () => { if (para.length) { out.push(`<p>${inline(para.join(" "))}</p>`); para = []; } };
  const flushList = () => { if (list) { out.push(`<${list.tag}>${list.items.map(i => `<li>${inline(i)}</li>`).join("")}</${list.tag}>`); list = null; } };
  const flushAll = () => { flushPara(); flushList(); };

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line.trim()) { flushAll(); continue; }
    if (/^---+$/.test(line.trim())) { flushAll(); continue; }

    let m;
    if ((m = line.match(/^####\s+(.+)$/)) || (m = line.match(/^###\s+(.+)$/))) {
      flushAll(); out.push(`<h4>${inline(m[1])}</h4>`); continue;
    }
    if ((m = line.match(/^\s*[-*]\s+(.+)$/))) {
      flushPara();
      if (!list || list.tag !== "ul") { flushList(); list = { tag: "ul", items: [] }; }
      list.items.push(m[1]); continue;
    }
    if ((m = line.match(/^\s*\d+\.\s+(.+)$/))) {
      flushPara();
      if (!list || list.tag !== "ol") { flushList(); list = { tag: "ol", items: [] }; }
      list.items.push(m[1]); continue;
    }
    flushList();
    para.push(line.trim());
  }
  flushAll();
  return out.join("\n");
}
