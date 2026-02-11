document.addEventListener("click", async (e) => {
  const userElem = e.target.closest("[data-userid]");
  if (!userElem) return;

  user_settings(userElem.innerText, userElem.dataset.userid);
});

async function user_settings(username, userId) {
  const wrapper = document.createElement("div");
  wrapper.addEventListener("click", (e) => {
    if (e.target === wrapper) wrapper.remove();
  });

  wrapper.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
  document.body.appendChild(wrapper);

  const modal = document.createElement("div");
  modal.style.cssText = `
        background-color: #fff;
        padding: 2rem;
        border-radius: 1rem;
        min-width: 400px;
    `;
  wrapper.appendChild(modal);

  const mTitle = document.createElement("div");
  mTitle.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    `;
  modal.appendChild(mTitle);

  const mtText = document.createElement("h2");
  mtText.innerText = username;
  mTitle.appendChild(mtText);

  const closeBtn = document.createElement("button");
  closeBtn.innerHTML = "&times;";
  closeBtn.style.cssText = `
    cursor: pointer;
    border: none;
    background: none;
    font-size: 2.5rem;
    line-height: 1;
    color: #000;
    opacity: 0.7;
    transition: opacity 0.2s;
    padding: 0;
    margin-left: auto;
    transition: all 200ms ease-in;
    scale: 150%;
  `;
  closeBtn.onmouseover = () => (closeBtn.style.opacity = "1");
  closeBtn.onmouseout = () => (closeBtn.style.opacity = "0.7");
  closeBtn.onclick = () => wrapper.remove();
  mTitle.appendChild(closeBtn);

  
  const mBody = document.createElement("div");
  modal.appendChild(mBody);

  const instructions = document.createElement("p");
  instructions.innerText = `Here you can select the user group.`;
  mBody.appendChild(instructions);

  const search = document.createElement("input");
  search.placeholder = `Search groups`;
  search.style.cssText = `
        width: 100%;
        padding: 0.5rem;
        margin-top: 1rem;
        border: 1px solid #ccc;
        border-radius: 0.5rem;
        box-sizing: border-box;
    `;
  search.addEventListener("input", (e) => {
    const val = e.target.value.toLowerCase();
    Array.from(groupsContainer.children).forEach((el) => {
      const name = el.innerText.toLowerCase();
      el.style.display = name.includes(val) ? "flex" : "none";
    });
  });
  mBody.appendChild(search);

  const { groups, web_users } = await (
    await fetch("/admin/view-tables")
  ).json();
  const currentUser = web_users.find((u) => String(u.id) === String(userId));
  const currentGroupId = currentUser ? currentUser.group_id : null;

  const groupsContainer = document.createElement("div");
  groupsContainer.style.cssText = `
        margin-top: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-height: 200px;
        overflow-y: auto;
    `;
  mBody.appendChild(groupsContainer);

  groups.forEach((group) => {
    const label = document.createElement("label");
    label.style.cssText = `
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            padding: 5px;
            border-radius: 4px;
            transition: background 0.2s;
        `;
    label.onmouseover = () => (label.style.backgroundColor = "#f0f0f0");
    label.onmouseout = () => (label.style.backgroundColor = "transparent");

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
