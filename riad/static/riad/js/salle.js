document.addEventListener("DOMContentLoaded", () => {
    refreshAllTables();

    setInterval(updateLocalTimers, 1000);

    document.querySelectorAll(".table-card").forEach(card => {
        card.addEventListener("click", () => {
            openDrawer(card.dataset.tableNumero);
        });
    });

    document.getElementById("drawerClose")?.addEventListener("click", closeDrawer);
    document.getElementById("drawerOverlay")?.addEventListener("click", closeDrawer);

    document.getElementById("drawerAddItem")?.addEventListener("click", openAddItemModal);
    document.getElementById("addItemClose")?.addEventListener("click", closeAddItemModal);
    document.getElementById("addItemOverlay")?.addEventListener("click", closeAddItemModal);

    document.getElementById("addItemBackToCategories")?.addEventListener("click", () => {
        showAddStep("addItemStepCategories");
    });

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

const ADD_GROUPS = [
    { name: "Plat", icon: "restaurant", categories: ["Plat", "Supplément"] },
    { name: "Entrée", icon: "restaurant_menu", categories: ["Entrée"] },
    { name: "Dessert", icon: "icecream", categories: ["Dessert"] },
    { name: "Boisson", icon: "local_bar", categories: ["Boisson", "Eau"] },
    { name: "Mocktail", icon: "local_bar", categories: ["Mocktail"] },
    { name: "Thé / Café", icon: "local_cafe", categories: ["Thé / Café"] },
];

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

async function openDrawer(numero) {
    selectedTableNumero = numero;

    const response = await fetch(`/riad/api/table/${numero}/details/`);
    const data = await response.json();

    tableState[data.numero] = data;

    updateTableCard(data);
    renderDrawer(data);

    document.getElementById("tableDrawer").classList.add("open");
    document.getElementById("drawerOverlay").classList.add("open");
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
    renderCurrentAction(data.next_action);
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

function renderCurrentAction(action) {
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

    html += `
        <button class="drawer-btn primary next-action-button" id="drawerNextStep">
            ${action.button || "Valider"}
        </button>
    `;

    actionCard.innerHTML = html;
    container.appendChild(actionCard);

    document.getElementById("drawerNextStep").addEventListener("click", nextStep);
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

        let html = `
            <strong>Client ${guest.guest_number}</strong>
            <div class="guest-menu">${guest.menu || "Sans menu"}</div>
        `;

        guest.choices.forEach(choice => {
            html += `
                <div class="choice-line">
                    <span class="choice-section">${choice.section}</span>
                    ${choice.quantity} × ${choice.product}
                </div>
            `;
        });

        guestEl.innerHTML = html;
        container.appendChild(guestEl);
    });
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

    await openDrawer(data.numero);

    if (data.status === "ordering") {
        window.location.href = `/riad/table/${data.numero}/commande/`;
    }
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

    showAddStep("addItemStepCategories");

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

function renderAddConfirm() {
    document.getElementById("addItemProductTitle").textContent = selectedProduct.name;

    updateQty();
    renderGuestChoices();

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
            guest_number: selectedGuest,
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

    let html = `
        <div class="payment-panel">

            <div class="payment-title">
                💰 Encaissement
            </div>

            <div class="payment-summary">
                <div>
                    <span>Total</span>
                    <strong>${total.toFixed(2)} €</strong>
                </div>

                <div>
                    <span>Déjà payé</span>
                    <strong>${paid.toFixed(2)} €</strong>
                </div>

                <div class="payment-remaining">
                    <span>Reste</span>
                    <strong id="drawerRemaining">${remaining.toFixed(2)} €</strong>
                </div>
            </div>
    `;

    if (payments.length > 0) {
        html += `
            <div class="payment-history">
                <h4>Historique</h4>
        `;

        payments.forEach(payment => {
            html += `
                <div class="payment-history-line">
                    <span>${payment.method_display}</span>
                    <strong>${Number(payment.amount).toFixed(2)} €</strong>
                </div>
            `;
        });

        html += `</div>`;
    }

    if (remaining <= 0) {
        html += `
            <div class="payment-finished">
                ✅ Paiement terminé
            </div>

            <button class="drawer-btn primary" onclick="freeTableAfterPayment()">
                Libérer la table
            </button>
        `;
    } else {
        html += `
            <div class="payment-buttons-drawer">
                <button type="button" onclick="drawerPayCard(${remaining})">
                    💳 Carte bancaire
                </button>

                <button type="button" onclick="showDrawerCash(${remaining})">
                    💶 Espèces
                </button>

                <button type="button" onclick="showDrawerMixed(${remaining})">
                    🔀 Mixte
                </button>
            </div>

            <div id="drawerPaymentForm"></div>
        `;
    }

    html += `</div>`;

    container.innerHTML = html;
}

function drawerPayCard(amount) {
    sendDrawerPayment([
        {
            method: "card",
            amount: amount
        }
    ]);
}

function showDrawerCash(remaining) {
    const form = document.getElementById("drawerPaymentForm");

    form.innerHTML = `
        <div class="drawer-payment-form">
            <h3>Paiement espèces</h3>

            <label>Le client donne</label>
            <input
                type="number"
                id="drawerCashGiven"
                step="0.01"
                min="0"
                oninput="calculateDrawerCash(${remaining})"
            >

            <p>Rendu : <strong id="drawerCashChange">0.00</strong> €</p>

            <button type="button" class="drawer-btn primary" onclick="validateDrawerCash(${remaining})">
                Valider espèces
            </button>
        </div>
    `;
}

function calculateDrawerCash(remaining) {
    const given = Number(document.getElementById("drawerCashGiven").value || 0);
    const change = Math.max(given - remaining, 0);

    document.getElementById("drawerCashChange").textContent = `${change.toFixed(2)} €`;
}

function validateDrawerCash(remaining) {
    const given = Number(document.getElementById("drawerCashGiven").value || 0);

    if (given < remaining) {
        alert("Montant insuffisant.");
        return;
    }

    sendDrawerPayment([
        {
            method: "cash",
            amount: remaining
        }
    ]);
}

function showDrawerMixed(remaining) {
    const form = document.getElementById("drawerPaymentForm");

    form.innerHTML = `
        <div class="drawer-payment-form">
            <h3>Paiement mixte</h3>

            <label>Carte bancaire</label>
            <input
                type="number"
                id="drawerMixedCard"
                step="0.01"
                min="0"
                oninput="calculateDrawerMixed(${remaining})"
            >

            <label>Espèces données</label>
            <input
                type="number"
                id="drawerMixedCash"
                step="0.01"
                min="0"
                oninput="calculateDrawerMixed(${remaining})"
            >

            <p>Espèces utilisées : <strong id="drawerMixedCashUsed">0.00 €</strong></p>
            <p>Rendu : <strong id="drawerMixedChange">0.00 €</strong></p>

            <button type="button" class="drawer-btn primary" onclick="validateDrawerMixed(${remaining})">
                Valider paiement mixte
            </button>
        </div>
    `;
}

function calculateDrawerMixed(remaining) {
    const card = Number(document.getElementById("drawerMixedCard").value || 0);
    const cashGiven = Number(document.getElementById("drawerMixedCash").value || 0);

    const cashNeeded = Math.max(remaining - card, 0);
    const cashUsed = Math.min(cashGiven, cashNeeded);
    const change = Math.max(cashGiven - cashNeeded, 0);

    document.getElementById("drawerMixedCashUsed").textContent = `${cashUsed.toFixed(2)} €`;
    document.getElementById("drawerMixedChange").textContent = `${change.toFixed(2)} €`;
}

function validateDrawerMixed(remaining) {
    const card = Number(document.getElementById("drawerMixedCard").value || 0);
    const cashGiven = Number(document.getElementById("drawerMixedCash").value || 0);

    const cashNeeded = Math.max(remaining - card, 0);
    const cashUsed = Math.min(cashGiven, cashNeeded);

    if (card + cashUsed < remaining) {
        alert("Montant insuffisant.");
        return;
    }

    const payments = [];

    if (card > 0) {
        payments.push({
            method: "card",
            amount: card
        });
    }

    if (cashUsed > 0) {
        payments.push({
            method: "cash",
            amount: cashUsed
        });
    }

    sendDrawerPayment(payments);
}

async function sendDrawerPayment(payments) {
    const order = tableState[selectedTableNumero]?.order;

    if (!order || !order.exists) {
        alert("Aucune commande.");
        return;
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

    if (!data.success) {
        alert(data.error || "Erreur paiement.");
        return;
    }

    await openDrawer(selectedTableNumero);
}

async function freeTableAfterPayment() {
    await nextStep();
}