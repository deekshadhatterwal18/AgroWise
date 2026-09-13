// This file runs on the /market page.
// Flow: load crop list -> user picks a crop -> we load that crop's
// states into the 2nd dropdown -> user optionally picks their state
// -> click Compare Prices -> render summary + bar chart, with the
// farmer's own state highlighted in a different color.

document.addEventListener("DOMContentLoaded", function () {

    const commoditySelect = document.getElementById("commodity-select");
    const stateSelect = document.getElementById("state-select");
    const searchBtn = document.getElementById("market-search-btn");

    const errorEl = document.getElementById("market-error");
    const loadingEl = document.getElementById("market-loading");
    const summarySection = document.getElementById("market-summary");
    const yourStateCard = document.getElementById("your-state-card");
    const chartSection = document.getElementById("market-chart-section");

    let priceChart = null;  // holds the Chart.js instance

    function showError(message) {
        errorEl.textContent = message;
        errorEl.classList.remove("hidden");
    }

    function hideError() {
        errorEl.classList.add("hidden");
    }

    function setLoading(isLoading) {
        loadingEl.classList.toggle("hidden", !isLoading);
    }

    // --- Step 1: load crop names into the dropdown ---
    async function loadCommodities() {

        try {
            const response = await fetch("/api/market/commodities");
            const data = await response.json();

            if (!data.success) {
                showError(data.error || "Could not load crop list.");
                return;
            }

            data.commodities.forEach(function (crop) {
                const option = document.createElement("option");
                option.value = crop;
                option.textContent = crop;
                commoditySelect.appendChild(option);
            });

        } catch (err) {
            showError("Could not connect to server.");
            console.error("Load commodities error:", err);
        }
    }

    // --- Step 2: when a crop is chosen, load the states it's traded in ---
    async function loadStatesForCommodity(commodity) {

        stateSelect.innerHTML = '<option value="">-- None --</option>';

        if (!commodity) return;

        try {
            const response = await fetch(
                "/api/market/states?commodity=" + encodeURIComponent(commodity)
            );
            const data = await response.json();

            if (!data.success) return;

            data.states.forEach(function (state) {
                const option = document.createElement("option");
                option.value = state;
                option.textContent = state;
                stateSelect.appendChild(option);
            });

        } catch (err) {
            console.error("Load states error:", err);
        }
    }

    // --- Fills the summary cards ---
    function renderSummary(summary, statePrices, selectedState) {

        document.getElementById("summary-avg").textContent =
            "₹" + summary.average_price_kg + " / kg";

        document.getElementById("summary-highest").textContent =
            "₹" + summary.highest_price_kg + " (" + summary.highest_state + ")";

        document.getElementById("summary-lowest").textContent =
            "₹" + summary.lowest_price_kg + " (" + summary.lowest_state + ")";

        // Only show the 4th card if the farmer picked their state
        if (selectedState) {

            const match = statePrices.find(function (item) {
                return item.state === selectedState;
            });

            if (match) {
                document.getElementById("summary-your-state").textContent =
                    "₹" + match.price + " / kg";
                yourStateCard.classList.remove("hidden");
            } else {
                yourStateCard.classList.add("hidden");
            }

        } else {
            yourStateCard.classList.add("hidden");
        }

        summarySection.classList.remove("hidden");
    }

    // --- Draws the bar chart, highlighting the selected state's bar ---
    function renderChart(statePrices, selectedState) {

        const labels = statePrices.map(function (item) { return item.state; });
        const prices = statePrices.map(function (item) { return item.price; });

        // Give every bar the normal green color, except the farmer's
        // own state, which gets an amber/orange highlight color.
        const barColors = statePrices.map(function (item) {
            return item.state === selectedState ? "#e08a1e" : "#3f7d3a";
        });

        const ctx = document.getElementById("price-chart").getContext("2d");

        if (priceChart) {
            priceChart.destroy();
        }

        priceChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Average Price (₹/kg)",
                    data: prices,
                    backgroundColor: barColors
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        chartSection.classList.remove("hidden");
    }

    // --- Main action: fetch data for the selected crop ---
    async function fetchPrices() {

        const commodity = commoditySelect.value;
        const selectedState = stateSelect.value;

        hideError();
        summarySection.classList.add("hidden");
        chartSection.classList.add("hidden");

        if (!commodity) {
            showError("Please select a crop first.");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(
                "/api/market/prices?commodity=" + encodeURIComponent(commodity)
            );
            const data = await response.json();

            setLoading(false);

            if (!response.ok || !data.success) {
                showError(data.error || "Could not fetch price data.");
                return;
            }

            renderSummary(data.summary, data.state_prices, selectedState);
            renderChart(data.state_prices, selectedState);

        } catch (err) {
            setLoading(false);
            showError("Something went wrong. Please try again.");
            console.error("Fetch prices error:", err);
        }
    }

    // When crop changes, refresh the state dropdown for that crop
    commoditySelect.addEventListener("change", function () {
        loadStatesForCommodity(commoditySelect.value);
    });

    searchBtn.addEventListener("click", fetchPrices);

    loadCommodities();
});
