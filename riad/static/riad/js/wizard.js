let guestCount = 2;
let currentGuest = 1;

let guests = [];

let currentMenu = null;
let currentSectionIndex = 0;
let currentGuestChoices = [];
let currentFormula = null;

let isEditing = false;
let editingGuestNumber = null;
let editingChoiceIndex = null;
let editingInProgress = false;

let returnAfterEdit = null;
let savedSectionIndex = null;

let editingFormulaRestart = false;
let guestSnapshotBeforeFormulaEdit = null;
let allGuestsCompleteBeforeFormulaEdit = false;
let pausedGuestProgress = null;

function initWizard() {
    const guestCountEl = document.getElementById("guestCount");

    document.getElementById("minusGuest").onclick = () => {
        if (guestCount > 1) {
            guestCount--;
            guestCountEl.textContent = guestCount;
        }
    };

    document.getElementById("plusGuest").onclick = () => {
        guestCount++;
        guestCountEl.textContent = guestCount;
    };

    document.getElementById("startOrder").onclick = () => {
        updateGuestTitle();
        renderLiveTicket();
        showStep("step-menu");
    };

    document.querySelectorAll(".menu-choice").forEach(btn => {
        btn.onclick = async () => {
            currentMenu = await loadMenu(btn.dataset.menuId);
            currentSectionIndex = 0;
            currentGuestChoices = [];
            currentFormula = null;
            showCurrentSection();
        };
    });

    document.getElementById("saveOrder").onclick = saveCurrentOrder;

    renderLiveTicket();
}

function updateGuestTitle() {
    const el = document.getElementById("currentGuest");

    if (el) {
        el.textContent = `${currentGuest} / ${guestCount}`;
    }
}

function showStep(stepId) {
    ["step-guests", "step-menu", "step-section", "recap"].forEach(id => {
        document.getElementById(id)?.classList.add("d-none");
    });

    document.getElementById(stepId)?.classList.remove("d-none");
}

function getVisibleSections() {
    if (!currentMenu) return [];

    if (!currentFormula) {
        return currentMenu.sections;
    }

    return currentMenu.sections.filter(section => {
        const name = section.name.toLowerCase();

        if (name === "formule") return true;
        if (name.includes("thé") || name.includes("café")) return true;
        if (name === "eau") return true;

        if (currentFormula === "Entrée + Plat") {
            return name.includes("entrée") || name.includes("plat");
        }

        if (currentFormula === "Plat + Dessert") {
            return name.includes("plat") || name.includes("dessert");
        }

        return true;
    });
}

function showCurrentSection() {
    const sections = getVisibleSections();

    if (!currentMenu || !sections[currentSectionIndex]) {
        showStep("step-menu");
        return;
    }

    const section = sections[currentSectionIndex];
    const container = document.getElementById("step-section");

    let html = `
        <div class="d-flex justify-content-between mb-3">
            <button id="btnBack" class="btn btn-outline-secondary">←</button>
            <strong>Convive ${currentGuest} / ${guestCount}</strong>
            <div></div>
        </div>

        <h4 class="text-center">${section.name}</h4>

        <div class="row">
    `;

    section.products.forEach(product => {
        html += `
            <div class="col-md-4 mb-3">
                <button class="btn btn-outline-dark w-100 p-3 product-choice"
                    data-name="${product.name}"
                    data-section="${section.name}"
                    data-section-index="${section.order || currentSectionIndex}">
                    ${product.name}
                </button>
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;

    showStep("step-section");

    document.getElementById("btnBack").onclick = goBack;

    let hasClicked = false;

    document.querySelectorAll(".product-choice").forEach(btn => {
        btn.onclick = () => {
            if (hasClicked) return;
            hasClicked = true;

            document.querySelectorAll(".product-choice").forEach(b => {
                b.disabled = true;
            });

            btn.classList.remove("btn-outline-dark");
            btn.classList.add("btn-success");

            const choice = {
                section_name: btn.dataset.section,
                product_name: btn.dataset.name,
                section_index: parseInt(btn.dataset.sectionIndex),
                note: ""
            };

            if (choice.section_name === "Formule") {
                currentFormula = choice.product_name;

                currentGuestChoices = currentGuestChoices.filter(
                    c => c.section_name !== "Formule"
                );
            }

            if (editingFormulaRestart && choice.section_name === "Formule") {
                restartGuestWithFormula(choice);
                return;
            }

            if (isEditing && editingChoiceIndex >= 0) {
                applyEditedChoice(choice);
                finishEdit();
                return;
            }

            currentGuestChoices.push(choice);

            currentGuestChoices = currentGuestChoices.filter(
                (c, i, arr) =>
                    i === arr.findIndex(x => x.section_index === c.section_index)
            );

            renderLiveTicket();

            setTimeout(nextSection, 150);
        };
    });
}

function nextSection() {
    currentSectionIndex++;

    const sections = getVisibleSections();

    if (currentSectionIndex < sections.length) {
        showCurrentSection();
        return;
    }

    const guestData = {
        number: currentGuest,
        menu_id: currentMenu.id,
        menu_name: currentMenu.name,
        formula: currentFormula,
        choices: [...currentGuestChoices]
    };

    const existing = guests.find(g => g.number === currentGuest);

    if (existing) {
        Object.assign(existing, guestData);
    } else {
        guests.push(guestData);
    }

    guests.sort((a, b) => a.number - b.number);

    resetCurrent();
    renderLiveTicket();

    if (allGuestsCompleteBeforeFormulaEdit) {
        allGuestsCompleteBeforeFormulaEdit = false;
        guestSnapshotBeforeFormulaEdit = null;
        showRecap();
        return;
    }

    if (pausedGuestProgress) {
        currentGuest = pausedGuestProgress.guestNumber;
        currentGuestChoices = [...pausedGuestProgress.choices];
        currentFormula = pausedGuestProgress.formula;
        currentMenu = pausedGuestProgress.menu;
        currentSectionIndex = pausedGuestProgress.sectionIndex;
        pausedGuestProgress = null;

        updateGuestTitle();
        renderLiveTicket();
        showCurrentSection();
        return;
    }

    if (currentGuest < guestCount) {
        currentGuest++;
        updateGuestTitle();
        showStep("step-menu");
    } else {
        showRecap();
    }
}

function isFormulaChoice(choice) {
    return choice?.section_name === "Formule";
}

function getFormulaSectionIndex() {
    if (!currentMenu) return 0;

    const index = currentMenu.sections.findIndex(section => section.name === "Formule");

    return index >= 0 ? index : 0;
}

function restartGuestWithFormula(choice) {
    currentFormula = choice.product_name;
    currentGuestChoices = [choice];

    const sections = getVisibleSections();
    const formulaIndex = sections.findIndex(section => section.name === "Formule");

    currentSectionIndex = formulaIndex + 1;
    editingFormulaRestart = false;

    renderLiveTicket();
    setTimeout(() => {
        if (currentSectionIndex < sections.length) {
            showCurrentSection();
        } else {
            nextSection();
        }
    }, 150);
}

function cancelFormulaRestart() {
    if (guestSnapshotBeforeFormulaEdit) {
        const snapshot = JSON.parse(JSON.stringify(guestSnapshotBeforeFormulaEdit));

        if (!guests.find(g => g.number === snapshot.number)) {
            guests.push(snapshot);
            guests.sort((a, b) => a.number - b.number);
        }

        if (editingInProgress && snapshot.number === currentGuest) {
            currentGuestChoices = [...snapshot.choices];
            currentFormula = snapshot.formula || null;
        }
    }

    if (pausedGuestProgress) {
        currentGuest = pausedGuestProgress.guestNumber;
        currentGuestChoices = [...pausedGuestProgress.choices];
        currentFormula = pausedGuestProgress.formula;
        currentMenu = pausedGuestProgress.menu;
        currentSectionIndex = pausedGuestProgress.sectionIndex;
        pausedGuestProgress = null;
    }

    guestSnapshotBeforeFormulaEdit = null;
    allGuestsCompleteBeforeFormulaEdit = false;
    editingFormulaRestart = false;
    editingInProgress = false;
    editingGuestNumber = null;

    renderLiveTicket();
    restoreAfterEdit();
}

async function startEditFormula(guestNumber) {
    const guest = guests.find(g => g.number === guestNumber);
    const isInProgress = guestNumber === currentGuest && !guest;

    if (!guest && !isInProgress) return;

    saveEditReturnContext();

    allGuestsCompleteBeforeFormulaEdit = guests.length === guestCount;
    editingFormulaRestart = true;
    editingGuestNumber = guestNumber;
    editingInProgress = isInProgress;

    if (currentGuest !== guestNumber && currentGuestChoices.length > 0) {
        pausedGuestProgress = {
            guestNumber: currentGuest,
            choices: [...currentGuestChoices],
            formula: currentFormula,
            menu: currentMenu,
            sectionIndex: currentSectionIndex,
        };
    }

    currentGuest = guestNumber;

    if (guest) {
        guestSnapshotBeforeFormulaEdit = JSON.parse(JSON.stringify(guest));
        guests = guests.filter(g => g.number !== guestNumber);
        currentMenu = await loadMenu(guest.menu_id);
        currentFormula = null;
        currentGuestChoices = [];
    } else {
        guestSnapshotBeforeFormulaEdit = {
            number: guestNumber,
            menu_id: currentMenu.id,
            menu_name: currentMenu.name,
            formula: currentFormula,
            choices: [...currentGuestChoices],
        };
        currentFormula = null;
        currentGuestChoices = [];
    }

    currentSectionIndex = getFormulaSectionIndex();

    updateGuestTitle();
    showCurrentSection();
}

function findChoice(guestNumber, sectionIndex) {
    const guest = guests.find(g => g.number === guestNumber);

    if (guest) {
        return guest.choices.find(c => c.section_index === sectionIndex) || null;
    }

    if (guestNumber === currentGuest) {
        return currentGuestChoices.find(c => c.section_index === sectionIndex) || null;
    }

    return null;
}

function addChoiceNote(guestNumber, sectionIndex) {
    const choice = findChoice(guestNumber, sectionIndex);
    if (!choice) return;

    const note = prompt("Note pour ce choix", choice.note || "");

    if (note !== null) {
        choice.note = note.trim();
        renderLiveTicket();

        if (!document.getElementById("recap")?.classList.contains("d-none")) {
            showRecap();
        }
    }
}

function getCurrentWizardContext() {
    if (!document.getElementById("recap")?.classList.contains("d-none")) {
        return "recap";
    }

    if (!document.getElementById("step-section")?.classList.contains("d-none")) {
        return "section";
    }

    if (!document.getElementById("step-menu")?.classList.contains("d-none")) {
        return "menu";
    }

    return "guests";
}

function saveEditReturnContext() {
    returnAfterEdit = getCurrentWizardContext();

    if (returnAfterEdit === "section") {
        savedSectionIndex = currentSectionIndex;
    }
}

function restoreAfterEdit() {
    const context = returnAfterEdit;

    returnAfterEdit = null;

    if (context === "recap") {
        showRecap();
        return;
    }

    if (context === "menu") {
        showStep("step-menu");
        return;
    }

    if (context === "section") {
        if (savedSectionIndex !== null) {
            currentSectionIndex = savedSectionIndex;
        }

        savedSectionIndex = null;

        if (currentMenu) {
            showCurrentSection();
        } else {
            showStep("step-menu");
        }

        return;
    }

    savedSectionIndex = null;
}

function applyEditedChoice(choice) {
    if (editingInProgress) {
        currentGuestChoices = currentGuestChoices.map(c => {
            if (c.section_index === editingChoiceIndex) {
                choice.note = c.note || "";
                return choice;
            }

            return c;
        });

        if (choice.section_name === "Formule") {
            currentFormula = choice.product_name;

            currentGuestChoices = currentGuestChoices.filter(
                c => c.section_name !== "Formule" || c.section_index === choice.section_index
            );
        }

        return;
    }

    const guest = guests.find(g => g.number === editingGuestNumber);

    if (!guest) return;

    guest.choices = guest.choices.map(c => {
        if (c.section_index === editingChoiceIndex) {
            choice.note = c.note || "";
            return choice;
        }

        return c;
    });

    if (choice.section_name === "Formule") {
        guest.formula = choice.product_name;
        currentFormula = choice.product_name;
    }
}

function finishEdit() {
    const context = returnAfterEdit;

    resetEditing();

    if (context === "section") {
        if (savedSectionIndex !== null) {
            currentSectionIndex = savedSectionIndex;
        }
    } else {
        resetCurrent();
    }

    renderLiveTicket();
    restoreAfterEdit();
}

async function startEditChoice(guestNumber, sectionIndex) {
    const choice = findChoice(guestNumber, sectionIndex);

    if (isFormulaChoice(choice)) {
        return startEditFormula(guestNumber);
    }

    const guest = guests.find(g => g.number === guestNumber);
    const isInProgress = guestNumber === currentGuest && !guest;

    if (!guest && !isInProgress) return;

    saveEditReturnContext();

    isEditing = true;
    editingGuestNumber = guestNumber;
    editingChoiceIndex = sectionIndex;
    editingInProgress = isInProgress;

    currentGuest = guestNumber;

    if (guest) {
        currentMenu = await loadMenu(guest.menu_id);
        currentFormula = guest.formula || null;
        currentGuestChoices = [];
    }

    const sectionToEdit = findChoice(guestNumber, sectionIndex);
    const sections = getVisibleSections();

    currentSectionIndex = sections.findIndex(s => {
        return sectionToEdit && s.name === sectionToEdit.section_name;
    });

    if (currentSectionIndex < 0) {
        currentSectionIndex = 0;
    }

    updateGuestTitle();
    showCurrentSection();
}

function goBack() {
    if (editingFormulaRestart) {
        cancelFormulaRestart();
        return;
    }

    if (isEditing) {
        finishEdit();
        return;
    }

    if (currentSectionIndex === 0) {
        resetCurrent();
        renderLiveTicket();
        showStep("step-menu");
        return;
    }

    currentSectionIndex--;

    const removedChoice = currentGuestChoices.pop();

    if (removedChoice && removedChoice.section_name === "Formule") {
        currentFormula = null;
    }

    renderLiveTicket();
    showCurrentSection();
}

function showRecap() {
    let html = "";

    guests.forEach(guest => {
        html += `
        <div class="card mb-3">
            <div class="card-body">

                <div class="d-flex justify-content-between">
                    <strong>Convive ${guest.number}</strong>
                    <button class="btn btn-sm btn-danger edit-menu"
                        data-number="${guest.number}">
                        Menu
                    </button>
                </div>

                <div class="text-muted">${guest.menu_name}</div>
                <hr>
        `;

        guest.choices.forEach(c => {
            const isFormula = isFormulaChoice(c);

            html += `
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <span>${c.section_name} : ${c.product_name}</span>

                        ${c.note ? `<div class="text-warning small mt-1">📝 ${c.note}</div>` : ""}
                    </div>

                    <div class="d-flex gap-2">
                        ${isFormula ? "" : `
                        <button class="btn btn-sm btn-outline-warning choice-note"
                            data-number="${guest.number}"
                            data-index="${c.section_index}">
                            + note
                        </button>
                        `}

                        <button class="btn btn-sm btn-outline-secondary edit-line"
                            data-number="${guest.number}"
                            data-index="${c.section_index}">
                            ${isFormula ? "Changer formule" : "Modifier"}
                        </button>
                    </div>
                </div>
            `;
        });

        html += `</div></div>`;
    });

    document.getElementById("recapContent").innerHTML = html;
    showStep("recap");

    bindRecapButtons();
}

function bindChoiceButtons(root = document) {
    root.querySelectorAll(".choice-note").forEach(btn => {
        btn.onclick = () => {
            addChoiceNote(
                parseInt(btn.dataset.number),
                parseInt(btn.dataset.index)
            );
        };
    });

    root.querySelectorAll(".edit-line").forEach(btn => {
        btn.onclick = () => {
            startEditChoice(
                parseInt(btn.dataset.number),
                parseInt(btn.dataset.index)
            );
        };
    });
}

function bindRecapButtons() {
    bindChoiceButtons(document.getElementById("recapContent"));

    document.querySelectorAll(".edit-menu").forEach(btn => {
        btn.onclick = () => {
            const guestNumber = parseInt(btn.dataset.number);

            saveEditReturnContext();

            isEditing = true;
            editingGuestNumber = guestNumber;
            editingChoiceIndex = -1;
            editingInProgress = false;

            currentGuest = guestNumber;
            currentMenu = null;
            currentSectionIndex = 0;
            currentGuestChoices = [];
            currentFormula = null;

            updateGuestTitle();
            showStep("step-menu");
        };
    });
}

function renderChoiceLine(guestNumber, choice) {
    const isFormula = isFormulaChoice(choice);

    return `
        <div class="d-flex justify-content-between align-items-start mb-1 gap-1">
            <div class="text-muted small">
                - ${choice.product_name}
                ${choice.note ? `<div class="text-warning small">📝 ${choice.note}</div>` : ""}
            </div>

            <div class="d-flex gap-1 flex-shrink-0">
                ${isFormula ? "" : `
                <button type="button"
                    class="btn btn-sm btn-outline-warning choice-note py-0 px-1"
                    data-number="${guestNumber}"
                    data-index="${choice.section_index}"
                    title="Ajouter une note">
                    + note
                </button>
                `}

                <button type="button"
                    class="btn btn-sm btn-outline-secondary edit-line py-0 px-1"
                    data-number="${guestNumber}"
                    data-index="${choice.section_index}"
                    title="${isFormula ? "Changer la formule" : "Modifier ce plat"}">
                    ${isFormula ? "Formule" : "Modif."}
                </button>
            </div>
        </div>
    `;
}

function renderLiveTicket() {
    const container = document.getElementById("liveTicket");
    if (!container) return;

    let html = "";

    guests.forEach(g => {
        html += `<div class="mb-2"><strong>Convive ${g.number}</strong>`;

        g.choices.forEach(c => {
            html += renderChoiceLine(g.number, c);
        });

        html += `</div>`;
    });

    if (!isEditing && currentGuestChoices.length > 0) {
        html += `<div class="mb-2 border-top pt-2">`;
        html += `<strong>Convive ${currentGuest} (en cours)</strong>`;

        currentGuestChoices.forEach(c => {
            html += renderChoiceLine(currentGuest, c);
        });

        html += `</div>`;
    }

    container.innerHTML = html || `<p class="text-muted">Aucune commande</p>`;

    bindChoiceButtons(container);
}

function getTableNumberFromUrl() {
    const match = window.location.pathname.match(/table\/(\d+)\/commande/);
    return match ? parseInt(match[1]) : null;
}

function getCSRFToken() {
    const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookie ? cookie.split("=")[1] : "";
}

async function saveCurrentOrder() {
    if (guests.length === 0) {
        alert("Aucune commande à valider");
        return;
    }

    const tableNumber = getTableNumberFromUrl();

    if (!tableNumber) {
        alert("Erreur : numéro de table introuvable");
        return;
    }

    const saveBtn = document.getElementById("saveOrder");

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = "Envoi en cuisine...";
    }

    try {
        const response = await fetch(`/riad/api/table/${tableNumber}/send-kitchen/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                guests_count: guestCount,
                guests: guests
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert("Erreur pendant l'envoi en cuisine");
            return;
        }

        window.location.href = "/riad/kitchen/";

    } catch (error) {
        alert("Erreur réseau pendant l'envoi en cuisine");
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = "Valider";
        }
    }
}

function resetEditing() {
    isEditing = false;
    editingGuestNumber = null;
    editingChoiceIndex = null;
    editingInProgress = false;
}

function resetCurrent() {
    currentGuestChoices = [];
    currentSectionIndex = 0;
    currentFormula = null;
}