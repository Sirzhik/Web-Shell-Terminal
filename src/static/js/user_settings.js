document.addEventListener("click", async (e) => {
  const userElem = e.target.closest("[data-userid]");
  if (!userElem) return;

  user_settings(userElem.innerText, userElem.dataset.userid);
});

async function user_settings(username, userId) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("modal-wrapper");
  wrapper.addEventListener("click", (e) => {
    if (e.target === wrapper) wrapper.remove();
  });
  document.body.appendChild(wrapper);

  const modal = document.createElement("div");
  modal.classList.add("modal");
  wrapper.appendChild(modal);

  const mTitle = document.createElement("div");
  mTitle.classList.add("modal-title");
  modal.appendChild(mTitle);

  const mtText = document.createElement("h2");
  mtText.innerText = username;
  mTitle.appendChild(mtText);

  const closeBtn = document.createElement("button");
  closeBtn.classList.add("modal-close");
  closeBtn.innerHTML = "&times;";
  closeBtn.onclick = () => wrapper.remove();
  mTitle.appendChild(closeBtn);

  const mBody = document.createElement("div");
  modal.appendChild(mBody);

  const instructions = document.createElement("p");
  instructions.innerText = `Here you can select the user group.`;
  mBody.appendChild(instructions);

  const search = document.createElement("input");
  search.placeholder = `Search groups`;
  search.classList.add("modal-search");
  mBody.appendChild(search);

  const { groups, web_users } = await (
    await fetch("/admin/view-tables")
  ).json();

  const currentUser = web_users.find((u) => String(u.id) === String(userId));
  const currentGroupId = currentUser ? currentUser.group_id : null;

  const groupsContainer = document.createElement("div");
  groupsContainer.classList.add("groups-container");
  mBody.appendChild(groupsContainer);

  search.addEventListener("input", (e) => {
    const val = e.target.value.toLowerCase();
    Array.from(groupsContainer.children).forEach((el) => {
      const name = el.innerText.toLowerCase();
      el.style.display = name.includes(val) ? "flex" : "none";
    });
  });

  groups.forEach((group) => {
    const label = document.createElement("label");
    label.classList.add("group-label");

    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "userGroup";
    radio.value = group.id;
    radio.checked = String(group.id) === String(currentGroupId);
    radio.dataset.userId = userId;
    radio.dataset.groupId = group.id;

    label.append(radio, group.name);
    groupsContainer.appendChild(label);
  });
}
