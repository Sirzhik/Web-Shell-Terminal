document.addEventListener("DOMContentLoaded", renderList);

async function renderList() {
  const servers = await fetch("/term/get_servers_by_user_id", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .catch((error) => {
      console.error("Error fetching servers:", error);
    });

  if (servers) {
    servers.forEach((srv) => {
      renderVirtUser(srv);
    });
  }
}

function renderVirtUser(srv) {
  const termsList = document.getElementById("termsList");
  console.log(srv);

  if (!termsList) {
    console.error('Element with ID "termsList" not found.');
    return;
  }

  const el = document.createElement("a");
  el.href = `/term/${srv.id}`;
  el.classList.add('term-list-elem')

  const virtUser = document.createElement("span");
  virtUser.innerText = `${srv.username}@${srv.domain}`;
  

  el.appendChild(virtUser);
  termsList.appendChild(el);
}
