import {
    cy,
    rebuildFromGraphData,
    updateSnapshotFromCurrentGraph,
    stations,
    tryPathCalculate
} from "./graph_worker.js";

let delFrom = document.getElementById("delFrom");
let delTo = document.getElementById("delTo");
let retBtn = document.getElementById("ret-btn");

const res = await fetch('/api/graph_history_len');
const data = await res.json();
if (data > 1) retBtn.style.display = 'block';

document.getElementById("logout").addEventListener("click", async function () {
    await fetch('/logout');
    window.location.href = "/";
});

document.querySelector("#delete-btn").addEventListener("click", async () => {
    const from = delFrom.value.trim();
    const to = delTo.value.trim();
    delFrom.value = '';
    delTo.value = '';
    delFrom.disabled = false;

    if (!from || !to) return;

    const res = await fetch(
        `/rm_road?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`
    );

    if (!res.ok) return;

    const data = await res.json();

    await rebuildFromGraphData(data);
    retBtn.style.display = 'block';
    await tryPathCalculate();

});

retBtn.addEventListener("click", async () => {
    delFrom.value = '';
    delTo.value = '';
    const res = await fetch('/ret_graph');
    if (!res.ok) return;
    const data = await res.json();
    await rebuildFromGraphData(data);
    retBtn.style.display = 'none';
    await tryPathCalculate();
});

function getNeighbors(nodeId) {
    if (!cy) return [];
    return cy.getElementById(nodeId)
        .connectedEdges()
        .connectedNodes()
        .filter(n => n.id() !== nodeId)
        .map(n => n.data("label"));
}

setupDropdown("delFrom", "delFromDropdown", () => stations);

setupDropdown("delTo", "delToDropdown", () => {
    const from = document.getElementById("delFrom").value.trim();
    if (!from) return [];
    return getNeighbors(from);
});

function setupDropdown(inputId, dropdownId, dataProvider) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    input.addEventListener("input", () => {
        const text = input.value.toLowerCase();
        dropdown.innerHTML = "";

        const data = dataProvider();

        if (!text) {
            dropdown.classList.add("hidden");
            return;
        }

        const results = data.filter(s => s.toLowerCase().includes(text));
        if (!results.length) {
            dropdown.classList.add("hidden");
            return;
        }

        results.forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            li.onclick = () => {
                input.value = r;
                dropdown.classList.add("hidden");
                handleInputLocking();
            };
            dropdown.appendChild(li);
        });

        dropdown.classList.remove("hidden");
    });
}

function handleInputLocking() {
    if (delTo.value.trim() !== "") {
        delFrom.disabled = true;
    } else {
        delFrom.disabled = false;
    }
}

document.getElementById("delTo").addEventListener("input", handleInputLocking);

// garage-flow work
import { openGarageGraph } from "./garage_graph.js";

function garages(open) {
  const screen = document.getElementById("Garage_Screen");

  if (open) {
    screen.style.display = "block";
    openGarageGraph();
  } else screen.style.display = "none";
}

document.getElementById("open_bus_flow_map").addEventListener("click", ()=>{garages(true)});
document.getElementById("close_garage_screen").addEventListener("click", ()=>{garages(false)});