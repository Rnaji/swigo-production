const PAYMENT_METHOD_LABELS = {
    card: "CB",
    cash: "espèces",
};

function formatPaymentAmount(amount) {
    return `${Number(amount).toFixed(2).replace(".", ",")} €`;
}

function ensurePaymentModal() {
    if (document.getElementById("paymentModalOverlay")) {
        return;
    }

    document.body.insertAdjacentHTML(
        "beforeend",
        `
        <div class="payment-modal-overlay" id="paymentModalOverlay" aria-hidden="true">
            <div class="payment-modal" role="dialog" aria-modal="true" aria-labelledby="paymentModalTitle">
                <h2 id="paymentModalTitle">Paiement</h2>
                <p class="payment-modal-remaining">
                    Reste à payer :
                    <strong id="paymentModalRemaining">0,00 €</strong>
                </p>

                <div class="payment-modal-actions" id="paymentModalChoices">
                    <button type="button" class="payment-modal-full" id="paymentModalFull">
                        Tout le reste
                    </button>
                    <button type="button" class="payment-modal-custom-trigger" id="paymentModalCustomTrigger">
                        Autre montant
                    </button>
                </div>

                <div class="payment-modal-custom-form" id="paymentModalCustomForm">
                    <label for="paymentModalAmount">Montant</label>
                    <input
                        type="number"
                        id="paymentModalAmount"
                        step="0.01"
                        min="0.01"
                        inputmode="decimal">
                    <button type="button" class="payment-modal-submit" id="paymentModalSubmit">
                        Valider
                    </button>
                    <div class="payment-modal-error" id="paymentModalError"></div>
                </div>

                <button type="button" class="payment-modal-cancel" id="paymentModalCancel">
                    Annuler
                </button>
            </div>
        </div>
        `
    );
}

const paymentModalState = {
    method: null,
    remaining: 0,
    onSubmit: null,
};

let paymentModalInitialized = false;

function closePaymentModal() {
    const overlay = document.getElementById("paymentModalOverlay");
    if (!overlay) return;

    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");

    document.getElementById("paymentModalCustomForm")?.classList.remove("open");
    document.getElementById("paymentModalError").textContent = "";

    const amountInput = document.getElementById("paymentModalAmount");
    if (amountInput) {
        amountInput.value = "";
    }
}

function updatePaymentModalSubmitLabel() {
    const submitBtn = document.getElementById("paymentModalSubmit");
    const amountInput = document.getElementById("paymentModalAmount");
    if (!submitBtn || !amountInput) return;

    const amount = parseFloat(String(amountInput.value).replace(",", ".")) || 0;
    const methodLabel = PAYMENT_METHOD_LABELS[paymentModalState.method] || "";

    if (amount > 0) {
        submitBtn.textContent = `Valider ${formatPaymentAmount(amount)} en ${methodLabel}`;
    } else {
        submitBtn.textContent = `Valider en ${methodLabel}`;
    }
}

function validatePaymentAmount(amount, remaining) {
    if (!Number.isFinite(amount) || amount <= 0) {
        return "Saisissez un montant valide.";
    }

    if (amount > remaining + 0.001) {
        return "Le montant ne peut pas dépasser le reste à payer.";
    }

    return "";
}

async function submitPaymentModalAmount(amount) {
    const errorEl = document.getElementById("paymentModalError");
    const error = validatePaymentAmount(amount, paymentModalState.remaining);

    if (error) {
        errorEl.textContent = error;
        return;
    }

    if (typeof paymentModalState.onSubmit !== "function") {
        return;
    }

    const submitBtn = document.getElementById("paymentModalSubmit");
    const fullBtn = document.getElementById("paymentModalFull");

    if (submitBtn) submitBtn.disabled = true;
    if (fullBtn) fullBtn.disabled = true;

    try {
        const success = await paymentModalState.onSubmit({
            method: paymentModalState.method,
            amount: Number(amount.toFixed(2)),
        });

        if (success) {
            closePaymentModal();
        }
    } finally {
        if (submitBtn) submitBtn.disabled = false;
        if (fullBtn) fullBtn.disabled = false;
    }
}

function openPaymentModal({
    method,
    remaining,
    onSubmit,
    prefillAmount = null,
    title = null,
    amountLabel = "Montant",
    fullButtonLabel = null,
}) {
    initPaymentModal();

    paymentModalState.method = method;
    paymentModalState.remaining = Number(remaining) || 0;
    paymentModalState.onSubmit = onSubmit;

    const defaultTitle = method === "card"
        ? "Carte bancaire"
        : "Espèces";

    document.getElementById("paymentModalTitle").textContent = title || defaultTitle;
    document.getElementById("paymentModalRemaining").textContent =
        formatPaymentAmount(paymentModalState.remaining);

    const amountLabelEl = document.querySelector('label[for="paymentModalAmount"]');
    if (amountLabelEl) {
        amountLabelEl.textContent = amountLabel;
    }

    document.getElementById("paymentModalFull").textContent =
        fullButtonLabel ||
        `Tout le reste — ${formatPaymentAmount(paymentModalState.remaining)}`;

    const customForm = document.getElementById("paymentModalCustomForm");
    customForm.classList.remove("open");

    const amountInput = document.getElementById("paymentModalAmount");
    const amountToPrefill = prefillAmount ?? paymentModalState.remaining;
    amountInput.value = Number(amountToPrefill || 0).toFixed(2);
    amountInput.max = paymentModalState.remaining.toFixed(2);
    updatePaymentModalSubmitLabel();

    document.getElementById("paymentModalError").textContent = "";

    const overlay = document.getElementById("paymentModalOverlay");
    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
}

function initPaymentModal() {
    ensurePaymentModal();

    if (paymentModalInitialized) {
        return;
    }

    paymentModalInitialized = true;

    document.getElementById("paymentModalCancel")?.addEventListener("click", closePaymentModal);
    document.getElementById("paymentModalOverlay")?.addEventListener("click", event => {
        if (event.target.id === "paymentModalOverlay") {
            closePaymentModal();
        }
    });

    document.getElementById("paymentModalFull")?.addEventListener("click", () => {
        submitPaymentModalAmount(paymentModalState.remaining);
    });

    document.getElementById("paymentModalCustomTrigger")?.addEventListener("click", () => {
        document.getElementById("paymentModalCustomForm")?.classList.add("open");
        document.getElementById("paymentModalAmount")?.focus();
        document.getElementById("paymentModalAmount")?.select();
    });

    document.getElementById("paymentModalAmount")?.addEventListener("input", updatePaymentModalSubmitLabel);

    document.getElementById("paymentModalSubmit")?.addEventListener("click", () => {
        const amount = parseFloat(
            String(document.getElementById("paymentModalAmount").value).replace(",", ".")
        );
        submitPaymentModalAmount(amount);
    });
}
