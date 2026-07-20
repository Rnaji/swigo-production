document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("btnTrackCard")?.addEventListener("click", () => {
        openOperationalPaymentModal("card");
    });

    document.getElementById("btnTrackCash")?.addEventListener("click", () => {
        openOperationalPaymentModal("cash");
    });

    document.getElementById("btnMarkPaidExternal")?.addEventListener("click", markPaidInExternalCashier);
});

function getCSRFToken() {
    const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookie ? cookie.split("=")[1] : "";
}

function openOperationalPaymentModal(method) {
    const remaining = Number(window.RIAD_PRE_TICKET?.remaining || 0);

    if (remaining <= 0) {
        alert("Addition déjà réglée.");
        return;
    }

    openPaymentModal({
        method,
        remaining,
        title: method === "card" ? "Carte bancaire" : "Espèces",
        onSubmit: submitOperationalPayment,
    });
}

async function submitOperationalPayment({ method, amount }) {
    const response = await fetch("/riad/api/payment/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
            order_id: window.RIAD_PRE_TICKET.orderId,
            payments: [{ method, amount }],
            operational_only: true,
        }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Erreur paiement.");
        return false;
    }

    window.location.reload();
    return true;
}

async function markPaidInExternalCashier() {
    const confirmed = window.confirm(
        "Confirmer que le paiement a été enregistré ?"
    );

    if (!confirmed) {
        return;
    }

    const response = await fetch(
        `/riad/api/table/${window.RIAD_PRE_TICKET.tableNumero}/mark-paid-external/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({}),
        }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
        alert(data.error || "Impossible de marquer la commande comme réglée.");
        return;
    }

    window.location.href = "/riad/salle/";
}
