function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
}

async function loadMenu(menuId) {
    const response = await fetch(`/riad/api/menu/${menuId}/`);
    return await response.json();
}

async function saveOrder(tableNumero, guests) {
    const response = await fetch(`/riad/api/table/${tableNumero}/order/start/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            guests: guests
        })
    });

    return await response.json();
}