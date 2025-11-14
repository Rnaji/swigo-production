// Fonction pour obtenir le jeton CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Fonction pour charger les plats d'une catégorie spécifique
function loadPlats(categorie_nom) {
    const platsContainer = document.getElementById('plats-container');
    platsContainer.innerHTML = '<p>Chargement...</p>';

    fetch(`/plats_par_categorie_ajax/${categorie_nom}/`)
    .then(response => response.json())
    .then(data => {
        platsContainer.innerHTML = '';

        if (data.plats.length === 0) {
            platsContainer.innerHTML = '<p>Aucun plat disponible pour cette catégorie.</p>';
            return;
        }

        data.plats.forEach(plat => {
            const imageUrl = plat.photo_url ? plat.photo_url : '/path/to/default/image.jpg'; // Mettez ici le chemin par défaut

            platsContainer.appendChild(createPlatElement(plat, imageUrl));
        });
    })
    .catch(error => {
        platsContainer.innerHTML = '<p>Erreur lors du chargement des plats.</p>';
        console.error('Erreur lors du chargement des plats :', error);
    });
}

// Fonction pour créer un élément de plat (DOM)
function createPlatElement(plat, imageUrl) {
    const li = document.createElement('li');
    li.className = 'card-container col-lg-4 col-md-6 m-b30';

    const divImgBox = document.createElement('div');
    divImgBox.className = 'dz-img-box style-7';
    divImgBox.onclick = () => openPlatModal(plat.id, plat.nom, imageUrl, plat.description_longue, plat.prix_unitaire);

    const dzMedia = document.createElement('div');
    dzMedia.className = 'dz-media';

    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = plat.nom;
    img.className = 'img-fluid';
    img.style.width = '200px';
    img.style.height = '200px';
    img.style.objectFit = 'cover';

    dzMedia.appendChild(img);
    divImgBox.appendChild(dzMedia);

    const dzContent = document.createElement('div');
    dzContent.className = 'dz-content';

    const title = document.createElement('h5');
    title.className = 'title';
    title.textContent = plat.nom;

    const desc = document.createElement('p');
    desc.textContent = plat.description_courte;

    const price = document.createElement('span');
    price.className = 'price';
    price.textContent = `${plat.prix_unitaire} €`;

    dzContent.appendChild(title);
    dzContent.appendChild(desc);
    dzContent.appendChild(price);

    divImgBox.appendChild(dzContent);
    li.appendChild(divImgBox);

    return li;
}

// Fonction pour afficher la modal avec les détails d'un plat
function openPlatModal(platId, nom, imageUrl, description_longue, prix) {
    document.getElementById('plat-nom').textContent = nom;
    document.getElementById('plat-photo').src = imageUrl;
    document.getElementById('plat-description').textContent = description_longue;
    document.getElementById('plat-prix').textContent = `${prix} €`;

    fetch(`/options_par_plat_ajax/${platId}/`)
    .then(response => response.json())
    .then(data => {
        if (data.options.length > 0) {
            document.getElementById('ajouter-au-panier-btn').onclick = function() {
                $('#platModal').modal('hide');
                showOptionsModal(platId);
            };
        } else {
            document.getElementById('ajouter-au-panier-btn').onclick = function() {
                ajouterAuPanier(platId);
                $('#platModal').modal('hide');
            };
        }
    })
    .catch(error => {
        console.error('Erreur lors de la vérification des options :', error);
    });

    $('#platModal').modal('show');
}

// Fonction pour afficher la modal des options d'un plat
function showOptionsModal(platId) {
    fetch(`/options_par_plat_ajax/${platId}/`)
    .then(response => response.json())
    .then(data => {
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        if (data.options.length === 0) {
            optionsContainer.innerHTML = '<p>Aucune option disponible pour ce plat.</p>';
            return;
        }

        data.options.forEach(option => {
            optionsContainer.innerHTML += `
                <div class="option-item">
                    <input type="checkbox" id="option-${option.id}" name="option" value="${option.id}">
                    <label for="option-${option.id}">${option.nom_option} - ${option.prix_unitaire} €</label>
                </div>
            `;
        });

        document.getElementById('ajouter-options-panier').onclick = function() {
            const optionsSelectionnees = [];
            const checkboxes = document.querySelectorAll('#options-container input[type="checkbox"]:checked');

            checkboxes.forEach(checkbox => {
                optionsSelectionnees.push(checkbox.value);
            });

            ajouterAuPanier(platId, optionsSelectionnees);
            $('#optionsModal').modal('hide');
        };

        $('#optionsModal').modal('show');
    })
    .catch(error => {
        console.error('Erreur lors du chargement des options :', error);
    });
}

// Fonction pour ajouter un plat au panier (avec ou sans options)
function ajouterAuPanier(platId, optionsSelectionnees = []) {
    fetch(`/ajouter_au_panier/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            plat_id: platId,
            options: optionsSelectionnees
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartDisplay(data.cart_items, data.totals, data.code_promo);
        } else {
            console.error('Erreur lors de l\'ajout au panier:', data.message);
        }
    })
    .catch(error => {
        console.error('Erreur lors de la requête d\'ajout au panier :', error);
    });
}

// Fonction pour mettre à jour l'affichage du panier
function updateCartDisplay(cartItems, totals, codePromo = null) {
    const cartContainer = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    cartContainer.innerHTML = '';

    if (cartItems.length === 0) {
        cartContainer.innerHTML = '<p id="empty-cart-message">Votre panier est vide.</p>';
        cartCount.textContent = '(0)';
        document.getElementById('invoice-details').innerHTML = '';
        return;
    }

    cartItems.forEach(item => {
        const optionsText = item.options && item.options.length > 0
            ? `<small><i>Options: ${item.options.join(', ')}</i></small>`
            : '';

        const prixTotalLigne = parseFloat(item.prix_total).toFixed(2);

        cartContainer.innerHTML += `
    <div class="cart-item style-1" data-article-id="${item.article_id}">
        <div class="dz-content">
            <div class="dz-head">
                <h6 class="title mb-0">${item.plat_nom}</h6>
                ${optionsText}
                <a href="javascript:void(0);" class="remove-item" data-article-id="${item.article_id}">
                    <i class="fa-solid fa-xmark text-danger"></i>
                </a>
            </div>
            <div class="dz-body">
                <div class="btn-quantity style-1" style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                    <button class="btn btn-default bootstrap-touchspin-down" data-article-id="${item.article_id}" style="display: inline-block; width: 40px; height: 40px;">
                        <i class="ti-minus"></i>
                    </button>
                    <input type="text" class="quantity-input form-control" value="${item.quantite}" readonly style="text-align: center; width: 50px; height: 40px;">
                    <button class="btn btn-default bootstrap-touchspin-up" data-article-id="${item.article_id}" style="display: inline-block; width: 40px; height: 40px;">
                        <i class="ti-plus"></i>
                    </button>
                </div>
                <h5 class="price">${prixTotalLigne} €</h5>
            </div>
        </div>
    </div>
`;


    });

    const totalItems = cartItems.reduce((acc, item) => acc + item.quantite, 0);
    cartCount.textContent = `(${totalItems})`;

    updateInvoiceDetails(totals, codePromo);
    attachCartEventListeners();
}

// Fonction pour mettre à jour les détails de la facture
function updateInvoiceDetails(totals, codePromo = null) {
    const invoiceDetails = document.getElementById('invoice-details');
    invoiceDetails.innerHTML = '';

    let reductionHtml = '';
    if (totals.reduction && parseFloat(totals.reduction) > 0 && codePromo) {
        reductionHtml = `
            <div class="flex-space-between">
                <p>Réduction (${codePromo.code}):</p>s
                <p class="text-primary">-${parseFloat(totals.reduction).toFixed(2)} €</p>
            </div>
        `;
    }

    invoiceDetails.innerHTML = `
        <h6>Détails de la facture</h6>
        <div class="flex-space-between">
            <p>Sous-total :</p>
            <p>${parseFloat(totals.sous_total).toFixed(2)} €</p>
        </div>
        ${reductionHtml}
        <div class="flex-space-between">
            <p>Frais de livraison :</p>
            <p>${parseFloat(totals.frais_livraison).toFixed(2)} €</p>
        </div>
        <div class="flex-space-between">
            <h5>Total TTC :</h5>
            <h5 class="text-primary">${parseFloat(totals.prix_total).toFixed(2)} €</h5>
        </div>
    `;
}

// Attacher les événements aux boutons dans le panier
function attachCartEventListeners() {
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function() {
            const articleId = this.getAttribute('data-article-id');
            removeItemFromCart(articleId);
        });
    });

    document.querySelectorAll('.bootstrap-touchspin-up').forEach(button => {
        button.addEventListener('click', function() {
            const articleId = this.getAttribute('data-article-id');
            changeQuantity(articleId, 1);
        });
    });

    document.querySelectorAll('.bootstrap-touchspin-down').forEach(button => {
        button.addEventListener('click', function() {
            const articleId = this.getAttribute('data-article-id');
            changeQuantity(articleId, -1);
        });
    });
}

// Fonction pour supprimer un article du panier
function removeItemFromCart(articleId) {
    fetch(`/remove_item_from_cart/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ article_id: articleId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartDisplay(data.cart_items, data.totals, data.code_promo);
        } else {
            console.error('Erreur lors de la suppression de l\'article:', data.message);
        }
    })
    .catch(error => {
        console.error('Erreur lors de la requête de suppression :', error);
    });
}

// Fonction pour changer la quantité d'un article
function changeQuantity(articleId, delta) {
    fetch(`/update_quantity/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ article_id: articleId, delta: delta })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartDisplay(data.cart_items, data.totals, data.code_promo);
        } else {
            console.error('Erreur lors de la mise à jour de la quantité :', data.message);
        }
    })
    .catch(error => {
        console.error('Erreur lors de la requête de mise à jour de la quantité :', error);
    });
}

// Gestion du formulaire de code promo
document.getElementById('code-promo-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const codePromo = document.getElementById('code_promo_input').value.trim();

    fetch('/appliquer_code_promo/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code_promo: codePromo })
    })
    .then(response => response.json())
    .then(data => {
        const messageContainer = document.getElementById('code-promo-message');
        if (data.success) {
            updateCartDisplay(data.cart_items, data.totals, data.code_promo);
            messageContainer.innerHTML = '<span class="text-success">Code promo appliqué avec succès.</span>';
        } else {
            messageContainer.innerHTML = `<span class="text-danger">Erreur : ${data.message}</span>`;
        }
    })
    .catch(error => {
        console.error('Erreur lors de l\'application du code promo :', error);
    });
});

// Charger le panier au chargement de la page
document.addEventListener("DOMContentLoaded", function() {
    fetch('/panier/')
    .then(response => response.json())
    .then(data => {
        if (data.cart_items) {
            updateCartDisplay(data.cart_items, data.totals, data.code_promo);
        }
    })
    .catch(error => {
        console.error('Erreur lors de la récupération du panier :', error);
    });

    const observer = new MutationObserver(function(mutationsList) {
        for (const mutation of mutationsList) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(node => {
                    if (node.classList && node.classList.contains('lg-container')) {
                        node.style.display = 'none';
                    }
                });
            }
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
