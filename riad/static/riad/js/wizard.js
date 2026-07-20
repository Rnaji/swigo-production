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

let editingMenuRestart = false;
let guestSnapshotBeforeMenuEdit = null;
let allGuestsCompleteBeforeMenuEdit = false;

let pendingSubChoice = null;
let isPickingSubChoice = false;

const DRINK_SECTIONS = new Set(["Boisson", "Jus", "Eau"]);
const MOCKTAIL_REPLACEMENT_SUPPLEMENT = 3.5;
const COUPE_REPLACEMENT_SUPPLEMENT = 2;

let editingOriginalProductName = null;

let wizardExtras = [];
let wizardExtraTempId = 1;
let editingExtraTempId = null;
let wizardStarted = false;

let draftSaveTimer = null;
const DRAFT_SAVE_DEBOUNCE_MS = 500;
let draftRestoreInProgress = false;

let wizardAddItemData = null;
let wizardSelectedCategory = null;
let wizardSelectedProduct = null;
let wizardSelectedGuest = 1;
let wizardSelectedQty = 1;
let wizardManualSelectedGuest = 1;

function getChoiceProductName(choice) {
    return choice.sub_choice_product_name || choice.product_name;
}

function isMocktailProduct(productName) {
    return Boolean(
        currentMenu?.replacement_options?.mocktails?.some(
            product => product.name === productName
        )
    );
}

function isCoupeProduct(productName) {
    return Boolean(
        currentMenu?.replacement_options?.coupes?.some(
            product => product.name === productName
        )
    );
}

function sectionIncludesProduct(sectionName, productName) {
    const section = currentMenu?.sections?.find(item => item.name === sectionName);
    return Boolean(section?.products?.some(product => product.name === productName));
}

function computeReplacementSupplement(sectionName, originalProductName, newProductName) {
    if (!currentMenu || !originalProductName || originalProductName === newProductName) {
        return 0;
    }

    if (sectionIncludesProduct(sectionName, newProductName)) {
        return 0;
    }

    if (DRINK_SECTIONS.has(sectionName) && isMocktailProduct(newProductName)) {
        return MOCKTAIL_REPLACEMENT_SUPPLEMENT;
    }

    if (
        sectionName === "Dessert" &&
        isCoupeProduct(newProductName) &&
        !currentMenu.replacement_options?.has_coupe_choice
    ) {
        return COUPE_REPLACEMENT_SUPPLEMENT;
    }

    return 0;
}

function applyChoiceBillingDefaults(choice) {
    choice.source = "menu";
    choice.supplement_amount = 0;
    choice.replaced_product_name = "";
    return choice;
}

async function confirmReplacementIfNeeded(choice) {
    if (!isEditing || !editingOriginalProductName) {
        return applyChoiceBillingDefaults(choice);
    }

    const newProductName = getChoiceProductName(choice);
    const baseProductName = choice.replaced_product_name || editingOriginalProductName;
    const supplement = computeReplacementSupplement(
        choice.section_name,
        baseProductName,
        newProductName
    );

    if (newProductName !== editingOriginalProductName && supplement > 0) {
        const confirmed = window.confirm(
            `Remplacer ${editingOriginalProductName} par ${newProductName}\n\nSupplément : +${supplement.toFixed(2)} €`
        );

        if (!confirmed) {
            return null;
        }

        choice.source = "replacement";
        choice.supplement_amount = supplement;
        choice.replaced_product_name = baseProductName;
        return choice;
    }

    return applyChoiceBillingDefaults(choice);
}

function formatChoiceSupplementLine(choice) {
    if (choice.source === "replacement" && Number(choice.supplement_amount) > 0) {
        return `<div class="text-success small">Remplacement — supplément +${Number(choice.supplement_amount).toFixed(2)} €</div>`;
    }

    return "";
}

function getSectionProductButtons(section) {
    const products = [...(section.products || [])];

    if (!isEditing || !editingOriginalProductName) {
        return products;
    }

    const existingNames = new Set(products.map(product => product.name));

    if (DRINK_SECTIONS.has(section.name)) {
        currentMenu?.replacement_options?.mocktails?.forEach(product => {
            if (!existingNames.has(product.name)) {
                products.push(product);
            }
        });
    }

    if (
        section.name === "Dessert" &&
        !currentMenu?.replacement_options?.has_coupe_choice
    ) {
        currentMenu?.replacement_options?.coupes?.forEach(product => {
            if (!existingNames.has(product.name)) {
                products.push(product);
            }
        });
    }

    return products;
}

function initWizard() {
    const guestCountEl = document.getElementById("guestCount");

    document.getElementById("minusGuest").onclick = () => {
        if (guestCount > 1) {
            guestCount--;
            guestCountEl.textContent = guestCount;
            scheduleWizardDraftSave();
        }
    };

    document.getElementById("plusGuest").onclick = () => {
        guestCount++;
        guestCountEl.textContent = guestCount;
        scheduleWizardDraftSave();
    };

    document.getElementById("startOrder").onclick = () => {
        wizardStarted = true;
        document.getElementById("wizardAddExtraBtn")?.classList.remove("d-none");
        updateGuestTitle();
        renderLiveTicket();
        showStep("step-menu");
        scheduleWizardDraftSave();
    };

    document.querySelectorAll(".menu-choice").forEach(btn => {
        btn.onclick = async () => {
            currentMenu = await loadMenu(btn.dataset.menuId);
            currentSectionIndex = 0;
            currentGuestChoices = [];
            currentFormula = null;

            if (editingMenuRestart) {
                editingMenuRestart = false;
                hideMenuEditBackButton();
            }

            renderLiveTicket();
            showCurrentSection();
        };
    });

    document.getElementById("saveOrder").onclick = saveCurrentOrder;

    initWizardExtrasModal();
    bootstrapWizardFromDraft();
}

function getInitialWizardDraft() {
    const el = document.getElementById("riad-wizard-draft");
    if (!el) return null;

    try {
        const data = JSON.parse(el.textContent);
        return data && typeof data === "object" ? data : null;
    } catch (error) {
        return null;
    }
}

function buildWizardDraftPayload() {
    return {
        version: 1,
        guest_count: guestCount,
        current_guest: currentGuest,
        current_step: getCurrentWizardContext(),
        wizard_started: wizardStarted,
        guests: JSON.parse(JSON.stringify(guests)),
        current_menu_id: currentMenu?.id || null,
        current_formula: currentFormula,
        current_guest_choices: JSON.parse(JSON.stringify(currentGuestChoices)),
        current_section_index: currentSectionIndex,
        wizard_extras: JSON.parse(JSON.stringify(wizardExtras)),
        wizard_extra_temp_id: wizardExtraTempId,
    };
}

function scheduleWizardDraftSave() {
    if (draftRestoreInProgress) return;

    clearTimeout(draftSaveTimer);
    draftSaveTimer = setTimeout(() => {
        saveWizardDraftNow();
    }, DRAFT_SAVE_DEBOUNCE_MS);
}

async function saveWizardDraftNow() {
    const tableNumber = getTableNumberFromUrl();
    if (!tableNumber) return;

    const draft = buildWizardDraftPayload();
    if (!draft.wizard_started && draft.guest_count <= 0) return;

    try {
        await fetch(`/riad/api/table/${tableNumber}/draft/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ draft }),
        });
    } catch (error) {
        // Sauvegarde best-effort : ne pas bloquer le wizard.
    }
}

async function restoreWizardFromDraft(draft) {
    if (!draft) return false;

    draftRestoreInProgress = true;

    try {
        guestCount = draft.guest_count || 2;
        document.getElementById("guestCount").textContent = guestCount;

        if (!draft.wizard_started) {
            showStep("step-guests");
            return true;
        }

        wizardStarted = true;
        currentGuest = draft.current_guest || 1;
        guests = draft.guests || [];
        currentFormula = draft.current_formula || null;
        currentGuestChoices = draft.current_guest_choices || [];
        currentSectionIndex = draft.current_section_index || 0;
        wizardExtras = draft.wizard_extras || [];
        wizardExtraTempId = draft.wizard_extra_temp_id || 1;

        document.getElementById("wizardAddExtraBtn")?.classList.remove("d-none");
        updateGuestTitle();
        renderLiveTicket();

        const allGuestsRecorded = guests.length >= guestCount;
        const hasInProgressChoices =
            currentGuestChoices.length > 0 ||
            (draft.current_menu_id && guests.length < guestCount);

        if (
            draft.current_step === "recap" ||
            (allGuestsRecorded && !hasInProgressChoices)
        ) {
            showRecap();
            return true;
        }

        if (draft.current_menu_id) {
            currentMenu = await loadMenu(draft.current_menu_id);
        }

        if (draft.current_step === "section" && currentMenu) {
            showCurrentSection();
        } else {
            showStep("step-menu");
        }

        return true;
    } finally {
        draftRestoreInProgress = false;
    }
}

async function bootstrapWizardFromDraft() {
    const draft = getInitialWizardDraft();

    if (draft) {
        await restoreWizardFromDraft(draft);
    } else {
        renderLiveTicket();
        showStep("step-guests");
    }

    finishWizardInit();
}

function finishWizardInit() {
    document.querySelector(".commande-wizard")?.classList.remove("wizard-loading");
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
    updateCancelOrderButtonVisibility(stepId);
}

function updateCancelOrderButtonVisibility(stepId = null) {
    const cancelBtn = document.getElementById("cancelOrderBtn");
    if (!cancelBtn) return;

    const activeStep = stepId || ["step-guests", "step-menu", "step-section", "recap"]
        .find(id => !document.getElementById(id)?.classList.contains("d-none"));

    cancelBtn.classList.toggle("d-none", activeStep !== "recap");
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

function getProductFromCurrentSection(productName) {
    const sections = getVisibleSections();
    const section = sections[currentSectionIndex];

    if (!section) return null;

    return section.products.find(product => product.name === productName) || null;
}

function getProductFromMenuSection(sectionName, productName) {
    if (!currentMenu) return null;

    const section = currentMenu.sections.find(item => item.name === sectionName);
    if (!section) return null;

    return section.products.find(product => product.name === productName) || null;
}

function getProductButtonLabel(product) {
    if (!product) return "";

    return product.short_name || product.name;
}

function formatChoiceLabel(choice, useShort = false) {
    const parentName = useShort
        ? (choice.short_label || choice.product_name)
        : choice.product_name;

    if (choice.sub_choice_product_name) {
        const subName = useShort
            ? (choice.sub_choice_short_label || choice.sub_choice_product_name)
            : choice.sub_choice_product_name;

        return `${parentName} : ${subName}`;
    }

    return parentName;
}

function attachChoiceLabels(choice, productData) {
    if (!productData) return choice;

    choice.short_label = productData.short_name || "";

    return choice;
}

function showSubChoiceSection(parentProduct, baseChoice) {
    const container = document.getElementById("step-section");

    let html = `
        <div class="d-flex justify-content-between mb-3">
            <button id="btnBack" class="btn btn-outline-secondary">←</button>
            <strong>Convive ${currentGuest} / ${guestCount}</strong>
            <div></div>
        </div>

        <h4 class="text-center">${getProductButtonLabel(parentProduct)}</h4>
        <p class="text-muted text-center mb-4">Choisissez la coupe glacée</p>

        <div class="row">
    `;

    parentProduct.sub_choices.forEach(subProduct => {
        html += `
            <div class="col-md-4 mb-3">
                <button class="btn btn-outline-dark w-100 p-3 subchoice-product"
                    data-name="${subProduct.name}">
                    ${getProductButtonLabel(subProduct)}
                </button>
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;

    showStep("step-section");
    isPickingSubChoice = true;
    pendingSubChoice = baseChoice;

    document.getElementById("btnBack").onclick = cancelSubChoice;

    let hasClicked = false;

    document.querySelectorAll(".subchoice-product").forEach(btn => {
        btn.onclick = async () => {
            if (hasClicked) return;
            hasClicked = true;

            const choice = {
                section_name: pendingSubChoice.section_name,
                product_name: pendingSubChoice.product_name,
                section_index: pendingSubChoice.section_index,
                short_label: pendingSubChoice.short_label || "",
                note: pendingSubChoice.note || "",
                sub_choice_product_name: btn.dataset.name,
                sub_choice_short_label: parentProduct.sub_choices.find(
                    sub => sub.name === btn.dataset.name
                )?.short_name || "",
            };

            const billedChoice = await confirmReplacementIfNeeded(choice);
            if (!billedChoice) {
                hasClicked = false;
                return;
            }

            pendingSubChoice = null;
            isPickingSubChoice = false;

            finalizeChoice(billedChoice);
        };
    });
}

function cancelSubChoice() {
    pendingSubChoice = null;
    isPickingSubChoice = false;
    showCurrentSection();
}

function finalizeChoice(choice) {
    if (!choice.source) {
        applyChoiceBillingDefaults(choice);
    }

    if (choice.section_name === "Formule") {
        currentFormula = choice.product_name;

        currentGuestChoices = currentGuestChoices.filter(
            c => c.section_name !== "Formule"
        );
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
    scheduleWizardDraftSave();
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

    getSectionProductButtons(section).forEach(product => {
        html += `
            <div class="col-md-4 mb-3">
                <button class="btn btn-outline-dark w-100 p-3 product-choice"
                    data-name="${product.name}"
                    data-section="${section.name}"
                    data-section-index="${section.order || currentSectionIndex}">
                    ${getProductButtonLabel(product)}
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
        btn.onclick = async () => {
            if (hasClicked) return;
            hasClicked = true;

            const choice = {
                section_name: btn.dataset.section,
                product_name: btn.dataset.name,
                section_index: parseInt(btn.dataset.sectionIndex),
                note: ""
            };

            const productData = getProductFromCurrentSection(btn.dataset.name)
                || currentMenu?.replacement_options?.mocktails?.find(p => p.name === btn.dataset.name)
                || currentMenu?.replacement_options?.coupes?.find(p => p.name === btn.dataset.name);

            if (productData?.sub_choices?.length) {
                showSubChoiceSection(productData, attachChoiceLabels(choice, productData));
                return;
            }

            if (editingFormulaRestart && choice.section_name === "Formule") {
                restartGuestWithFormula(choice);
                return;
            }

            const billedChoice = await confirmReplacementIfNeeded(choice);
            if (!billedChoice) {
                hasClicked = false;
                return;
            }

            document.querySelectorAll(".product-choice").forEach(b => {
                b.disabled = true;
            });

            btn.classList.remove("btn-outline-dark");
            btn.classList.add("btn-success");

            finalizeChoice(attachChoiceLabels(billedChoice, productData));
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

    const shouldReturnToRecap =
        allGuestsCompleteBeforeFormulaEdit || allGuestsCompleteBeforeMenuEdit;

    const wasRebuild =
        guestSnapshotBeforeMenuEdit !== null ||
        guestSnapshotBeforeFormulaEdit !== null ||
        editingMenuRestart ||
        editingFormulaRestart;

    resetCurrent();

    if (wasRebuild) {
        clearGuestRebuildState();
    } else {
        currentMenu = null;
    }

    renderLiveTicket();

    if (shouldReturnToRecap) {
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

    scheduleWizardDraftSave();
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

function cancelMenuRestart() {
    if (guestSnapshotBeforeMenuEdit) {
        const snapshot = JSON.parse(JSON.stringify(guestSnapshotBeforeMenuEdit));

        if (!guests.find(g => g.number === snapshot.number)) {
            guests.push(snapshot);
            guests.sort((a, b) => a.number - b.number);
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

    guestSnapshotBeforeMenuEdit = null;
    allGuestsCompleteBeforeMenuEdit = false;
    editingMenuRestart = false;
    editingGuestNumber = null;

    resetCurrent();
    hideMenuEditBackButton();
    renderLiveTicket();
    restoreAfterEdit();
}

function ensureMenuEditBackButton() {
    const stepMenu = document.getElementById("step-menu");
    if (!stepMenu) return;

    let btn = document.getElementById("btnBackMenuEdit");

    if (!btn) {
        btn = document.createElement("button");
        btn.type = "button";
        btn.id = "btnBackMenuEdit";
        btn.className = "btn btn-outline-secondary mb-3";
        btn.textContent = "← Annuler";
        btn.onclick = cancelMenuRestart;
        stepMenu.insertBefore(btn, stepMenu.firstChild);
    }

    btn.classList.remove("d-none");
}

function hideMenuEditBackButton() {
    document.getElementById("btnBackMenuEdit")?.classList.add("d-none");
}

function startEditMenu(guestNumber) {
    const guest = guests.find(g => g.number === guestNumber);
    if (!guest) return;

    saveEditReturnContext();

    allGuestsCompleteBeforeMenuEdit = guests.length === guestCount;
    editingMenuRestart = true;
    editingGuestNumber = guestNumber;

    if (currentGuest !== guestNumber && currentGuestChoices.length > 0) {
        pausedGuestProgress = {
            guestNumber: currentGuest,
            choices: [...currentGuestChoices],
            formula: currentFormula,
            menu: currentMenu,
            sectionIndex: currentSectionIndex,
        };
    }

    guestSnapshotBeforeMenuEdit = JSON.parse(JSON.stringify(guest));
    guests = guests.filter(g => g.number !== guestNumber);

    currentGuest = guestNumber;
    currentMenu = null;
    currentSectionIndex = 0;
    currentGuestChoices = [];
    currentFormula = null;

    updateGuestTitle();
    renderLiveTicket();
    showStep("step-menu");
    ensureMenuEditBackButton();
}

function isGuestBeingRebuilt(guestNumber) {
    if (guestSnapshotBeforeMenuEdit?.number === guestNumber) {
        return true;
    }

    if (guestSnapshotBeforeFormulaEdit?.number === guestNumber) {
        return true;
    }

    return editingMenuRestart && guestNumber === editingGuestNumber;
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

        scheduleWizardDraftSave();
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

function mergeEditedChoice(oldChoice, newChoice) {
    const merged = {
        section_name: newChoice.section_name,
        section_index: newChoice.section_index,
        product_name: newChoice.product_name,
        note: oldChoice.note || "",
        source: newChoice.source ?? "menu",
        supplement_amount: Number(newChoice.supplement_amount) || 0,
        replaced_product_name: newChoice.replaced_product_name || "",
        short_label: newChoice.short_label || "",
    };

    if (newChoice.sub_choice_product_name) {
        merged.sub_choice_product_name = newChoice.sub_choice_product_name;
        merged.sub_choice_short_label = newChoice.sub_choice_short_label || "";
    }

    return merged;
}

function applyEditedChoice(choice) {
    if (editingInProgress) {
        currentGuestChoices = currentGuestChoices.map(c => {
            if (c.section_index === editingChoiceIndex) {
                return mergeEditedChoice(c, choice);
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
            return mergeEditedChoice(c, choice);
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
    scheduleWizardDraftSave();
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

    const sectionToEdit = findChoice(guestNumber, sectionIndex);
    editingOriginalProductName = sectionToEdit
        ? getChoiceProductName(sectionToEdit)
        : null;

    if (guest) {
        currentMenu = await loadMenu(guest.menu_id);
        currentFormula = guest.formula || null;
        currentGuestChoices = [];
    }

    if (sectionToEdit?.sub_choice_product_name) {
        const productData = getProductFromMenuSection(
            sectionToEdit.section_name,
            sectionToEdit.product_name
        );

        if (productData?.sub_choices?.length) {
            const baseChoice = {
                section_name: sectionToEdit.section_name,
                product_name: sectionToEdit.product_name,
                section_index: sectionToEdit.section_index,
                note: sectionToEdit.note || "",
            };

            updateGuestTitle();
            showSubChoiceSection(productData, baseChoice);
            return;
        }
    }

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
    if (isPickingSubChoice) {
        cancelSubChoice();
        return;
    }

    if (editingMenuRestart) {
        cancelMenuRestart();
        return;
    }

    if (editingFormulaRestart) {
        cancelFormulaRestart();
        return;
    }

    if (isEditing) {
        finishEdit();
        return;
    }

    if (currentSectionIndex === 0) {
        if (guestSnapshotBeforeMenuEdit) {
            editingMenuRestart = true;
            renderLiveTicket();
            showStep("step-menu");
            ensureMenuEditBackButton();
            return;
        }

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
                        <span>${c.section_name} : ${formatChoiceLabel(c, false)}</span>
                        ${formatChoiceSupplementLine(c)}

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

        getExtrasForGuest(guest.number).forEach(extra => {
            html += renderExtraRecapLine(guest.number, extra);
        });

        html += `</div></div>`;
    });

    document.getElementById("recapContent").innerHTML = html;
    showStep("recap");

    bindRecapButtons();
    bindExtraButtons(document.getElementById("recapContent"));
    renderLiveTicket();
    scheduleWizardDraftSave();
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
            startEditMenu(parseInt(btn.dataset.number));
        };
    });
}

function renderChoiceLine(guestNumber, choice) {
    const isFormula = isFormulaChoice(choice);

    return `
        <div class="d-flex justify-content-between align-items-start mb-1 gap-1">
            <div class="text-muted small">
                - ${formatChoiceLabel(choice, true)}
                ${formatChoiceSupplementLine(choice)}
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
    const renderedGuestExtras = new Set();

    guests.forEach(g => {
        html += `<div class="mb-2"><strong>Convive ${g.number}</strong>`;

        g.choices.forEach(c => {
            html += renderChoiceLine(g.number, c);
        });

        getExtrasForGuest(g.number).forEach(extra => {
            html += renderExtraLine(g.number, extra);
        });

        if (getExtrasForGuest(g.number).length > 0) {
            renderedGuestExtras.add(g.number);
        }

        html += `</div>`;
    });

    const showInProgressGuest =
        !isEditing &&
        (
            currentGuestChoices.length > 0 ||
            getExtrasForGuest(currentGuest).length > 0 ||
            (isGuestBeingRebuilt(currentGuest) && currentMenu)
        );

    if (showInProgressGuest) {
        html += `<div class="mb-2 border-top pt-2">`;
        html += `<strong>Convive ${currentGuest} (en cours)</strong>`;

        if (currentMenu) {
            html += `<div class="text-muted small mb-1">${currentMenu.name}</div>`;
        }

        currentGuestChoices.forEach(c => {
            html += renderChoiceLine(currentGuest, c);
        });

        if (!renderedGuestExtras.has(currentGuest)) {
            getExtrasForGuest(currentGuest).forEach(extra => {
                html += renderExtraLine(currentGuest, extra);
            });
        }

        renderedGuestExtras.add(currentGuest);

        html += `</div>`;
    } else if (editingMenuRestart && guestSnapshotBeforeMenuEdit) {
        html += `<div class="mb-2 border-top pt-2">`;
        html += `<strong>Convive ${currentGuest} (en cours)</strong>`;
        html += `<div class="text-muted small">Choix du menu...</div>`;
        html += `</div>`;
    }

    for (let guestNumber = 1; guestNumber <= guestCount; guestNumber += 1) {
        if (renderedGuestExtras.has(guestNumber)) {
            continue;
        }

        const pendingExtras = getExtrasForGuest(guestNumber);

        if (!pendingExtras.length) {
            continue;
        }

        html += `<div class="mb-2 border-top pt-2">`;
        html += `<strong>Convive ${guestNumber}</strong>`;

        pendingExtras.forEach(extra => {
            html += renderExtraLine(guestNumber, extra);
        });

        html += `</div>`;
    }

    container.innerHTML = html || (
        wizardExtras.length > 0
            ? ""
            : `<p class="text-muted">Aucune commande</p>`
    );

    bindChoiceButtons(container);
    bindExtraButtons(container);
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
                guests: buildGuestsPayload()
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(data.error || "Erreur pendant l'envoi en cuisine");
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
    editingOriginalProductName = null;
}

function clearGuestRebuildState() {
    guestSnapshotBeforeMenuEdit = null;
    guestSnapshotBeforeFormulaEdit = null;
    allGuestsCompleteBeforeMenuEdit = false;
    allGuestsCompleteBeforeFormulaEdit = false;
    editingMenuRestart = false;
    editingFormulaRestart = false;
    editingGuestNumber = null;
    pendingSubChoice = null;
    isPickingSubChoice = false;
    currentMenu = null;
    hideMenuEditBackButton();
}

function resetCurrent() {
    currentGuestChoices = [];
    currentSectionIndex = 0;
    currentFormula = null;
}

function getExtrasForGuest(guestNumber) {
    return wizardExtras.filter(extra => extra.guest_number === guestNumber);
}

function getDefaultWizardExtraGuest() {
    return currentGuest;
}

function getExtraLineAmount(extra) {
    if (extra.source === "manual_extra") {
        return parsePriceAmount(extra.line_total);
    }

    const unitPrice = parsePriceAmount(extra.price);
    const quantity = Number(extra.quantity) || 1;

    return unitPrice * quantity;
}

function formatExtraDisplayLabel(extra) {
    if (extra.source === "manual_extra") {
        return extra.label;
    }

    const quantity = Number(extra.quantity) || 1;

    if (quantity > 1) {
        return `${quantity} × ${extra.product_name}`;
    }

    return extra.product_name;
}

function renderExtraLine(guestNumber, extra) {
    const amount = formatExtraAmount(getExtraLineAmount(extra));
    const destination = extra.source === "manual_extra"
        ? (extra.station === "bar" ? "Office" : "Cuisine")
        : "";

    return `
        <div class="d-flex justify-content-between align-items-start mb-1 gap-1 wizard-extra-line">
            <div class="text-muted small">
                Extra : ${formatExtraDisplayLabel(extra)} — ${amount}
                ${destination ? `<div class="text-muted smaller">${destination}</div>` : ""}
            </div>

            <div class="d-flex gap-1 flex-shrink-0">
                <button type="button"
                    class="btn btn-sm btn-outline-secondary edit-extra py-0 px-1"
                    data-id="${extra.temp_id}"
                    title="Modifier">
                    Modif.
                </button>
                <button type="button"
                    class="btn btn-sm btn-outline-danger delete-extra py-0 px-1"
                    data-id="${extra.temp_id}"
                    title="Supprimer">
                    Suppr.
                </button>
            </div>
        </div>
    `;
}

function renderExtraRecapLine(guestNumber, extra) {
    const amount = formatExtraAmount(getExtraLineAmount(extra));

    return `
        <div class="d-flex justify-content-between align-items-start mb-2">
            <div>
                <span>Extra : ${formatExtraDisplayLabel(extra)} — ${amount}</span>
            </div>

            <div class="d-flex gap-2">
                <button class="btn btn-sm btn-outline-secondary edit-extra"
                    data-id="${extra.temp_id}">
                    Modifier
                </button>
                <button class="btn btn-sm btn-outline-danger delete-extra"
                    data-id="${extra.temp_id}">
                    Supprimer
                </button>
            </div>
        </div>
    `;
}

function bindExtraButtons(root = document) {
    root.querySelectorAll(".edit-extra").forEach(btn => {
        btn.onclick = () => {
            openWizardExtraModal(parseInt(btn.dataset.id, 10));
        };
    });

    root.querySelectorAll(".delete-extra").forEach(btn => {
        btn.onclick = () => {
            deleteWizardExtra(parseInt(btn.dataset.id, 10));
        };
    });
}

function deleteWizardExtra(tempId) {
    if (!window.confirm("Supprimer cet extra ?")) {
        return;
    }

    wizardExtras = wizardExtras.filter(extra => extra.temp_id !== tempId);
    renderLiveTicket();

    if (!document.getElementById("recap").classList.contains("d-none")) {
        showRecap();
    }

    scheduleWizardDraftSave();
}

function buildGuestsPayload() {
    return guests.map(guest => ({
        ...guest,
        extras: getExtrasForGuest(guest.number).map(serializeWizardExtraForPayload)
    }));
}

function serializeWizardExtraForPayload(extra) {
    if (extra.source === "manual_extra") {
        return {
            source: "manual_extra",
            label: extra.label,
            line_total: String(extra.line_total),
            station: extra.station || "kitchen",
            vat_rate: String(extra.vat_rate || "10.00"),
        };
    }

    return {
        source: "extra",
        product_id: extra.product_id,
        product_name: extra.product_name,
        quantity: extra.quantity || 1,
        price: extra.price,
    };
}

function initWizardExtrasModal() {
    const addBtn = document.getElementById("wizardAddExtraBtn");
    if (!addBtn) return;

    addBtn.addEventListener("click", () => openWizardExtraModal());

    document.getElementById("addItemClose")?.addEventListener("click", closeWizardExtraModal);
    document.getElementById("addItemOverlay")?.addEventListener("click", closeWizardExtraModal);

    document.getElementById("addItemBackToCategories")?.addEventListener("click", () => {
        showWizardAddStep("addItemStepCategories");
    });

    document.getElementById("addItemBackToMode")?.addEventListener("click", () => {
        showWizardAddStep("addItemStepMode");
    });

    document.getElementById("addCatalogBtn")?.addEventListener("click", () => {
        showWizardAddStep("addItemStepCategories");
    });

    document.getElementById("addManualBtn")?.addEventListener("click", () => {
        resetWizardManualExtraForm();
        renderWizardManualGuestChoices();
        showWizardAddStep("addItemStepManual");
    });

    document.getElementById("addItemBackToProducts")?.addEventListener("click", () => {
        showWizardAddStep("addItemStepProducts");
    });

    document.getElementById("qtyMinus")?.addEventListener("click", () => {
        if (wizardSelectedQty > 1) {
            wizardSelectedQty--;
            updateWizardQty();
        }
    });

    document.getElementById("qtyPlus")?.addEventListener("click", () => {
        wizardSelectedQty++;
        updateWizardQty();
    });

    document.getElementById("confirmAddItem")?.addEventListener("click", confirmWizardCatalogExtra);
    document.getElementById("confirmManualExtra")?.addEventListener("click", confirmWizardManualExtra);
}

async function openWizardExtraModal(editTempId = null) {
    if (!wizardStarted) return;

    editingExtraTempId = editTempId || null;

    const title = document.getElementById("addItemTitle");
    if (title) {
        title.textContent = editTempId ? "Modifier l'extra" : "Ajouter un extra";
    }

    document.getElementById("addItemOverlay")?.classList.add("open");
    document.getElementById("addItemModal")?.classList.add("open");

    if (!wizardAddItemData) {
        const response = await fetch("/riad/api/products/categories/");
        wizardAddItemData = await response.json();
    }

    if (editTempId) {
        const extra = wizardExtras.find(item => item.temp_id === editTempId);
        if (!extra) {
            closeWizardExtraModal();
            return;
        }

        if (extra.source === "manual_extra") {
            document.getElementById("manualExtraLabel").value = extra.label || "";
            document.getElementById("manualExtraTotal").value = String(extra.line_total || "");
            document.getElementById("manualExtraStation").value = extra.station || "kitchen";
            document.getElementById("manualExtraVat").value = extra.vat_rate || "10.00";
            wizardManualSelectedGuest = extra.guest_number;
            renderWizardManualGuestChoices();
            showWizardAddStep("addItemStepManual");
            return;
        }

        wizardSelectedProduct = {
            id: extra.product_id,
            name: extra.product_name,
            price: extra.price,
        };
        wizardSelectedQty = extra.quantity || 1;
        wizardSelectedGuest = extra.guest_number;
        renderWizardAddConfirm();
        return;
    }

    wizardSelectedCategory = null;
    wizardSelectedProduct = null;
    wizardSelectedGuest = getDefaultWizardExtraGuest();
    wizardSelectedQty = 1;
    wizardManualSelectedGuest = getDefaultWizardExtraGuest();

    showWizardAddStep("addItemStepMode");
    renderWizardAddCategories();
}

function closeWizardExtraModal() {
    editingExtraTempId = null;
    document.getElementById("addItemOverlay")?.classList.remove("open");
    document.getElementById("addItemModal")?.classList.remove("open");
}

function showWizardAddStep(stepId) {
    document.querySelectorAll(".add-item-step").forEach(step => {
        step.classList.remove("active");
    });

    document.getElementById(stepId)?.classList.add("active");
}

function renderWizardAddCategories() {
    const container = document.getElementById("addItemCategories");
    if (!container) return;

    container.innerHTML = "";

    const groups = window.RIAD_ADD_GROUPS || [];

    groups.forEach(group => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "add-category-card";

        card.innerHTML = `
            <span class="material-symbols-outlined">${group.icon}</span>
            <strong>${group.name}</strong>
        `;

        card.addEventListener("click", () => {
            wizardSelectedCategory = group;
            renderWizardAddProducts(group);
        });

        container.appendChild(card);
    });
}

function renderWizardAddProducts(group) {
    const container = document.getElementById("addItemProducts");
    if (!container || !wizardAddItemData) return;

    container.innerHTML = "";
    document.getElementById("addItemCategoryTitle").textContent = group.name;

    const categories = wizardAddItemData.categories.filter(category =>
        group.categories.includes(category.name)
    );

    categories.forEach(category => {
        const title = document.createElement("div");
        title.className = "add-product-section-title";
        title.textContent = category.name;
        container.appendChild(title);

        category.products.forEach(product => {
            const card = document.createElement("button");
            card.type = "button";
            card.className = "add-product-card";

            card.innerHTML = `
                <strong>${product.name}</strong>
                <span>${product.price} €</span>
            `;

            card.addEventListener("click", () => {
                wizardSelectedProduct = product;
                wizardSelectedQty = 1;
                if (!editingExtraTempId) {
                    wizardSelectedGuest = currentGuest;
                }
                renderWizardAddConfirm();
            });

            container.appendChild(card);
        });
    });

    showWizardAddStep("addItemStepProducts");
}

function renderWizardAddConfirm() {
    if (!wizardSelectedProduct) return;

    document.getElementById("addItemProductTitle").textContent = wizardSelectedProduct.name;
    updateWizardQty();
    renderWizardGuestChoices("addItemGuests", wizardSelectedGuest);
    showWizardAddStep("addItemStepConfirm");
}

function updateWizardQty() {
    const qtyEl = document.getElementById("addItemQty");
    if (qtyEl) {
        qtyEl.textContent = wizardSelectedQty;
    }
}

function renderWizardGuestChoices(containerId, selectedValue) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = "";

    const tableChoice = document.createElement("button");
    tableChoice.type = "button";
    tableChoice.className = "guest-choice-card";
    tableChoice.dataset.guest = "table";
    tableChoice.textContent = "Toute la table";

    tableChoice.addEventListener("click", () => {
        if (containerId === "wizardManualGuests") {
            wizardManualSelectedGuest = "table";
        } else {
            wizardSelectedGuest = "table";
        }
        refreshWizardGuestSelection(containerId);
    });

    container.appendChild(tableChoice);

    for (let guestNumber = 1; guestNumber <= guestCount; guestNumber += 1) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "guest-choice-card";
        btn.dataset.guest = guestNumber;
        btn.textContent = `Convive ${guestNumber}`;

        btn.addEventListener("click", () => {
            if (containerId === "wizardManualGuests") {
                wizardManualSelectedGuest = guestNumber;
            } else {
                wizardSelectedGuest = guestNumber;
            }
            refreshWizardGuestSelection(containerId);
        });

        container.appendChild(btn);
    }

    refreshWizardGuestSelection(containerId, selectedValue);
}

function renderWizardManualGuestChoices() {
    renderWizardGuestChoices("wizardManualGuests", wizardManualSelectedGuest);
}

function refreshWizardGuestSelection(containerId, selectedValue = null) {
    const selected = selectedValue ?? (
        containerId === "wizardManualGuests"
            ? wizardManualSelectedGuest
            : wizardSelectedGuest
    );

    document.querySelectorAll(`#${containerId} .guest-choice-card`).forEach(btn => {
        btn.classList.remove("selected");

        if (btn.dataset.guest === "table" && selected === "table") {
            btn.classList.add("selected");
        }

        if (String(btn.dataset.guest) === String(selected)) {
            btn.classList.add("selected");
        }
    });
}

function resolveWizardGuestNumber(guestValue) {
    if (guestValue === "table") {
        return 1;
    }

    return parseInt(guestValue, 10);
}

function resetWizardManualExtraForm() {
    const labelInput = document.getElementById("manualExtraLabel");
    const totalInput = document.getElementById("manualExtraTotal");
    const stationInput = document.getElementById("manualExtraStation");
    const vatInput = document.getElementById("manualExtraVat");

    if (labelInput) labelInput.value = "";
    if (totalInput) totalInput.value = "";
    if (stationInput) stationInput.value = "kitchen";
    if (vatInput) vatInput.value = "10.00";

    if (!editingExtraTempId) {
        wizardManualSelectedGuest = currentGuest;
    }
}

function confirmWizardCatalogExtra() {
    if (!wizardSelectedProduct) return;

    const guestNumber = resolveWizardGuestNumber(wizardSelectedGuest);
    const extra = {
        temp_id: editingExtraTempId || wizardExtraTempId++,
        source: "extra",
        guest_number: guestNumber,
        product_id: wizardSelectedProduct.id,
        product_name: wizardSelectedProduct.name,
        price: wizardSelectedProduct.price,
        quantity: wizardSelectedQty,
    };

    upsertWizardExtra(extra);
    closeWizardExtraModal();
    renderLiveTicket();

    if (!document.getElementById("recap").classList.contains("d-none")) {
        showRecap();
    }
}

function confirmWizardManualExtra() {
    const label = document.getElementById("manualExtraLabel").value.trim();
    const lineTotal = document.getElementById("manualExtraTotal").value.trim();
    const station = document.getElementById("manualExtraStation").value;
    const vatRate = document.getElementById("manualExtraVat")?.value || "10.00";

    if (!label) {
        alert("L'intitulé est obligatoire.");
        return;
    }

    if (!lineTotal) {
        alert("Le prix total TTC est obligatoire.");
        return;
    }

    const amount = parsePriceAmount(lineTotal);

    if (amount <= 0) {
        alert("Le prix total TTC est obligatoire.");
        return;
    }

    const guestNumber = resolveWizardGuestNumber(wizardManualSelectedGuest);
    const extra = {
        temp_id: editingExtraTempId || wizardExtraTempId++,
        source: "manual_extra",
        guest_number: guestNumber,
        label,
        line_total: amount,
        station,
        vat_rate: vatRate,
    };

    upsertWizardExtra(extra);
    closeWizardExtraModal();
    renderLiveTicket();

    if (!document.getElementById("recap").classList.contains("d-none")) {
        showRecap();
    }
}

function upsertWizardExtra(extra) {
    const index = wizardExtras.findIndex(item => item.temp_id === extra.temp_id);

    if (index >= 0) {
        wizardExtras[index] = extra;
        scheduleWizardDraftSave();
        return;
    }

    wizardExtras.push(extra);
    scheduleWizardDraftSave();
}