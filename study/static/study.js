document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-theme-toggle]");
  toggle?.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("study-theme", next);
  });

  const article = document.querySelector(".markdown");
  const highlightButton = document.querySelector("#highlight-selection");
  let highlight = null;

  document.addEventListener("selectionchange", () => {
    const selection = window.getSelection();
    if (!article || !highlightButton || !selection?.rangeCount) return;
    const range = selection.getRangeAt(0);
    const quote = selection.toString().trim();
    if (!quote || !article.contains(range.commonAncestorContainer)) {
      highlight = null;
      highlightButton.disabled = true;
      return;
    }
    const before = range.cloneRange();
    before.selectNodeContents(article);
    before.setEnd(range.startContainer, range.startOffset);
    const after = range.cloneRange();
    after.selectNodeContents(article);
    after.setStart(range.endContainer, range.endOffset);
    highlight = {
      quote,
      prefix: before.toString().slice(-40),
      suffix: after.toString().slice(0, 40),
    };
    highlightButton.disabled = false;
  });

  highlightButton?.addEventListener("click", () => {
    if (!highlight) return;
    htmx.ajax("POST", `/a/${highlightButton.dataset.slug}/highlights`, {
      values: highlight,
      target: "#highlight-feedback",
      swap: "innerHTML",
    });
  });
});
