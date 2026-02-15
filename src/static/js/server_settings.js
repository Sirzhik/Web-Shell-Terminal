document.addEventListener("click", async (e) => {
  const server = e.target.closest("[data-serverid]");
  if (!server) return;

  server_settings(server.innerText, server.dataset.serverid);
});

async function server_settings(title, serverId) {
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
  mtText.innerText = title;
  mTitle.appendChild(mtText);

  const closeBtn = document.createElement("button");
  closeBtn.classList.add("modal-close");
  closeBtn.innerHTML = "&times;";
  closeBtn.onclick = () => wrapper.remove();
  mTitle.appendChild(closeBtn);

  const mBody = document.createElement("div");
  modal.appendChild(mBody);

  const instructions = document.createElement("p");
  instructions.innerText = `Here you can change access to the specified server. Users whose groups are marked here will be able to use WST using the information specified above.`;
  mBody.appendChild(instructions);

  const search = document.createElement("input");
  search.placeholder = `Search groups`;
  search.classList.add("modal-search");
  mBody.appendChild(search);

  const { groups, links } = await take_sg_info();

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
    const isLinked = links.some(
      (link) =>
        String(link.group_id) === String(group.id) &&
        String(link.server_id) === String(serverId),
    );

    const label = document.createElement("label");
    label.classList.add("group-label");

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
