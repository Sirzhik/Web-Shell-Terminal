let rows = 50;
let cols = 200;

const termEl = document.getElementById("terminal");
const term = new Terminal({
  rows: rows,
  cols: cols,
  cursorBlink: true,
  theme: {
    background: "#010747"
  },
});
term.open(termEl);

const serverId = termEl?.dataset?.serverId || null;
console.log("Connecting to WebSocket...");
console.log("Server ID:", serverId);
const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const wsUrl = `${wsProtocol}//${window.location.host}/ws/ssh/${serverId}`;
console.log("WebSocket URL:", wsUrl);
const socket = new WebSocket(wsUrl);
socket.binaryType = "arraybuffer";

socket.onopen = () => {
  term.write("Connected to SSH server\r\n");
  try {
    socket.send(JSON.stringify({ cols: cols, rows: rows }));
  } catch (error) {
    console.error("Error sending window size:", error);
    term.write("Error: Failed to send window size\r\n");
  }
  term.focus();
};

socket.addEventListener("message", (event) => {
  term.write(new TextDecoder().decode(event.data));
});

socket.onerror = (error) => {
  console.error("WebSocket error:", error);
  term.write("Error: Connection error\r\n");
};

socket.onclose = () => {
  console.log("WebSocket connection closed");
  term.write("Connection closed\r\n");
};

term.onData((data) => {
  try {
    socket.send(new TextEncoder().encode(data));
  } catch (error) {
    console.error("Error sending data:", error, error.message);
    term.write("Error: Failed to send data\r\n");
  }
});
