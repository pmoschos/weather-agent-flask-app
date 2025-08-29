const form = document.getElementById('weatherForm');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const result = document.getElementById('weatherResult');
const searchBtn = document.getElementById('searchBtn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const town = document.getElementById('town').value.trim();
    const country = document.getElementById('country').value.trim();

    if (!town || !country) {
        showError('Please fill in both town and country fields');
        return;
    }

    loading.style.display = 'block';
    error.style.display = 'none';
    result.style.display = 'none';
    searchBtn.disabled = true;
    searchBtn.textContent = '🔍 Searching...';

    try {
        const response = await fetch('/weather', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ town, country })
        });
        const data = await response.json();

        if (data.success) {
            displayWeather(data.data);
            loadRecentSearches();
        } else {
            showError(data.error || 'Failed to fetch weather data');
        }
    } catch (err) {
        showError('Network error. Please try again.');
        console.error('Error:', err);
    } finally {
        loading.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.textContent = '🔍 Get Weather';
    }
});

function displayWeather(weather) {
    document.getElementById('weatherLocation').textContent =
        `${weather.town}, ${weather.country}`;
    document.getElementById('temperature').textContent = weather.temperature;
    document.getElementById('wind').textContent = weather.wind;
    document.getElementById('humidity').textContent = weather.humidity;
    result.style.display = 'block';
}

function showError(message) {
    error.textContent = message;
    error.style.display = 'block';
}

async function loadRecentSearches() {
    try {
        const response = await fetch('/recent');
        const data = await response.json();
        if (data.success && data.data.length > 0) {
            const recentList = document.getElementById('recentList');
            recentList.innerHTML = data.data.slice(0, 5).map(search =>
                `<div class="recent-item">
                    ${search.town}, ${search.country} - ${search.temperature}
                    (${new Date(search.timestamp).toLocaleString()})
                </div>`
            ).join('');
        }
    } catch (err) {
        console.error('Error loading recent searches:', err);
    }
}

document.addEventListener('DOMContentLoaded', loadRecentSearches);
