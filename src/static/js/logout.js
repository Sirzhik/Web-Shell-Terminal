document.addEventListener('click', (e) => {

  const logout = e.target;

  if (!logout) return;
  if (!logout.dataset.logouton) return;

  fetch(logout.dataset.logouton, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      window.location.replace("/");
    });
});
