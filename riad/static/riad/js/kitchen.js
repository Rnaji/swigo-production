const togglingItems = new Set();
const closingTickets = new Set();

document.addEventListener("DOMContentLoaded", () => {
    initTicketFooterButtons();
    initLineDoneButtons();
    initWaitingTimers();
    markNewTickets();
});

function initTicketFooterButtons() {
    document.querySelectorAll(".kitchen-close-btn").forEach(button => {
        button.addEventListener("click", () => {
            const ticketId = button.dataset.ticket;
            if (!ticketId || closingTickets.has(ticketId) || button.disabled) return;

            closeTicket(ticketId, button);
        });
    });
}

function initLineDoneButtons() {
    document.querySelectorAll(".kitchen-ticket-line").forEach(line => {
        const button = line.querySelector(".line-done-btn");
        if (!button) return;

        const toggle = () => {
            const itemId = button.dataset.item;
            if (!itemId || togglingItems.has(itemId)) return;

            toggleLineDone(itemId, line, button);
        };

        button.addEventListener("click", event => {
            event.stopPropagation();
            toggle();
        });

        line.addEventListener("click", event => {
            if (event.target.closest(".line-done-btn")) return;
            toggle();
        });
    });
}

function toggleLineDone(itemId, lineEl, buttonEl) {
    togglingItems.add(itemId);
    lineEl.classList.add("line-busy");
    buttonEl.disabled = true;

    fetch(`/riad/kitchen/item/${itemId}/toggle/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken(),
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Erreur serveur");
        }

        return response.json();
    })
    .then(data => {
        applyLineDoneState(lineEl, buttonEl, data.is_done);

        const ticketEl = lineEl.closest(".kitchen-ticket");
        if (ticketEl) {
            updateTicketAllDoneState(ticketEl, data.all_items_done);
            updateCloseButton(ticketEl, data.all_items_done);
        }
    })
    .catch(error => {
        console.error(error);
        alert("Impossible de mettre à jour la ligne.");
    })
    .finally(() => {
        togglingItems.delete(itemId);
        lineEl.classList.remove("line-busy");
        buttonEl.disabled = false;
    });
}

function applyLineDoneState(lineEl, buttonEl, isDone) {
    lineEl.classList.toggle("line-done", isDone);
    buttonEl.classList.toggle("is-done", isDone);

    const check = buttonEl.querySelector(".line-done-check");
    const label = buttonEl.querySelector(".line-done-label");

    if (check) {
        check.textContent = isDone ? "✓" : "○";
    }

    if (label) {
        label.textContent = "Fait";
    }

    buttonEl.setAttribute(
        "aria-label",
        isDone ? "Annuler la validation" : "Marquer comme fait"
    );
}

function updateTicketAllDoneState(ticketEl, allDone) {
    ticketEl.classList.toggle("ticket-all-done", Boolean(allDone));
}

function updateCloseButton(ticketEl, allDone) {
    const button = ticketEl.querySelector(".kitchen-close-btn");
    if (!button) return;

    button.disabled = !allDone;
}

function closeTicket(ticketId, button) {
    const ticketEl = button.closest(".kitchen-ticket");
    const originalText = button.textContent;

    closingTickets.add(ticketId);
    button.disabled = true;
    button.textContent = "Clôture...";

    fetch(`/riad/kitchen/ticket/${ticketId}/close/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken(),
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Erreur serveur");
        }

        if (ticketEl) {
            ticketEl.remove();
        }

        updateHeaderCounters();
        checkEmptyKitchen();
    })
    .catch(error => {
        console.error(error);
        alert("Impossible de clôturer le bon.");
        button.disabled = false;
        button.textContent = originalText;
    })
    .finally(() => {
        closingTickets.delete(ticketId);
    });
}

function initWaitingTimers() {
    updateWaitingTimers();
    setInterval(updateWaitingTimers, 1000);
}

function updateWaitingTimers() {
    const timers = document.querySelectorAll(".ticket-waiting-time");
    let lateTickets = 0;

    timers.forEach(timer => {
        const sentAt = timer.dataset.sentAt;
        if (!sentAt) return;

        const ticket = timer.closest(".kitchen-ticket");
        const sentDate = new Date(sentAt);
        const now = new Date();

        let diffSeconds = Math.floor((now - sentDate) / 1000);

        if (diffSeconds < 0) {
            diffSeconds = 0;
        }

        const minutes = Math.floor(diffSeconds / 60);
        const seconds = diffSeconds % 60;

        const formatted =
            String(minutes).padStart(2, "0") +
            ":" +
            String(seconds).padStart(2, "0");

        ticket.classList.remove("ticket-warning", "ticket-danger");

        if (minutes >= 10) {
            timer.textContent = `🔴 ${formatted}`;
            ticket.classList.add("ticket-danger");
            lateTickets++;
        } else if (minutes >= 5) {
            timer.textContent = `🟠 ${formatted}`;
            ticket.classList.add("ticket-warning");
        } else {
            timer.textContent = `🟢 ${formatted}`;
        }
    });

    updateHeaderCounters(lateTickets);
}

function updateHeaderCounters(lateTickets = null) {
    const ticketCountEl = document.getElementById("ticketCount");
    const lateCountEl = document.getElementById("lateCount");

    const tickets = document.querySelectorAll(".kitchen-ticket");

    if (ticketCountEl) {
        ticketCountEl.textContent = tickets.length;
    }

    if (lateCountEl) {
        const count = lateTickets !== null
            ? lateTickets
            : document.querySelectorAll(".ticket-danger").length;

        lateCountEl.textContent = count > 0 ? `🔴 ${count} en retard` : "";
    }
}

function markNewTickets() {
    const tickets = document.querySelectorAll(".kitchen-ticket");

    tickets.forEach(ticket => {
        ticket.classList.add("ticket-new");

        setTimeout(() => {
            ticket.classList.remove("ticket-new");
        }, 2500);
    });

    playNewTicketSound();
}

function playNewTicketSound() {
    const sound = document.getElementById("newTicketSound");

    if (!sound) return;

    sound.volume = 0.25;

    sound.play().catch(() => {
        // Le navigateur bloque parfois le son avant interaction utilisateur.
    });
}

function checkEmptyKitchen() {
    const board = document.querySelector(".kitchen-board");
    const tickets = document.querySelectorAll(".kitchen-ticket");

    if (!board) return;

    if (tickets.length === 0) {
        board.innerHTML = `
            <div class="kitchen-empty">
                <h2>Aucun bon</h2>
                <p>Les nouveaux bons apparaîtront ici.</p>
            </div>
        `;
    }
}

function getCsrfToken() {
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith("csrftoken=")) {
            return cookie.substring("csrftoken=".length);
        }
    }

    return "";
}
