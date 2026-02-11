document.addEventListener("submit", async (e) => {
  const form = e.target;

  if (!(form instanceof HTMLFormElement)) return;
  if (!form.dataset.endpoint) return;

  if (!form.checkValidity()) {
    e.preventDefault();
    form.reportValidity();
    return;
  }

  e.preventDefault();

  const data = {};

  new FormData(form).forEach((value, key) => {
    data[key] = value;
  });

  await fetch(form.dataset.endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);

      const endpointMap = {
        "/admin/add_user": "users",
        "/admin/add_group": "groups",
        "/admin/add_virtual_user": "servers",
      };

      const listType = endpointMap[form.dataset.endpoint];
      if (!listType) return;

      document.dispatchEvent(
        new CustomEvent("admin:list:update", {
          detail: { type: listType },
        }),
      );
    });

  if (form.dataset.type) {
    if (form.dataset.type == "auth") {
      window.location.replace("/term");
    }
    if (form.dataset.type == "passkey") {
      window.location.replace("/admin/panel");
    }
  }
});
