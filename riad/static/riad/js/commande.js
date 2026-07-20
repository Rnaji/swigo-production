document.addEventListener("DOMContentLoaded", () => {
    initWizard();
    initCancelOrder();
});

function getCSRFToken() {
    const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookie ? cookie.split("=")[1] : "";
}

function initCancelOrder() {
    const cancelBtn = document.getElementById("cancelOrderBtn");
    const modalEl = document.getElementById("cancelOrderModal");
    const messageEl = document.getElementById("cancelOrderModalMessage");
    const confirmBtn = document.getElementById("confirmCancelOrderBtn");

    if (!cancelBtn || !modalEl || !messageEl || !confirmBtn) {
        return;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    const tableNumero = window.RIAD_TABLE_NUMERO;

    cancelBtn.addEventListener("click", () => {
        messageEl.textContent =
            "Annuler cette prise de commande et supprimer le brouillon ?";

        modal.show();
    });

    confirmBtn.addEventListener("click", async () => {
        confirmBtn.disabled = true;
        confirmBtn.textContent = "Annulation...";

        try {
            const response = await fetch(`/riad/api/table/${tableNumero}/cancel-order/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                },
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                alert(data.error || "Impossible d'annuler la commande.");
                return;
            }

            window.location.href = data.redirect || "/riad/salle/";
        } catch (error) {
            alert("Erreur réseau pendant l'annulation.");
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.textContent = "Oui, annuler la commande";
            modal.hide();
        }
    });
}
