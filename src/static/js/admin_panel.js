const lists_assoc = {
  users: {
    listId: "users_list",
    title: (i) => i.username,
    removeType: "user",
  },
  groups: {
    listId: "groups_list",
    title: (i) => i.name,
    removeType: "group",
  },
  servers: {
    listId: "servers_list",
    title: (i) => `${i.username}@${i.domain}`,
    removeType: "virtual_user",
  },
};

document.addEventListener("DOMContentLoaded", loadLists);

document.addEventListener("admin:list:update", async (e) => {
  const { type } = e.detail;
  if (!type) return;

  const response = await fetch("/admin/view-tables");
  const dbInfo = await response.json();

  const dataMap = {
    users: dbInfo.web_users,
    groups: dbInfo.groups,
    servers: dbInfo.virtual_users,
  };

  loadLists();
});


async function loadLists() {
  const response = await fetch("/admin/view-tables");
  const dbInfo = await response.json();

  Object.entries(lists_assoc).forEach(([type, cfg]) => {
    const dataKey =
      type === "users"
        ? "web_users"
        : type === "servers"
          ? "virtual_users"
          : type;

    renderList(type, dbInfo[dataKey]);
  });
}

function renderList(type, data) {
  const cfg = lists_assoc[type];
  const list = document.getElementById(cfg.listId);
  if (!list || !data) return;

  list.innerHTML = "";

  data.forEach((i) => {
    const le = create_listelem(i.id, cfg.title(i), cfg.removeType);
    list.appendChild(le);
  });
}

function create_listelem(id, title, removeType) {
  const div = document.createElement("div");
  div.classList.add("admin-list-elem");
  
  const head = document.createElement("p");
  head.innerText = title;

  if (removeType === "virtual_user" || removeType === "user") {
    head.style.cursor = "pointer";
    
    head.addEventListener("mouseenter", () => {
      head.style.textDecoration = "underline";
    });
    
    head.addEventListener("mouseleave", () => {
      head.style.textDecoration = "none";
    });

    if (removeType === "virtual_user") {
      head.dataset.serverid = id;
    } else if (removeType === "user") {
      head.dataset.userid = id;
    }
  }

  div.appendChild(head);

  const btn = document.createElement("button");
  btn.innerText = "×";
  btn.classList.add("delete-btn");
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    admin_remove(id, removeType);
  });
  div.appendChild(btn);

  return div;
}

async function admin_remove(id, table) {
  const response = await fetch(`/admin/remove_${table}/${id}`, {
    method: "DELETE",
  });

  if (response.ok) {
    const listType = Object.keys(lists_assoc).find(
      (key) => lists_assoc[key].removeType === table
    );

    const updateEvent = new CustomEvent("admin:list:update", {
      detail: { type: listType },
    });

    document.dispatchEvent(updateEvent);
  } else {
    console.error("Error, unable to delete record from database");
  }
}
