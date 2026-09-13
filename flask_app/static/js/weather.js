// This file runs on the /weather page.
// Job: take whatever the farmer types -> call our Flask API (/api/weather)
// -> take the JSON response -> fill it into the HTML.

document.addEventListener("DOMContentLoaded", function () {

    // Grab all the HTML elements we need to read from / write into
    const locationInput = document.getElementById("location-input");
    const searchBtn = document.getElementById("search-btn");
    const errorEl = document.getElementById("weather-error");
    const loadingEl = document.getElementById("weather-loading");
    const currentCard = document.getElementById("current-weather-card");
    const advisorySection = document.getElementById("advisory-section");
    const forecastSection = document.getElementById("forecast-section");

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

    // Converts "2026-09-15" -> "Tue, 15 Sep" for display
    function formatDate(dateString) {
        const date = new Date(dateString + "T00:00:00");
        return date.toLocaleDateString("en-IN", {
            weekday: "short", day: "numeric", month: "short"
        });
    }

    // Fills the "current weather" card with data from the API
    function renderCurrentWeather(place, current) {

        document.getElementById("current-icon").textContent = current.icon || "☀️";

        const locationLabel = [place.name, place.admin1, place.country]
            .filter(Boolean)   // remove empty values
            .join(", ");

        document.getElementById("current-location").textContent = locationLabel;
        document.getElementById("current-description").textContent = current.description || "--";
        document.getElementById("current-temp").textContent = (current.temperature ?? "--") + " °C";
        document.getElementById("current-humidity").textContent = (current.humidity ?? "--") + " %";
        document.getElementById("current-rain").textContent = (current.precipitation ?? "--") + " mm";
        document.getElementById("current-wind").textContent = (current.wind_speed ?? "--") + " km/h";

        currentCard.classList.remove("hidden");
    }

    // Fills the advisory (farming tips) list
    function renderAdvisory(tips) {

        const list = document.getElementById("advisory-list");
        list.innerHTML = "";

        if (!tips || tips.length === 0) {
            advisorySection.classList.add("hidden");
            return;
        }

        // One <li> per tip
        tips.forEach(function (tip) {
            const li = document.createElement("li");
            li.textContent = tip;
            list.appendChild(li);
        });

        advisorySection.classList.remove("hidden");
    }

    // Builds one card per day for the 7-day forecast
    function renderForecast(days) {

        const grid = document.getElementById("forecast-grid");
        grid.innerHTML = "";

        if (!days || days.length === 0) {
            forecastSection.classList.add("hidden");
            return;
        }

        days.forEach(function (day) {
            const card = document.createElement("div");
            card.className = "forecast-day-card";

            card.innerHTML = `
                <p class="forecast-date">${formatDate(day.date)}</p>
                <p class="forecast-icon">${day.icon || "☀️"}</p>
                <p class="forecast-desc">${day.description || ""}</p>
                <p class="forecast-temps">
                    <span class="temp-max">${day.temp_max ?? "--"}°</span> /
                    <span class="temp-min">${day.temp_min ?? "--"}°</span>
                </p>
                <p class="forecast-rain">🌧️ ${day.rain_probability ?? "--"}% (${day.rain_mm ?? "--"} mm)</p>
                <p class="forecast-wind">💨 ${day.wind_speed ?? "--"} km/h</p>
            `;

            grid.appendChild(card);
        });

        forecastSection.classList.remove("hidden");
    }

    // Main function: called on Search click / Enter key / page load
    async function fetchWeather() {

        const location = locationInput.value.trim();

        // reset UI before every new search
        hideError();
        currentCard.classList.add("hidden");
        advisorySection.classList.add("hidden");
        forecastSection.classList.add("hidden");

        if (!location) {
            showError("Please enter a location.");
            return;
        }

        setLoading(true);

        try {
            // Call our own Flask backend, NOT Open-Meteo directly
            // (backend does the geocoding + forecast + advisory logic)
            const response = await fetch("/api/weather?location=" + encodeURIComponent(location));
            const data = await response.json();

            setLoading(false);

            if (!response.ok || !data.success) {
                showError(data.error || "Could not fetch weather. Please try again.");
                return;
            }

            renderCurrentWeather(data.location, data.current);
            renderAdvisory(data.advisory);
            renderForecast(data.forecast);

        } catch (err) {
            setLoading(false);
            showError("Something went wrong. Please check your connection.");
            console.error("Weather fetch error:", err);
        }
    }

    // Event listeners: click Search button, or press Enter in the input
    searchBtn.addEventListener("click", fetchWeather);
    locationInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") fetchWeather();
    });

    // Auto-fetch once on page load if a default location was pre-filled
    if (locationInput.value.trim()) {
        fetchWeather();
    }
});
