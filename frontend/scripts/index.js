const stations = [
    "Cocieri",
    "Cosnita",
    "Chisinau",
    "Briceni",
    "Ocnita",
    "Leuseni",
    "Stefan-Voda",
    "",
];

function setupDropdown(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);

    input.addEventListener("input", () => {
        const text = input.value.toLowerCase();
        dropdown.innerHTML = "";

        if (text.trim() === "") {
            dropdown.classList.add("hidden");
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
            };
            dropdown.appendChild(li);
        });

        dropdown.classList.remove("hidden");
    });
}

setupDropdown("fromInput", "fromDropdown");
setupDropdown("toInput", "toDropdown");
