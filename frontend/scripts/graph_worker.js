export let cy = null;
export let initialSnapshot = null;
export let stations = [];

export function updateSnapshotFromCurrentGraph() {
    if (!cy) return;

    initialSnapshot = {
        elements: cy.json().elements,
        positions: cy.nodes().map(n => ({
            id: n.id(),
            position: { ...n.position() }
        }))
    };
}

export function rebuildFromGraphData(graphData) {
    return new Promise(resolve => {
        cy.elements().remove();
        cy.add(graphData.elements);

        const layout = cy.layout({ name: "cose", animate: true });
        layout.run();

        cy.once("layoutstop", () => {
            updateSnapshotFromCurrentGraph();
            resolve(); // <-- now it's done
        });
    });
}

export function restoreInitialGraph() {
    if (!initialSnapshot) return;

    cy.elements().remove();
    cy.add(initialSnapshot.elements);

    initialSnapshot.positions.forEach(p => {
        const node = cy.getElementById(p.id);
        if (node) node.position(p.position);
    });

    cy.fit(undefined, 40);
}


const lineColors = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", "#008080",
    "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3",
    "#808000", "#ffd8b1", "#000075", "#808080", "#ffffff",
    "#ffe119", "#0000ff", "#ff7f00", "#4daf4a", "#984ea3",
    "#a65628", "#f781bf", "#999999", "#e41a1c", "#377eb8",
    "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628",
    "#f781bf", "#999999", "#66c2a5", "#fc8d62", "#8da0cb",
    "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3",
    "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e"
];

function setupDropdown(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    input.addEventListener("input", () => {
        const text = input.value.toLowerCase();
        dropdown.innerHTML = "";

        if (text.trim() === "") {
            dropdown.classList.add("hidden");
            tryPathCalculate();
            return;
        }

        const results = stations.filter(s => s.toLowerCase().includes(text));
        if (results.length === 0) {
            dropdown.classList.add("hidden");
            return;
        }

        results.forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            li.onclick = () => {
                input.value = r;
                dropdown.classList.add("hidden");
                tryPathCalculate();
            };
            dropdown.appendChild(li);
        });

        dropdown.classList.remove("hidden");
    });

    input.addEventListener("change", () => tryPathCalculate());
}

setupDropdown("fromInput", "fromDropdown");
setupDropdown("toInput", "toDropdown");

export async function tryPathCalculate() {
    const from = document.getElementById("fromInput").value.trim();
    const to = document.getElementById("toInput").value.trim();

    if (from === "" || to === "") {
        restoreInitialGraph();
        document.getElementById("resultBox").innerHTML = "<div id = 'nothing_to_show'>Nothing to show here yet.</div>";
        return;
    }

    if (!stations.includes(from) || !stations.includes(to)) return;

    const res = await fetch(`/user_path?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`);
    if (!res.ok) return;

    const data = await res.json();

    const newGraph = data.graph;
    const pathDict = data.path;

    let pathText = "";

    for (const i of pathDict['order']) {
        const value = pathDict[i];
        const startStation = value[0];
        const endStation = value[value.length - 1];
        const color = lineColors[i] || "#777";

        pathText += `
            <div class="route-box" style="border-left: 8px solid ${color}">
                <span class="route-label" style="background:${color}20; color:${color}">
                    Route ${i}
                </span>
                <span class="route-path">${startStation} → ${endStation}</span>
            </div>
        `;
    }

    document.getElementById("resultBox").innerHTML = pathText;

    rebuildCytoscape(newGraph);
}

document.addEventListener("DOMContentLoaded", async () => {
    const res = await fetch("/api/graph");
    const graphData = await res.json();
    stations = graphData.elements.nodes.map(n => n.data.label);
    createCy(graphData);
});

function createCy(graphData) {
    cy = cytoscape({
        container: document.querySelector(".graph-box"),
        elements: graphData.elements,
        style: [
            {
                selector: "node",
                style: {
                    "background-color": "#888",
                    "label": "data(label)",
                    "color": "#000",
                    "font-size": "12px",
                    "text-valign": "center",
                    "text-halign": "center"
                }
            },
            {
                selector: "edge",
                style: {
                    "width": 3,
                    "curve-style": "bezier",
                    "line-color": ele => lineColors[ele.data("number")] || "#888",
                    "target-arrow-shape": "none",
                    "source-arrow-shape": "none"
                }
            }
        ],
        layout: { name: "cose", animate: true }
    });

    // IMPORTANT: snapshot AFTER first layout
    cy.ready(() => {
        updateSnapshotFromCurrentGraph();
    });

}


function rebuildCytoscape(graphData) {
    cy.elements().remove();
    cy.add(graphData.elements);
    cy.layout({ name: "cose", animate: true }).run();
}
