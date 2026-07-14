// menu-loader.js
// Charge les menus depuis l'API et les affiche dans le wizard

async function loadMenuChoices() {
    const container = document.getElementById('menuChoices');
    if (!container) {
        console.error('Container menuChoices introuvable');
        return;
    }

    try {
        const response = await fetch('/riad/api/menus/');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const menus = await response.json();

        if (!menus || menus.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted">
                    Aucun menu disponible
                </div>
            `;
            return;
        }

        let html = '';
        menus.forEach(menu => {
            html += `
                <div class="col-md-4 mb-3">
                    <button type="button"
                        class="btn btn-outline-dark w-100 p-3 menu-choice"
                        data-menu-id="${menu.id}"
                        data-menu-name="${escapeHtml(menu.name)}">
                        <strong>${escapeHtml(menu.name)}</strong><br>
                        <small>${menu.price} €</small>
                    </button>
                </div>
            `;
        });
        container.innerHTML = html;

        // ✅ Attacher les événements
        document.querySelectorAll('.menu-choice').forEach(btn => {
            btn.onclick = async function() {
                try {
                    const menuId = this.dataset.menuId;
                    const response = await fetch(`/riad/api/menu/${menuId}/`);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    const menu = await response.json();

                    window.currentMenu = menu;
                    window.currentSectionIndex = 0;
                    window.currentGuestChoices = [];

                    if (typeof renderLiveTicket === 'function') {
                        renderLiveTicket();
                    }
                    if (typeof showCurrentSection === 'function') {
                        showCurrentSection();
                    }
                } catch (error) {
                    console.error('Erreur chargement menu:', error);
                    alert('Erreur lors du chargement du menu');
                }
            };
        });

    } catch (error) {
        console.error('Erreur chargement menus:', error);
        container.innerHTML = `
            <div class="col-12 text-center text-danger">
                Erreur chargement des menus
                <button class="btn btn-sm btn-primary mt-2" onclick="loadMenuChoices()">
                    Réessayer
                </button>
            </div>
        `;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Exposer globalement
window.loadMenuChoices = loadMenuChoices;