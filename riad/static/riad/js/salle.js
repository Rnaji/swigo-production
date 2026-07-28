const SALLE_POLL_MS = 5000;

document.addEventListener("DOMContentLoaded", () => {
    initPaymentModal();
    refreshAllTables();

    if (!window._riadSalleLocalTimer) {
        window._riadSalleLocalTimer = setInterval(updateLocalTimers, 1000);
    }
    if (!window._riadSallePollTimer) {
        window._riadSallePollTimer = setInterval(refreshAllTablesIfVisible, SALLE_POLL_MS);
    }
    if (!window._riadSalleTasksListener) {
        window._riadSalleTasksListener = true;
        window.addEventListener("riad:tasks-updated", async () => {
            await refreshAllTables();
            if (selectedTableNumero) {
                const cached = tableState[selectedTableNumero];
                if (cached) {
                    renderDrawerFromState(selectedTableNumero);
                } else {
                    await openDrawer(selectedTableNumero);
                }
            }
        });
    }

    document.addEventListener("visibilitychange", () => {
        if (!document.hidden) {
            refreshAllTables();
        }
    });

    document.querySelectorAll(".table-card").forEach(card => {
        card.addEventListener("click", () => {
            openDrawer(card.dataset.tableNumero);
        });
    });

    document.querySelectorAll("#tableDrawer .drawer-close").forEach(btn => {
        btn.addEventListener("click", closeDrawer);
    });
    document.getElementById("drawerOverlay")?.addEventListener("click", closeDrawer);

    document.getElementById("drawerAddItem")?.addEventListener("click", openAddItemModal);
    document.getElementById("drawerCoversMinus")?.addEventListener("click", () => {
        const current = parseInt(document.getElementById("drawerCoversCount")?.textContent || "0", 10);
        updateCoversCount(Math.max(current - 1, 0));
    });
    document.getElementById("drawerCoversPlus")?.addEventListener("click", () => {
        const current = parseInt(document.getElementById("drawerCoversCount")?.textContent || "0", 10);
        updateCoversCount(current + 1);
    });
    document.getElementById("addItemClose")?.addEventListener("click", closeAddItemModal);
    document.getElementById("addItemOverlay")?.addEventListener("click", closeAddItemModal);

    document.getElementById("addItemBackToCategories")?.addEventListener("click", () => {
        showAddStep("addItemStepCategories");
    });

    document.getElementById("addItemBackToMode")?.addEventListener("click", () => {
        showAddStep("addItemStepMode");
    });

    document.getElementById("addCatalogBtn")?.addEventListener("click", () => {
        showAddStep("addItemStepCategories");
    });

    document.getElementById("addManualBtn")?.addEventListener("click", () => {
        resetManualExtraForm();
        showAddStep("addItemStepManual");
    });

    document.getElementById("confirmManualExtra")?.addEventListener("click", confirmManualExtra);

    document.getElementById("addItemBackToProducts")?.addEventListener("click", () => {
        showAddStep("addItemStepProducts");
    });

    document.getElementById("qtyMinus")?.addEventListener("click", () => {
        if (selectedQty > 1) {
            selectedQty--;
            updateQty();
        }
    });

    document.getElementById("qtyPlus")?.addEventListener("click", () => {
        selectedQty++;
        updateQty();
    });

    document.getElementById("confirmAddItem")?.addEventListener("click", confirmAddItem);
});

const tableState = {};
let selectedTableNumero = null;
let isNextStepLoading = false;

let addItemData = null;
let selectedCategory = null;
let selectedProduct = null;
let selectedGuest = "table";
let selectedQty = 1;

const ADD_GROUPS = window.RIAD_ADD_GROUPS || [
    { name: "Boissons", icon: "local_bar", categories: ["Boisson", "Eau", "Jus"] },
    { name: "Mocktails", icon: "local_bar", categories: ["Mocktail"] },
    { name: "Desserts", icon: "icecream", categories: ["Dessert"] },
    { name: "Coupes glacées", icon: "icecream", categories: ["Coupe glacée"] },
    { name: "Thé / Café", icon: "local_cafe", categories: ["Thé / Café"] },
];

async function refreshAllTablesIfVisible() {
    if (document.hidden) {
        return;
    }
    await refreshAllTables();
}

async function refreshAllTables() {
    const response = await fetch("/riad/api/salle/");
    const data = await response.json();

    data.tables.forEach(table => {
        tableState[table.numero] = table;
        updateTableCard(table);
    });

}

function updateTableCard(table) {
    const card = document.getElementById(`table-${table.numero}`);
    if (!card) return;

    card.querySelector(".table-time").textContent = table.elapsed_text || "";
    card.querySelector(".table-icon").textContent = table.icon || "table_restaurant";
    card.querySelector(".table-action").textContent = table.action || table.label || "Libre";

    const progress = Math.min(table.progress || 0, 100);
    card.querySelector(".progress-bar").style.width = `${progress}%`;

    card.classList.remove("normal", "warning", "danger", "none", "selected");
    card.classList.add(table.alert || "none");

    if (String(selectedTableNumero) === String(table.numero)) {
        card.classList.add("selected");
    }
}

function updateLocalTimers() {
    Object.keys(tableState).forEach(numero => {
        const table = tableState[numero];

        if (!table.target_seconds) return;
        if (table.status === "free" || table.status === "reserved") return;

        table.elapsed_seconds += 1;
        table.elapsed_text = formatSeconds(table.elapsed_seconds);
        table.progress = Math.round((table.elapsed_seconds / table.target_seconds) * 100);
        table.alert = getAlertLevel(table.elapsed_seconds, table.target_seconds);

        updateTableCard(table);

        if (String(selectedTableNumero) === String(numero)) {
            updateDrawerTimer(table);
        }
    });
}

async function openDrawer(numero, existingData = null) {
    selectedTableNumero = numero;

    const data = existingData || await (async () => {
        const response = await fetch(`/riad/api/table/${numero}/details/`);
        return response.json();
    })();

    tableState[data.numero] = data;

    updateTableCard(data);
    renderDrawer(data);

    document.getElementById("tableDrawer").classList.add("open");
    document.getElementById("drawerOverlay").classList.add("open");
}

function renderDrawerFromState(numero) {
    const data = tableState[numero];
    if (!data) {
        return;
    }
    renderDrawer(data);
}

function closeDrawer() {
    document.getElementById("tableDrawer").classList.remove("open");
    document.getElementById("drawerOverlay").classList.remove("open");

    selectedTableNumero = null;

    document.querySelectorAll(".table-card").forEach(card => {
        card.classList.remove("selected");
    });
}

function renderDrawer(data) {
    document.getElementById("drawerRoom").textContent = data.room || "";
    document.getElementById("drawerTitle").textContent = `Table ${data.numero}`;
    document.getElementById("drawerAction").textContent = data.action || data.label || "Libre";
    document.getElementById("drawerTime").textContent = data.elapsed_text || "--";

    const progress = Math.min(data.progress || 0, 100);
    document.getElementById("drawerProgressBar").style.width = `${progress}%`;

    const addButton = document.getElementById("drawerAddItem");
    if (addButton) {
        addButton.style.display = data.status === "free" ? "none" : "flex";
    }

    renderTimeline(data.timeline || []);
    renderCurrentAction(data.next_action, data);
    renderCoversControl(data);
    renderPaymentPanel(data);
    renderOrderDetails(data.order);

    colorDrawer(data.alert);
}



function updateDrawerTimer(table) {
    document.getElementById("drawerTime").textContent = table.elapsed_text || "--";

    const progress = Math.min(table.progress || 0, 100);
    document.getElementById("drawerProgressBar").style.width = `${progress}%`;

    colorDrawer(table.alert);
}

function renderTimeline(timeline) {
    const container = document.getElementById("drawerTimeline");
    container.innerHTML = "";

    if (!timeline || timeline.length === 0) {
        container.innerHTML = `<div class="empty-state">Aucune progression.</div>`;
        return;
    }

    timeline.forEach(step => {
        const item = document.createElement("div");
        item.className = `timeline-step ${step.state}`;
        item.title = step.label;

        item.innerHTML = `
            <div class="timeline-icon">
                <span class="material-symbols-outlined">${step.icon}</span>
            </div>
        `;

        container.appendChild(item);
    });
}

function renderCurrentAction(action, tableData = null) {
    const container = document.getElementById("drawerCurrentAction");
    container.innerHTML = "";

    if (!action) {
        container.innerHTML = `<div class="empty-state">Aucune action.</div>`;
        return;
    }

    const actionCard = document.createElement("div");
    actionCard.className = "next-action-card";

    let html = `
        <div class="next-action-label">À faire maintenant</div>

        <div class="next-action-title">
            <span class="material-symbols-outlined">${getActionIcon(action)}</span>
            <strong>${action.title || "Action suivante"}</strong>
        </div>
    `;

    if (action.items && action.items.length > 0) {
        html += `<div class="next-action-products">`;

        action.items.forEach(section => {
            html += `
                <div class="next-action-section">
                    <h4>${getSectionIcon(section.section)} ${section.section}</h4>
            `;

            section.items.forEach(item => {
                html += `
                    <div class="next-product-line">
                        <strong>${item.quantity} ×</strong>
                        <span>${item.name}</span>
                    </div>
                `;
            });

            html += `</div>`;
        });

        html += `</div>`;
    }

    if (action.served_items && action.served_items.length > 0) {
        html += `<div class="served-items-block">`;
        html += `<div class="served-items-title">Sur la table</div>`;

        action.served_items.forEach(section => {
            html += `
                <div class="next-action-section">
                    <h4>${getSectionIcon(section.section)} ${section.section}</h4>
            `;

            section.items.forEach(item => {
                html += `
                    <div class="next-product-line">
                        <strong>${item.quantity} ×</strong>
                        <span>${item.name}</span>
                    </div>
                `;
            });

            html += `</div>`;
        });

        html += `</div>`;
    }

    if (action.type !== "open_pre_ticket" && action.type !== "wait") {
        html += `
            <button class="drawer-btn primary next-action-button" id="drawerNextStep">
                ${action.button || "Valider"}
            </button>
        `;
    }

    if (
        tableData?.order?.exists &&
        tableData.order.is_sent_to_kitchen &&
        !["free", "paid"].includes(tableData.status)
    ) {
        html += `
            <a class="drawer-btn secondary next-action-button"
               href="/riad/table/${tableData.numero}/commande/?mode=add_guest">
                + Ajouter un client
            </a>
        `;
    }

    actionCard.innerHTML = html;
    container.appendChild(actionCard);

    const nextBtn = document.getElementById("drawerNextStep");
    if (!nextBtn) {
        return;
    }

    if (action.type === "open_commande") {
        nextBtn.addEventListener("click", openCommandeWizard);
    } else {
        nextBtn.addEventListener("click", nextStep);
    }
}

function getActionIcon(action) {
    const title = (action.title || "").toLowerCase();

    if (title.includes("boisson")) return "local_bar";
    if (title.includes("entrée")) return "restaurant_menu";
    if (title.includes("plat")) return "restaurant";
    if (title.includes("dessert")) return "icecream";
    if (title.includes("thé") || title.includes("café")) return "local_cafe";
    if (title.includes("addition") || title.includes("encaiss")) return "payments";
    if (title.includes("débarrasser")) return "cleaning_services";
    if (title.includes("commande")) return "edit_note";
    if (title.includes("installer")) return "table_restaurant";

    return "touch_app";
}

function getSectionIcon(section) {
    const name = (section || "").toLowerCase();

    if (name.includes("mocktail")) return "🍹";
    if (name.includes("boisson")) return "🥤";
    if (name.includes("eau")) return "💧";
    if (name.includes("entrée")) return "🥗";
    if (name.includes("plat")) return "🍽️";
    if (name.includes("dessert")) return "🍰";
    if (name.includes("thé") || name.includes("café")) return "☕";

    return "•";
}

function formatMoney(amount) {
    return `${Number(amount || 0).toFixed(2).replace(".", ",")} €`;
}

function renderCoversControl(data) {
    const block = document.getElementById("drawerCoversBlock");
    const countEl = document.getElementById("drawerCoversCount");

    if (!block || !countEl) {
        return;
    }

    const order = data.order;

    if (!order?.exists || data.status === "free") {
        block.classList.add("d-none");
        return;
    }

    block.classList.remove("d-none");
    countEl.textContent = String(order.guests_count ?? 0);
}

async function updateCoversCount(newCount) {
    if (!selectedTableNumero || newCount < 0) {
        return;
    }

    const response = await fetch(`/riad/api/table/${selectedTableNumero}/covers/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ guests_count: newCount }),
    });

    if (!response.ok) {
        return;
    }

    const data = await response.json();
    tableState[data.numero] = data;
    updateTableCard(data);
    renderDrawer(data);
}

function renderOrderDetails(order) {
    const container = document.getElementById("drawerOrder");
    container.innerHTML = "";

    if (!order || !order.exists) {
        container.innerHTML = `<div class="empty-state">Aucune commande.</div>`;
        return;
    }

    order.guests.forEach(guest => {
        const guestEl = document.createElement("div");
        guestEl.className = "guest-card";

        const paidBadge = guest.is_paid
            ? `<span class="guest-paid-badge">Payé</span>`
            : "";

        let html = `
            <div class="guest-card-header">
                <strong>Client ${guest.guest_number}</strong>
                ${paidBadge}
            </div>
        `;

        if (guest.menu) {
            html += `
                <div class="guest-menu-line">
                    ${guest.menu} — ${formatMoney(guest.menu_price)}
                </div>
            `;
        } else {
            html += `<div class="guest-menu">${guest.menu || "Sans menu"}</div>`;
        }

        html += `<div class="order-detail-lines">`;

        guest.choices.forEach(choice => {
            html += renderOrderChoiceLine(choice);
        });

        html += `</div>`;

        html += `
            <div class="guest-card-total">
                Total du client ${formatMoney(guest.total)}
            </div>
        `;

        guestEl.innerHTML = html;
        container.appendChild(guestEl);
    });

    if (order.table_extras && order.table_extras.length > 0) {
        const tableExtrasEl = document.createElement("div");
        tableExtrasEl.className = "guest-card table-extras-card";

        let html = `
            <strong>Extras de la table</strong>
            <div class="order-detail-lines">
        `;

        order.table_extras.forEach(choice => {
            html += renderOrderChoiceLine(choice);
        });

        html += `
            </div>
            <div class="guest-card-total table-extras-total">
                Total extras de la table ${formatMoney(order.table_extras_total)}
            </div>
        `;

        tableExtrasEl.innerHTML = html;
        container.appendChild(tableExtrasEl);
    }

    const summaryEl = document.createElement("div");
    summaryEl.className = "order-billing-summary";
    summaryEl.innerHTML = `
        <div class="order-billing-line">
            <span>Total convives</span>
            <strong>${formatMoney(order.guests_total)}</strong>
        </div>
        ${Number(order.table_extras_total || 0) > 0 ? `
            <div class="order-billing-line">
                <span>Extras de la table</span>
                <strong>${formatMoney(order.table_extras_total)}</strong>
            </div>
        ` : ""}
        <div class="order-billing-grand-total">
            <span>TOTAL GÉNÉRAL</span>
            <strong>${formatMoney(order.total)}</strong>
        </div>
    `;
    container.appendChild(summaryEl);

    container.querySelectorAll(".delete-choice-btn").forEach(button => {
        button.addEventListener("click", () => {
            deleteOrderChoice(parseInt(button.dataset.choiceId, 10));
        });
    });
}

function getOrderDetailCategory(choice) {
    if (choice.source === "extra" || choice.source === "manual_extra") {
        return "EXTRA";
    }

    return (choice.section || "—").toUpperCase();
}

function getOrderDetailProductName(choice) {
    let name = choice.product || "";

    if (choice.source === "replacement") {
        name = `Remplacement par ${name}`;
    } else if (choice.source === "extra") {
        name = `Extra : ${name}`;
    } else if (choice.source === "manual_extra") {
        name = `Supplément libre — ${name}`;
    }

    if (choice.quantity > 1 && choice.source !== "manual_extra") {
        return `${choice.quantity} × ${name}`;
    }

    return name;
}

function formatOrderDetailPrice(choice) {
    if (choice.source === "menu" || choice.source === "offered") {
        return "";
    }

    const amount = Number(choice.line_amount) || 0;

    if (amount <= 0) {
        return "";
    }

    if (choice.source === "replacement") {
        return `+${amount.toFixed(2)} €`;
    }

    return `${amount.toFixed(2)} €`;
}

function renderOrderChoiceLine(choice) {
    const category = getOrderDetailCategory(choice);
    const productName = getOrderDetailProductName(choice);
    const price = formatOrderDetailPrice(choice);
    const deletable =
        (choice.source === "extra" || choice.source === "manual_extra") && choice.id;

    const replacementNote =
        choice.source === "replacement" && choice.replaced_product_name
            ? `<div class="order-detail-sub">↳ remplace ${choice.replaced_product_name}</div>`
            : "";

    return `
        <div class="order-detail-line">
            <span class="order-detail-cat">${category}</span>
            <div class="order-detail-content">
                <div class="order-detail-main">
                    <span class="order-detail-name">${productName}</span>
                    <span class="order-detail-end">
                        ${price ? `<span class="order-detail-price">${price}</span>` : ""}
                        ${deletable ? `
                            <button type="button"
                                class="order-detail-delete delete-choice-btn"
                                data-choice-id="${choice.id}"
                                title="Supprimer"
                                aria-label="Supprimer">×</button>
                        ` : ""}
                    </span>
                </div>
                ${replacementNote}
            </div>
        </div>
    `;
}

function colorDrawer(alert) {
    const drawer = document.getElementById("tableDrawer");
    drawer.classList.remove("normal", "warning", "danger", "none");
    drawer.classList.add(alert || "none");
}

async function nextStep() {
    if (!selectedTableNumero) return;
    if (isNextStepLoading) return;

    isNextStepLoading = true;

    const button = document.getElementById("drawerNextStep");
    if (button) {
        button.disabled = true;
        button.textContent = "Validation...";
    }

    const response = await fetch(`/riad/api/table/${selectedTableNumero}/next/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
    });

    const data = await response.json();

    tableState[data.numero] = data;
    updateTableCard(data);

    isNextStepLoading = false;

    await openDrawer(data.numero, data);

    if (data.status === "ordering") {
        window.location.href = `/riad/table/${data.numero}/commande/`;
    }
}

function openCommandeWizard() {
    if (!selectedTableNumero) return;
    window.location.href = `/riad/table/${selectedTableNumero}/commande/`;
}

async function openAddItemModal() {
    if (!selectedTableNumero) return;

    document.getElementById("addItemTitle").textContent =
        `Ajouter — Table ${selectedTableNumero}`;

    document.getElementById("addItemOverlay").classList.add("open");
    document.getElementById("addItemModal").classList.add("open");

    selectedCategory = null;
    selectedProduct = null;
    selectedGuest = "table";
    selectedQty = 1;

    showAddStep("addItemStepMode");

    const container = document.getElementById("addItemCategories");
    container.innerHTML = "Chargement...";

    const response = await fetch("/riad/api/products/categories/");
    addItemData = await response.json();

    renderAddCategories();
}

function closeAddItemModal() {
    document.getElementById("addItemOverlay").classList.remove("open");
    document.getElementById("addItemModal").classList.remove("open");
}

function showAddStep(stepId) {
    document.querySelectorAll(".add-item-step").forEach(step => {
        step.classList.remove("active");
    });

    document.getElementById(stepId).classList.add("active");
}

function renderAddCategories() {
    const container = document.getElementById("addItemCategories");
    container.innerHTML = "";

    ADD_GROUPS.forEach(group => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "add-category-card";

        card.innerHTML = `
            <span class="material-symbols-outlined">${group.icon}</span>
            <strong>${group.name}</strong>
        `;

        card.addEventListener("click", () => {
            selectedCategory = group;
            renderAddProducts(group);
        });

        container.appendChild(card);
    });
}

function renderAddProducts(group) {
    const container = document.getElementById("addItemProducts");
    container.innerHTML = "";

    document.getElementById("addItemCategoryTitle").textContent = group.name;

    const categories = addItemData.categories.filter(category =>
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
                selectedProduct = product;
                selectedQty = 1;
                selectedGuest = "table";
                renderAddConfirm();
            });

            container.appendChild(card);
        });
    });

    showAddStep("addItemStepProducts");
}

function resetManualExtraForm() {
    const labelInput = document.getElementById("manualExtraLabel");
    const totalInput = document.getElementById("manualExtraTotal");
    const stationInput = document.getElementById("manualExtraStation");
    const vatInput = document.getElementById("manualExtraVat");

    if (labelInput) labelInput.value = "";
    if (totalInput) totalInput.value = "";
    if (stationInput) stationInput.value = "kitchen";
    if (vatInput) vatInput.value = "10.00";
}

async function confirmManualExtra() {
    if (!selectedTableNumero) return;

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

    const response = await fetch(
        `/riad/api/table/${selectedTableNumero}/add-manual-extra/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                label,
                line_total: lineTotal,
                station,
                vat_rate: vatRate,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Impossible d'ajouter le supplément libre.");
        return;
    }

    closeAddItemModal();
    await openDrawer(selectedTableNumero);
}

async function deleteOrderChoice(choiceId) {
    if (!selectedTableNumero) return;

    if (!window.confirm("Supprimer cette ligne de la commande ?")) {
        return;
    }

    const response = await fetch(
        `/riad/api/table/${selectedTableNumero}/choice/${choiceId}/delete/`,
        {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
        }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Suppression impossible.");
        return;
    }

    await openDrawer(selectedTableNumero);
}

function renderAddConfirm() {
    document.getElementById("addItemProductTitle").textContent = selectedProduct.name;

    updateQty();
    showAddStep("addItemStepConfirm");
}

function updateQty() {
    document.getElementById("addItemQty").textContent = selectedQty;
}

function renderGuestChoices() {
    const container = document.getElementById("addItemGuests");
    container.innerHTML = "";

    const tableChoice = document.createElement("button");
    tableChoice.type = "button";
    tableChoice.className = "guest-choice-card selected";
    tableChoice.textContent = "Toute la table";

    tableChoice.addEventListener("click", () => {
        selectedGuest = "table";
        refreshGuestSelection();
    });

    container.appendChild(tableChoice);

    const order = tableState[selectedTableNumero]?.order;

    if (!order || !order.exists) return;

    order.guests.forEach(guest => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "guest-choice-card";
        btn.dataset.guest = guest.guest_number;
        btn.textContent = `Client ${guest.guest_number}`;

        btn.addEventListener("click", () => {
            selectedGuest = guest.guest_number;
            refreshGuestSelection();
        });

        container.appendChild(btn);
    });
}

function refreshGuestSelection() {
    document.querySelectorAll(".guest-choice-card").forEach(btn => {
        btn.classList.remove("selected");

        if (btn.textContent === "Toute la table" && selectedGuest === "table") {
            btn.classList.add("selected");
        }

        if (String(btn.dataset.guest) === String(selectedGuest)) {
            btn.classList.add("selected");
        }
    });
}

async function confirmAddItem() {
    if (!selectedTableNumero || !selectedProduct) return;

    const response = await fetch(`/riad/api/table/${selectedTableNumero}/add-item/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            product_id: selectedProduct.id,
            quantity: selectedQty,
        }),
    });

    if (!response.ok) {
        alert("Erreur lors de l'ajout.");
        return;
    }

    closeAddItemModal();
    await openDrawer(selectedTableNumero);
}

function formatSeconds(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function getAlertLevel(elapsed, target) {
    if (!target) return "none";

    const ratio = elapsed / target;

    if (ratio < 0.75) return "normal";
    if (ratio < 1) return "warning";
    return "danger";
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
}


function paymentMethodShortLabel(method) {
    if (method === "card") return "💳 CB";
    if (method === "cash") return "💶 Espèces";
    return method;
}

function renderPaymentPanel(data) {
    const container = document.getElementById("drawerPayment");
    if (!container) return;

    container.innerHTML = "";

    if (data.status !== "bill_requested" && data.status !== "paid") {
        return;
    }

    if (!data.order || !data.order.exists) {
        container.innerHTML = `<div class="empty-state">Aucune addition.</div>`;
        return;
    }

    const total = Number(data.order.total || 0);
    const paid = Number(data.order.paid || 0);
    const remaining = Math.max(Number(data.order.remaining || 0), 0);
    const payments = data.order.payments || [];
    const preTicketUrl = `/riad/table/${data.id}/pre-ticket/`;

    let html = `
        <div class="payment-panel">

            <div class="payment-title">
                📄 Récapitulatif non fiscal
            </div>

            <p class="payment-disclaimer">
                Document interne — le ticket officiel est émis par la caisse homologuée.
            </p>

            <a href="${preTicketUrl}" class="drawer-btn primary pre-ticket-link-btn">
                Voir / Imprimer le pré-ticket
            </a>

            <div class="payment-summary">
                <div>
                    <span>Total indicatif</span>
                    <strong>${total.toFixed(2)} €</strong>
                </div>

                <div>
                    <span>Suivi interne</span>
                    <strong>${paid.toFixed(2)} €</strong>
                </div>

                <div class="payment-remaining">
                    <span>Reste indicatif</span>
                    <strong id="drawerRemaining">${remaining.toFixed(2)} €</strong>
                </div>
            </div>
    `;

    if (payments.length > 0) {
        html += `
            <div class="payment-history">
                <h4>Suivi interne (non fiscal)</h4>
        `;

        payments.forEach(payment => {
            const guestLabel = payment.guest_number
                ? ` — Client ${payment.guest_number}`
                : "";
            const deleteBtn = data.status !== "paid" && payment.id
                ? `<button type="button" class="payment-delete-btn" onclick="confirmDeleteInternalPayment(${payment.id})" aria-label="Supprimer ce paiement">✕</button>`
                : "";
            html += `
                <div class="payment-history-line">
                    <span class="payment-history-label">${paymentMethodShortLabel(payment.method)}${guestLabel}</span>
                    <strong class="payment-history-amount">${Number(payment.amount).toFixed(2).replace(".", ",")} €</strong>
                    ${deleteBtn}
                </div>
            `;
        });

        html += `</div>`;
    }

    if (data.status === "paid") {
        html += `
            <div class="payment-finished">
                ✅ Paiement enregistré dans la caisse homologuée
            </div>

            <button class="drawer-btn primary" onclick="freeTableAfterPayment()">
                Libérer la table
            </button>
        `;
    } else {
        if (remaining > 0) {
            html += `
                <div class="payment-tracking-label">Répartition interne (non fiscal)</div>
                <div class="payment-buttons-drawer">
                    <button type="button" onclick="openDrawerCardPayment(${remaining})">
                        💳 Suivi CB
                    </button>

                    <button type="button" onclick="openDrawerCashPayment(${remaining})">
                        💶 Suivi espèces
                    </button>
                </div>

                <div id="drawerPaymentForm"></div>
            `;
        }

        html += `
            <button class="drawer-btn primary mark-paid-external-btn" onclick="markPaidInExternalCashier()">
                Paiement enregistré dans la caisse homologuée
            </button>
        `;
    }

    html += `</div>`;

    container.innerHTML = html;
}

function openDrawerCardPayment(remaining) {
    openPaymentModal({
        method: "card",
        remaining,
        title: "Suivi interne — CB",
        amountLabel: "Montant suivi (indicatif)",
        fullButtonLabel: "Tout le reste indicatif",
        onSubmit: submitDrawerSinglePayment,
    });
}

function openDrawerCashPayment(remaining) {
    openPaymentModal({
        method: "cash",
        remaining,
        title: "Suivi interne — Espèces",
        amountLabel: "Montant suivi (indicatif)",
        fullButtonLabel: "Tout le reste indicatif",
        onSubmit: submitDrawerSinglePayment,
    });
}

async function submitDrawerSinglePayment({ method, amount }) {
    return sendDrawerPayment([{ method, amount }]);
}

async function sendDrawerPayment(payments) {
    const order = tableState[selectedTableNumero]?.order;

    if (!order || !order.exists) {
        alert("Aucune commande.");
        return false;
    }

    const response = await fetch("/riad/api/payment/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            order_id: order.id,
            payments: payments
        }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Erreur paiement.");
        return false;
    }

    await openDrawer(selectedTableNumero);
    return true;
}

function confirmDeleteInternalPayment(paymentId) {
    openPaymentDeleteConfirm({
        onConfirm: () => deleteInternalPayment(paymentId),
    });
}

async function deleteInternalPayment(paymentId) {
    const response = await fetch(`/riad/api/payment/${paymentId}/delete/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Impossible de supprimer ce paiement.");
        return false;
    }

    await openDrawer(selectedTableNumero);
    return true;
}

async function markPaidInExternalCashier() {
    if (!selectedTableNumero) return;

    const confirmed = window.confirm(
        "Confirmer que le paiement a été saisi dans la caisse homologuée ?\n\n" +
        "Cette action marque la commande comme réglée dans Riad.\n" +
        "Aucun ticket fiscal ne sera généré ici."
    );

    if (!confirmed) return;

    const response = await fetch(
        `/riad/api/table/${selectedTableNumero}/mark-paid-external/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({}),
        }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Impossible de marquer la commande comme réglée.");
        return;
    }

    await openDrawer(selectedTableNumero);
}

async function freeTableAfterPayment() {
    await nextStep();
}
