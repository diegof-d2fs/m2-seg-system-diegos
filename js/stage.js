// Palco 1920x1080 que escala proporcionalmente para caber no pai (letterbox).
export function mountStage(viewport, stage) {
  const fit = () => {
    const s = Math.min(viewport.clientWidth / 1920, viewport.clientHeight / 1080);
    stage.style.setProperty("--scale", Number.isFinite(s) && s > 0 ? s : 1);
  };
  new ResizeObserver(fit).observe(viewport);
  window.addEventListener("resize", fit);
  fit();
}
