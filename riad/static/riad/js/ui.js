function updateGuestTitle(currentGuest, guestCount) {
    document.getElementById("currentGuest").textContent =
        `${currentGuest} / ${guestCount}`;
}


function showStep(stepId) {
    const steps = [
        "step-guests",
        "step-menu",
        "step-section",
        "recap",
    ];

    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.add("d-none");
        }
    });

    document.getElementById(stepId).classList.remove("d-none");
}


function renderSection(section, currentGuest, guestCount) {
    const container = document.getElementById("step-section");

    let html = `
        <h3 class="mb-3">Convive ${currentGuest} / ${guestCount}</h3>
        <h4 class="mb-2">${section.name}</h4>
        <p class="text-muted mb-4">
            Choisissez ${section.min_choices}
        </p>
        <div class="row">
    `;

    section.products.forEach(product => {
        html += `
            <div class="col-md-4 mb-3">
                <button
                    type="button"
                    class="btn btn-outline-dark w-100 p-4 product-choice"
                    data-section-id="${section.id}"
                    data-section-name="${section.name}"
                    data-product-id="${product.id}"
                    data-product-name="${product.name}">
                    ${product.name}
                </button>
            </div>
        `;
    });

    html += `</div>`;

    container.innerHTML = html;
    showStep("step-section");
}


function renderRecap(guests) {
    let html = "";

    guests.forEach(guest => {
        html += `
            <div class="card mb-3">
                <div class="card-body">
                    <strong>Convive ${guest.number}</strong><br>
                    ${guest.menu_name}
                    <hr>
        `;

        guest.choices.forEach(choice => {
            html += `
                <div>
                    <strong>${choice.section_name} :</strong>
                    ${choice.product_name}
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    document.getElementById("recapContent").innerHTML = html;
    showStep("recap");
}