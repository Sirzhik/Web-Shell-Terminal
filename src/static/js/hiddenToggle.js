document.addEventListener("click", (e) => {
  const toggler = e.target.closest("[data-toggle]");
  if (!toggler) return;

  const targetId = toggler.dataset.toggle;
  const target = document.getElementById(targetId);
  if (!target) return;

  target.classList.toggle("hidden");
});
