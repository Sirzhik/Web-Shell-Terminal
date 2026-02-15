document.addEventListener("submit", async (e) => {
  const form = e.target;

  if (!(form instanceof HTMLFormElement)) return;
  if (!form.dataset.endpoint) return;

  if (form.dataset.loading === "true") return;

  if (!form.checkValidity()) {
    e.preventDefault();
    form.reportValidity();
    return;
  }

  e.preventDefault();
  form.dataset.loading = "true";

  const data = {};
  new FormData(form).forEach((value, key) => {
    data[key] = value;
  });

  let responseData;

  try {
    const res = await fetch(form.dataset.endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    responseData = await res.json();
  } catch (err) {
    console.error("Request failed:", err);
    form.dataset.loading = "false";
    return;
  }

  // ===== AUTH =====
  if (form.dataset.type === "auth") {
    if (responseData.message) {
      window.location.replace("/term");
      return;
    }

    if (responseData.detail) {
      renderError(responseData.detail);
      form.dataset.loading = "false";
      return;
    }
  }

  if (form.dataset.type === "passkey") {
    if (responseData.message) {
      window.location.replace("/admin/panel");
      return;
    }

    if (responseData.detail) {
      renderError(responseData.detail);
      form.dataset.loading = "false";
      return;
    }
  }

  // ===== ADMIN LIST UPDATE =====
  const endpointMap = {
    "/admin/add_user": "users",
    "/admin/add_group": "groups",
    "/admin/add_virtual_user": "servers",
  };

  const listType = endpointMap[form.dataset.endpoint];
  if (listType) {
    document.dispatchEvent(
      new CustomEvent("admin:list:update", {
        detail: { type: listType },
      }),
    );
  }

  form.dataset.loading = "false";
});

function renderError(msg) {
  const errbox = document.createElement("div");
  errbox.classList.add("errbox");
  errbox.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  `;

  const errmsg = document.createElement("b");
  errmsg.innerText = msg;

  const rightWrap = document.createElement("div");
  rightWrap.style.display = "flex";
  rightWrap.style.alignItems = "center";
  rightWrap.style.gap = "0.5rem";

  const counter = document.createElement("p");
  counter.style.opacity = "0.6";

  const delbtn = document.createElement("button");
  delbtn.classList.add("delete-btn");
  delbtn.innerText = "X";
  delbtn.style.cursor = "pointer";
  delbtn.style.scale = "115%";
  delbtn.style.margin = "0.5rem";

  rightWrap.append(counter, delbtn);
  errbox.append(errmsg, rightWrap);
  document.body.appendChild(errbox);

  let seconds = 5;
  counter.innerText = `(${seconds})`;

  const interval = setInterval(() => {
    seconds--;
    counter.innerText = `(${seconds})`;

    if (seconds <= 0) {
      clearInterval(interval);
      errbox.remove();
    }
  }, 1000);

  delbtn.addEventListener("click", () => {
    clearInterval(interval);
    errbox.remove();
  });
}
