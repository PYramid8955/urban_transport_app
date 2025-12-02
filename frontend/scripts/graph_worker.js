let stations = [];
let originalCyData = null;
let cy = null;

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

async function tryPathCalculate() {
    const from = document.getElementById("fromInput").value.trim();
    const to = document.getElementById("toInput").value.trim();

    if (from === "" || to === "") {
        rebuildCytoscape(originalCyData);
        document.getElementById("resultBox").innerHTML = "";
        return;
    }

    if (!stations.includes(from) || !stations.includes(to)) return;

    const res = await fetch(`/user_path?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`);
    if (!res.ok) return;

    const data = await res.json();

    const newGraph = data.graph;
    const pathList = data.path;

    document.getElementById("resultBox").innerHTML = pathList.join(" → ");

    rebuildCytoscape(newGraph);
}

document.addEventListener("DOMContentLoaded", async () => {
    const res = await fetch("/api/graph");
    const graphData = await res.json();
    originalCyData = graphData;
    stations = graphData.elements.nodes.map(n => n.data.label);
    createCy(graphData);
});

function createCy(graphData) {
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
}

function rebuildCytoscape(graphData) {
    cy.json({ elements: graphData.elements });
    cy.layout({ name: "cose", animate: true }).run();
}
