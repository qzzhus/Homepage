document.addEventListener("DOMContentLoaded", () => {
  const content = document.querySelector(".post-content");
  if (!content || typeof renderMathInElement !== "function") return;
  renderMathInElement(content, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false },
    ],
    preProcess: source => source.replace(/\\dd\[([^\]]+)\]/g, "\\mathop{}\\!\\mathrm{d}^{$1}"),
    macros: {
      "\\dd": "\\mathop{}\\!\\mathrm{d}",
      "\\ketbra": "\\lvert #1\\rangle\\langle #2\\rvert",
    },
    throwOnError: false,
  });
});
