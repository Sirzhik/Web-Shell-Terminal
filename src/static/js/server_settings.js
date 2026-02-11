document.addEventListener("click", async (e) => {
  const server = e.target.closest("[data-serverid]");

  if (!server) return;

  server_settings(server.innerText, server.dataset.serverid);
});

async function server_settings(title, serverId) {
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
  `;
  document.body.appendChild(wrapper);

  const modal = document.createElement("div");
  modal.style.cssText = `
    background-color: #fff;
    padding: 2rem;
    border-radius: 1rem;
    min-width: 60%
    max-width: 100vw
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
  mtText.innerText = title;
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
  instructions.innerText = `Here you can change access to the specified server. Users whose groups are marked here will be able to use WST using the information specified above.`;
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

  const { groups, links } = await take_sg_info();

  const groupsContainer = document.createElement("div");
  groupsContainer.style.cssText = `
        margin-top: 1rem;
        max-height: 200px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-height: 15rem;
        overflow-y: scroll;
        box-sizing: border-box;
    `;
  mBody.appendChild(groupsContainer);

  groups.forEach((group) => {
    const isLinked = links.some(
      (link) =>
        String(link.group_id) === String(group.id) &&
        String(link.server_id) === String(serverId),
    );

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

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = group.id;
    checkbox.checked = isLinked;
    checkbox.dataset.groupId = group.id;
    checkbox.dataset.serverId = serverId;

    checkbox.addEventListener("change", () => {
      console.log(
        `Group ${group.id} status for server ${serverId}: ${checkbox.checked}`,
      );
    });

    label.append(checkbox, group.name);
    groupsContainer.appendChild(label);
  });
}

async function take_sg_info() {
  const response = await fetch("/admin/view-tables");
  const dbInfo = await response.json();

  const dataMap = {
    groups: dbInfo.groups,
    links: dbInfo.group_to_server,
  };

  return dataMap;
}
