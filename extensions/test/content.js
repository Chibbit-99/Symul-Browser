// Symul's host shortcut handler routes Ctrl+T here when the browser chrome
// has focus; this listener also handles the shortcut when a page receives it.
document.addEventListener("keydown", (event) => {
  if (event.ctrlKey && !event.shiftKey && !event.altKey && !event.metaKey && event.key.toLowerCase() === "t") {
    event.preventDefault();
    alert("Ctrl+T was pressed!");
  }
}, true);
