document.addEventListener("keydown", (event) => {
  if (event.ctrlKey && !event.altKey && !event.metaKey && event.key.toLowerCase() === "t") {
    alert("Ctrl+T was pressed!");
  }
}, true);
