const TASKS_POLL_MS = 3000;
const OVERDUE_SECONDS = 5 * 60;

let tasksState = [];
let pollTimer = null;
let localTimer = null;
let busyTaskKey = null;
let tasksRefreshPending = false;

document.addEventListener("DOMContentLoaded", () => {
    refreshTasks();
    if (!pollTimer) {
        pollTimer = setInterval(refreshTasksIfVisible, TASKS_POLL_MS);
    }
    if (!localTimer) {
        localTimer = setInterval(updateLocalTaskTimers, 1000);
    }

    document.addEventListener("visibilitychange", () => {
        if (!document.hidden) {
            refreshTasks();
        }
    });
});

async function refreshTasksIfVisible() {
    if (document.hidden) {
        return;
    }
    await refreshTasks();
}

async function refreshTasks() {
    try {
        const response = await fetch("/riad/api/tasks/");
        const data = await response.json();
        tasksState = data.tasks || [];
        renderTasks();
        document.getElementById("taskCount").textContent = String(tasksState.length);
    } catch (error) {
        console.error("Impossible de charger les tâches", error);
    }
}

function formatServedSinceLabel(prefix, seconds) {
    const minutes = Math.max(Math.floor(seconds / 60), 0);

    if (minutes <= 0) {
        return `${prefix} depuis moins d'1 min`;
    }

    if (minutes === 1) {
        return `${prefix} depuis 1 min`;
    }

    return `${prefix} depuis ${minutes} min`;
}

function formatInstalledSinceLabel(seconds) {
    const minutes = Math.max(Math.floor(seconds / 60), 0);

    if (minutes < 1) {
        return "👥 Clients installés à l'instant";
    }

    if (minutes < 60) {
        if (minutes === 1) {
            return "👥 Clients installés depuis 1 min";
        }

        return `👥 Clients installés depuis ${minutes} min`;
    }

    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    return `👥 Clients installés depuis ${hours} h ${String(remainingMinutes).padStart(2, "0")}`;
}

function updateLocalTaskTimers() {
    let changed = false;

    tasksState.forEach(task => {
        if (task.ready_at) {
            const readyDate = new Date(task.ready_at);
            const elapsed = Math.max(Math.floor((Date.now() - readyDate.getTime()) / 1000), 0);
            const previousLabel = task.elapsed_label;
            task.ready_label = formatReadySince(elapsed);
            task.elapsed_label = task.ready_label;

            if (previousLabel !== task.elapsed_label) {
                changed = true;
            }
            return;
        }

        if (task.served_since_at && task.served_since_prefix && !task.claimed) {
            const servedDate = new Date(task.served_since_at);
            const elapsed = Math.max(
                Math.floor((Date.now() - servedDate.getTime()) / 1000),
                0
            );
            const previousLabel = task.served_since_label;
            task.served_since_label = formatServedSinceLabel(
                task.served_since_prefix,
                elapsed
            );

            if (previousLabel !== task.served_since_label) {
                changed = true;
            }
            return;
        }

        if (task.installed_at && !task.claimed) {
            const installedDate = new Date(task.installed_at);
            const elapsed = Math.max(
                Math.floor((Date.now() - installedDate.getTime()) / 1000),
                0
            );
            const previousLabel = task.installed_since_label;
            task.installed_since_label = formatInstalledSinceLabel(elapsed);
            task.installed_since_seconds = elapsed;

            if (!task.claimed) {
                const previousState = task.visual_state;
                task.visual_state = elapsed > OVERDUE_SECONDS
                    ? "overdue"
                    : "pending";

                if (
                    previousState !== task.visual_state
                    || previousLabel !== task.installed_since_label
                ) {
                    changed = true;
                }
            } else if (previousLabel !== task.installed_since_label) {
                changed = true;
            }
            return;
        }

        if (typeof task.elapsed_seconds !== "number") {
            return;
        }

        task.elapsed_seconds += 1;

        const previousLabel = task.elapsed_label;
        task.elapsed_label = formatElapsedSince(task.elapsed_seconds);

        if (!task.claimed) {
            const previousState = task.visual_state;
            task.visual_state = task.elapsed_seconds > OVERDUE_SECONDS
                ? "overdue"
                : "pending";

            if (previousState !== task.visual_state || previousLabel !== task.elapsed_label) {
                changed = true;
            }
        } else if (previousLabel !== task.elapsed_label) {
            changed = true;
        }
    });

    if (changed) {
        renderTasks();
    }
}

function formatReadySince(seconds) {
    const minutes = Math.max(Math.floor(seconds / 60), 0);
    const remainingSeconds = Math.max(seconds % 60, 0);
    return `Prêt depuis ${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
}

function formatElapsedSince(seconds) {
    const minutes = Math.max(Math.floor(seconds / 60), 0);

    if (minutes <= 0) {
        return null;
    }

    if (minutes === 1) {
        return "Depuis 1 min";
    }

    return `Depuis ${minutes} min`;
}

function isOrderTask(task) {
    return Boolean(task.is_order_task || task.action_type === "open_commande");
}

function getDoneLabel(task) {
    if (task.action_type === "serve_items") {
        return "Fait";
    }

    if (isOrderTask(task) && task.claimed) {
        return "Reprendre la commande";
    }

    return "Fait";
}

function getCommandeUrl(task) {
    return task.commande_url || `/riad/table/${task.table_numero}/commande/?from=tasks`;
}

function taskIdentity(task) {
    return `${task.id}:${task.task_key}`;
}

function renderTasks() {
    const board = document.getElementById("tasksBoard");

    if (!tasksState.length) {
        board.innerHTML = `
            <div class="tasks-empty">
                Aucune tâche en cours — le service est à jour.
            </div>
        `;
        return;
    }

    board.innerHTML = tasksState.map(renderTaskCard).join("");
    bindTaskButtons();
}

function renderTaskItems(task) {
    if (task.action_type !== "serve_items" || !Array.isArray(task.items) || !task.items.length) {
        return "";
    }

    const lines = task.items.map(item => {
        const note = item.note
            ? `<div class="task-item-note">${escapeHtml(item.note)}</div>`
            : "";

        return `
            <div class="task-item-line">
                <span>${item.quantity} × ${escapeHtml(item.name)}</span>
                ${note}
            </div>
        `;
    }).join("");

    return `<div class="task-items">${lines}</div>`;
}

function renderTaskCard(task) {
    const identity = taskIdentity(task);
    const isBusy = busyTaskKey === identity;
    const itemsBlock = renderTaskItems(task);
    const meta = task.claimed
        ? `<div class="task-status-label">PRIS EN CHARGE</div>`
        : (task.served_since_label
            ? `<div class="task-meta">${escapeHtml(task.served_since_label)}</div>`
            : (task.installed_since_label
                ? `<div class="task-meta">${escapeHtml(task.installed_since_label)}</div>`
                : (task.elapsed_label
                    ? `<div class="task-meta">${escapeHtml(task.elapsed_label)}</div>`
                    : "")));

    const doneLabel = getDoneLabel(task);

    const button = task.claimed
        ? `<button type="button" class="task-btn task-btn-done" data-action="done" data-task-id="${task.id}" data-task-key="${escapeHtml(task.task_key)}" ${isBusy ? "disabled" : ""}>${doneLabel}</button>`
        : `<button type="button" class="task-btn task-btn-claim" data-action="claim" data-task-id="${task.id}" data-task-key="${escapeHtml(task.task_key)}" ${isBusy ? "disabled" : ""}>Prendre en charge</button>`;

    return `
        <article class="task-card ${escapeHtml(task.visual_state || "pending")}" data-task-id="${task.id}" data-task-key="${escapeHtml(task.task_key)}">
            <div class="task-table">Table ${task.table_numero}</div>
            <div class="task-action">${escapeHtml(task.emoji)} ${escapeHtml(task.title)}</div>
            ${itemsBlock}
            ${meta}
            <div class="task-actions">${button}</div>
        </article>
    `;
}

function bindTaskButtons() {
    document.querySelectorAll("[data-action='claim']").forEach(button => {
        button.addEventListener("click", () => {
            claimTask(button);
        });
    });

    document.querySelectorAll("[data-action='done']").forEach(button => {
        button.addEventListener("click", () => {
            completeTask(button);
        });
    });
}

function findTask(taskId, taskKey) {
    return tasksState.find(item => item.id === taskId && item.task_key === taskKey);
}

async function claimTask(button) {
    if (busyTaskKey) {
        return;
    }

    const taskId = Number(button.dataset.taskId);
    const taskKey = button.dataset.taskKey;
    const task = findTask(taskId, taskKey);
    if (!task) {
        return;
    }

    busyTaskKey = taskIdentity(task);
    button.disabled = true;
    button.textContent = "Prise en charge…";

    try {
        const response = await fetch(`/riad/api/tasks/${taskId}/claim/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ task_key: taskKey }),
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(data.error || "Impossible de prendre cette tâche en charge.");
            await refreshTasks();
            return;
        }

        if (data.redirect_url) {
            window.location.href = data.redirect_url;
            return;
        }

        if (isOrderTask(data.task || task)) {
            window.location.href = getCommandeUrl(data.task || task);
            return;
        }

        await refreshTasks();
    } catch (error) {
        console.error(error);
        alert("Erreur réseau.");
    } finally {
        busyTaskKey = null;
    }
}

async function completeTask(button) {
    if (busyTaskKey) {
        return;
    }

    const taskId = Number(button.dataset.taskId);
    const taskKey = button.dataset.taskKey;
    const task = findTask(taskId, taskKey);
    if (!task) {
        return;
    }

    busyTaskKey = taskIdentity(task);
    button.disabled = true;
    button.textContent = "Validation…";

    try {
        if (task.action_type === "serve_items") {
            const response = await fetch(`/riad/api/tasks/${taskId}/complete/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ task_key: taskKey }),
            });

            const data = await response.json();
            if (!response.ok || !data.success) {
                alert(data.error || "Impossible de terminer cette tâche.");
                await refreshTasks();
                return;
            }

            await refreshTasks();
            window.dispatchEvent(new CustomEvent("riad:tasks-updated"));
            return;
        }

        if (isOrderTask(task)) {
            window.location.href = getCommandeUrl(task);
            return;
        }

        if (task.action_type === "open_pre_ticket") {
            if (task.pre_ticket_url) {
                window.location.href = task.pre_ticket_url;
            }
            return;
        }

        const response = await fetch(`/riad/api/table/${task.table_numero}/next/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
        });

        const data = await response.json();

        if (!response.ok) {
            alert("Impossible de valider cette tâche.");
            await refreshTasks();
            return;
        }

        if (data.status === "ordering") {
            window.location.href = `/riad/table/${task.table_numero}/commande/`;
            return;
        }

        await refreshTasks();
        window.dispatchEvent(new CustomEvent("riad:tasks-updated"));
    } catch (error) {
        console.error(error);
        alert("Erreur réseau.");
    } finally {
        busyTaskKey = null;
    }
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
}
