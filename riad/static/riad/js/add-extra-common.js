window.RIAD_ADD_GROUPS = [
    { name: "Boissons", icon: "local_bar", categories: ["Boisson", "Eau", "Jus"] },
    { name: "Mocktails", icon: "local_bar", categories: ["Mocktail"] },
    { name: "Desserts", icon: "icecream", categories: ["Dessert"] },
    { name: "Coupes glacées", icon: "icecream", categories: ["Coupe glacée"] },
    { name: "Thé / Café", icon: "local_cafe", categories: ["Thé / Café"] },
];

function parsePriceAmount(value) {
    if (value === null || value === undefined) return 0;
    const normalized = String(value).replace(",", ".").trim();
    const amount = parseFloat(normalized);
    return Number.isFinite(amount) ? amount : 0;
}

function formatExtraAmount(amount) {
    return `${Number(amount).toFixed(2)} €`;
}
