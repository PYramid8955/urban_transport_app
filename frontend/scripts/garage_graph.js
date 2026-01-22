// garage_graph.js
let cyGarages = null;

export async function openGarageGraph() {
    const res = await fetch("/api/bus_supply_graph");
    if (!res.ok) {
        console.error("Failed to load garage graph");
        return;
    }

    const graphData = await res.json();

    if (!cyGarages) {
        createGarageCy(graphData);
    } else {
        rebuildGarageCy(graphData);
    }
}

function createGarageCy(graphData) {
    cyGarages = cytoscape({
        container: document.getElementById("cy-garages"),
        elements: graphData.elements,

        style: [
            /* ---------- DEFAULT NODES ---------- */
            {
                selector: "node",
                style: {
                    "background-color": "#f1f1f1",
                    "label": "data(label)",
                    "color": "#222",
                    "font-size": "11px",
                    "text-valign": "center",
                    "text-halign": "center",
                    "text-margin-y": 0,
                    "text-margin-x": 0,
                    "text-wrap": "wrap",
                    "text-max-width": 60
                }
            },

            /* ---------- GARAGE NODES ---------- */
            {
                selector: 'node[is_garage]',
                style: {
                    /* SHAPE */
                    'shape': 'round-rectangle',

                    /* SIZE */
                    'width': 25,
                    'height': 25,

                    /* BACKGROUND */
                    'background-color': '#222',
                    'background-image': 'url(/static/res/garage.svg)',
                    'background-fit': 'none',

                    /* IMAGE PADDING (THIS IS THE KEY PART) */
                    'background-width': '16px',
                    'background-height': '16px',
                    'background-position-x': '50%',
                    'background-position-y': '50%',

                    /* BORDER */
                    'border-width': 2,
                    'border-color': '#000',

                    /* LABEL */
                    'label': 'data(label)',
                    'color': '#fff',
                    'text-valign': 'bottom',
                    'text-margin-y': 6
                }
            },


            /* ---------- EDGES ---------- */
            {
                selector: "edge",
                style: {
                    "curve-style": "bezier",
                    "width": ele => {
                        const f = ele.data("flow") || 1;
                        return 2 + Math.log2(f + 1);
                    },
                    "line-color": "#666",
                    "label": ele => {
                        const r = ele.data("route");
                        const f = ele.data("flow");

                        return r !== undefined
                            ? `R${r} • ${f}`
                            : f !== undefined
                                ? `flow: ${f}`
                                : "";
                    },
                    "font-size": "10px",
                    "text-background-color": "#fff",
                    "text-background-opacity": 1,
                    "text-background-padding": "2px",
                    "color": "#000"
                }
            }
        ],

        layout: {
            name: "cose",
            animate: true
        }
    });
}

function rebuildGarageCy(graphData) {
    cyGarages.elements().remove();
    cyGarages.add(graphData.elements);

    const layout = cyGarages.layout({ name: "cose", animate: true });
    layout.run();
}
