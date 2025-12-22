// Poker Tracker v2 - With Event Management
let players = [];
let currentEvent = '';
let profitLossChart = null;
let chipsTrendChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadEvents();
    attachEventListeners();
});

// Tab Navigation
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

// Attach Event Listeners
function attachEventListeners() {
    document.getElementById('event-select').addEventListener('change', handleEventChange);
    document.getElementById('new-event-btn').addEventListener('click', showEventModal);
    document.getElementById('create-event-btn').addEventListener('click', createEvent);
    document.getElementById('cancel-event-btn').addEventListener('click', hideEventModal);
    document.getElementById('add-player').addEventListener('click', addPlayer);
    document.getElementById('save-data').addEventListener('click', saveData);
    document.getElementById('calculate-settlements').addEventListener('click', calculateSettlements);
    document.getElementById('refresh-charts').addEventListener('click', refreshCharts);
    document.getElementById('clear-data').addEventListener('click', clearEventData);
    
    // Event name input - Enter key
    document.getElementById('event-name-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') createEvent();
    });
}

// Load Events List
async function loadEvents() {
    try {
        const response = await fetch('/api/events');
        const data = await response.json();
        const select = document.getElementById('event-select');
        
        // Clear existing options except first
        select.innerHTML = '<option value="">-- Select an Event --</option>';
        
        data.events.forEach(event => {
            const option = document.createElement('option');
            option.value = event;
            option.textContent = event;
            select.appendChild(option);
        });
    } catch (error) {
        showToast('Error loading events', 'error');
        console.error(error);
    }
}

// Handle Event Selection Change
async function handleEventChange(e) {
    currentEvent = e.target.value;
    
    if (currentEvent) {
        await loadEventData(currentEvent);
    } else {
        players = [];
        renderTable();
        updateTotals();
        updateSummary();
    }
}

// Show Event Modal
function showEventModal() {
    document.getElementById('event-modal').classList.remove('hidden');
    document.getElementById('event-name-input').value = '';
    document.getElementById('event-name-input').focus();
}

// Hide Event Modal
function hideEventModal() {
    document.getElementById('event-modal').classList.add('hidden');
}

// Create New Event
async function createEvent() {
    const eventName = document.getElementById('event-name-input').value.trim();
    
    if (!eventName) {
        showToast('Please enter an event name', 'error');
        return;
    }
    
    showLoading(true);
    try {
        const response = await fetch('/api/events', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_name: eventName })
        });
        
        const result = await response.json();
        
        if (result.success) {
            hideEventModal();
            await loadEvents();
            document.getElementById('event-select').value = eventName;
            currentEvent = eventName;
            players = [];
            addPlayer(); // Add first empty player
            showToast(`Event "${eventName}" created!`, 'success');
        } else {
            showToast(result.error || 'Error creating event', 'error');
        }
    } catch (error) {
        showToast('Error creating event', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Load Event Data
async function loadEventData(eventName) {
    showLoading(true);
    try {
        const response = await fetch(`/api/data/${encodeURIComponent(eventName)}`);
        const data = await response.json();
        players = data.players || [];
        
        if (players.length === 0) {
            addPlayer(); // Add first empty player
        } else {
            renderTable();
        }
        
        updateTotals();
        updateSummary();
    } catch (error) {
        showToast('Error loading event data', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Save Data
async function saveData() {
    if (!currentEvent) {
        showToast('Please select an event first', 'error');
        return;
    }
    
    // Collect data from table
    const tbody = document.getElementById('players-tbody');
    const rows = tbody.querySelectorAll('tr');
    players = [];
    
    rows.forEach(row => {
        const player = {
            name: row.querySelector('[data-field="name"]').value,
            phone: row.querySelector('[data-field="phone"]').value,
            start: parseFloat(row.querySelector('[data-field="start"]').value) || 20,
            buyins: parseInt(row.querySelector('[data-field="buyins"]').value) || 0,
            day1: row.querySelector('[data-field="day1"]').value,
            day2: row.querySelector('[data-field="day2"]').value,
            day3: row.querySelector('[data-field="day3"]').value,
            day4: row.querySelector('[data-field="day4"]').value,
            day5: row.querySelector('[data-field="day5"]').value,
            day6: row.querySelector('[data-field="day6"]').value,
            day7: row.querySelector('[data-field="day7"]').value
        };
        
        if (player.name) {
            players.push(player);
        }
    });
    
    showLoading(true);
    try {
        const response = await fetch(`/api/save/${encodeURIComponent(currentEvent)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ players })
        });
        
        const result = await response.json();
        if (result.success) {
            showToast('✅ Data saved successfully!', 'success');
            await loadEventData(currentEvent); // Reload to get calculated P/L
        }
    } catch (error) {
        showToast('Error saving data', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Clear Event Data
async function clearEventData() {
    if (!currentEvent) {
        showToast('Please select an event first', 'error');
        return;
    }
    
    if (confirm(`⚠️ This will delete ALL player data for "${currentEvent}". Are you sure?`)) {
        try {
            const response = await fetch(`/api/clear/${encodeURIComponent(currentEvent)}`, { method: 'POST' });
            const result = await response.json();
            if (result.success) {
                players = [];
                renderTable();
                updateTotals();
                updateSummary();
                showToast('Event data cleared', 'success');
            }
        } catch (error) {
            showToast('Error clearing data', 'error');
            console.error(error);
        }
    }
}

// Add Player
function addPlayer() {
    // First, collect data from existing rows to preserve inputs
    const tbody = document.getElementById('players-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach((row, index) => {
        if (players[index]) {
            players[index] = {
                name: row.querySelector('[data-field="name"]').value,
                phone: row.querySelector('[data-field="phone"]').value,
                start: parseFloat(row.querySelector('[data-field="start"]').value) || 20,
                buyins: parseInt(row.querySelector('[data-field="buyins"]').value) || 0,
                day1: row.querySelector('[data-field="day1"]').value,
                day2: row.querySelector('[data-field="day2"]').value,
                day3: row.querySelector('[data-field="day3"]').value,
                day4: row.querySelector('[data-field="day4"]').value,
                day5: row.querySelector('[data-field="day5"]').value,
                day6: row.querySelector('[data-field="day6"]').value,
                day7: row.querySelector('[data-field="day7"]').value
            };
        }
    });
    
    // Now add new empty player
    const player = {
        name: '',
        phone: '',
        start: 20,
        buyins: 0,
        day1: '',
        day2: '',
        day3: '',
        day4: '',
        day5: '',
        day6: '',
        day7: '',
        pl: 0,
        days_played: 0
    };
    
    players.push(player);
    renderTable();
    updateTotals();
}

// Remove Player
function removePlayer(index) {
    players.splice(index, 1);
    renderTable();
    updateTotals();
    updateSummary();
}

// Render Table
function renderTable() {
    const tbody = document.getElementById('players-tbody');
    tbody.innerHTML = '';
    
    players.forEach((player, index) => {
        const row = createTableRow(player, index);
        tbody.appendChild(row);
    });
}

// Create Table Row
function createTableRow(player, index) {
    const row = document.createElement('tr');
    row.dataset.index = index;
    
    // Calculate P/L
    const pl = calculatePL(player);
    const plClass = pl > 0 ? 'positive' : pl < 0 ? 'negative' : 'neutral';
    const plSign = pl > 0 ? '+' : '';
    
    row.innerHTML = `
        <td><input type="text" data-field="name" value="${player.name || ''}" placeholder="Name"></td>
        <td><input type="tel" data-field="phone" value="${player.phone || ''}" placeholder="Phone"></td>
        <td><input type="number" data-field="start" value="${player.start || 20}" min="0"></td>
        <td><input type="number" data-field="buyins" value="${player.buyins || 0}" min="0" title="Number of $20 buy-ins"></td>
        <td><input type="number" data-field="day1" value="${player.day1 || ''}" placeholder="0"></td>
        <td><input type="number" data-field="day2" value="${player.day2 || ''}" placeholder="0"></td>
        <td><input type="number" data-field="day3" value="${player.day3 || ''}" placeholder="0"></td>
        <td><input type="number" data-field="day4" value="${player.day4 || ''}" placeholder="0"></td>
        <td><input type="number" data-field="day5" value="${player.day5 || ''}" placeholder="0"></td>
        <td><input type="number" data-field="day6" value="${player.day6 || ''}" placeholder="0"></td>
        <td><input type="number" data-field="day7" value="${player.day7 || ''}" placeholder="0"></td>
        <td class="pl-cell ${plClass}">${plSign}$${Math.abs(pl).toFixed(2)}</td>
        <td><button class="btn-remove" onclick="removePlayer(${index})">✕</button></td>
    `;
    
    // Add input listeners to update totals
    row.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', () => {
            updateTotals();
            updateSummary();
        });
    });
    
    return row;
}

// Calculate P/L for a player
function calculatePL(player) {
    const start = parseFloat(player.start) || 20;
    const buyins = parseInt(player.buyins) || 0;
    let daysPlayed = 0;
    let lastValue = start;
    
    for (let day = 1; day <= 7; day++) {
        const dayValue = parseFloat(player['day' + day]);
        if (dayValue) {
            daysPlayed++;
            lastValue = dayValue;
        }
    }
    
    if (daysPlayed > 0) {
        const totalInvestment = start + (buyins * 20);
        return lastValue - totalInvestment;
    }
    
    return 0;
}

// Update Totals Row
function updateTotals() {
    const tbody = document.getElementById('players-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    let totals = {
        buyins: 0,
        day1: 0, day2: 0, day3: 0, day4: 0,
        day5: 0, day6: 0, day7: 0, pl: 0
    };
    
    rows.forEach(row => {
        // Count buy-ins
        const buyinsInput = row.querySelector('[data-field="buyins"]');
        if (buyinsInput && buyinsInput.value) {
            totals.buyins += parseInt(buyinsInput.value) || 0;
        }
        
        for (let day = 1; day <= 7; day++) {
            const input = row.querySelector(`[data-field="day${day}"]`);
            const value = parseFloat(input.value) || 0;
            if (input.value) {
                totals[`day${day}`] += value;
            }
        }
        
        // Calculate PL from inputs
        const player = {
            start: parseFloat(row.querySelector('[data-field="start"]').value) || 20,
            buyins: parseInt(row.querySelector('[data-field="buyins"]').value) || 0,
            day1: row.querySelector('[data-field="day1"]').value,
            day2: row.querySelector('[data-field="day2"]').value,
            day3: row.querySelector('[data-field="day3"]').value,
            day4: row.querySelector('[data-field="day4"]').value,
            day5: row.querySelector('[data-field="day5"]').value,
            day6: row.querySelector('[data-field="day6"]').value,
            day7: row.querySelector('[data-field="day7"]').value
        };
        totals.pl += calculatePL(player);
    });
    
    // Update footer
    document.getElementById('total-buyins').textContent = totals.buyins;
    for (let day = 1; day <= 7; day++) {
        const value = totals[`day${day}`];
        document.getElementById(`total-day${day}`).textContent = value > 0 ? `$${value.toFixed(2)}` : '$0';
    }
    const plElement = document.getElementById('total-pl');
    const plClass = totals.pl > 0 ? 'positive' : totals.pl < 0 ? 'negative' : 'neutral';
    const plSign = totals.pl > 0 ? '+' : '';
    plElement.textContent = `${plSign}$${Math.abs(totals.pl).toFixed(2)}`;
    plElement.className = plClass;
}

// Update Summary
function updateSummary() {
    const tbody = document.getElementById('players-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    let totalPlayers = 0;
    let totalProfit = 0;
    let totalLoss = 0;
    
    rows.forEach(row => {
        const nameInput = row.querySelector('[data-field="name"]');
        if (nameInput && nameInput.value.trim()) {
            totalPlayers++;
            
            const player = {
                start: parseFloat(row.querySelector('[data-field="start"]').value) || 20,
                buyins: parseInt(row.querySelector('[data-field="buyins"]').value) || 0,
                day1: row.querySelector('[data-field="day1"]').value,
                day2: row.querySelector('[data-field="day2"]').value,
                day3: row.querySelector('[data-field="day3"]').value,
                day4: row.querySelector('[data-field="day4"]').value,
                day5: row.querySelector('[data-field="day5"]').value,
                day6: row.querySelector('[data-field="day6"]').value,
                day7: row.querySelector('[data-field="day7"]').value
            };
            
            const pl = calculatePL(player);
            if (pl > 0) totalProfit += pl;
            if (pl < 0) totalLoss += Math.abs(pl);
        }
    });
    
    document.getElementById('total-players').textContent = totalPlayers;
    document.getElementById('total-profit').textContent = `$${totalProfit.toFixed(2)}`;
    document.getElementById('total-loss').textContent = `$${totalLoss.toFixed(2)}`;
}

// Calculate Settlements
async function calculateSettlements() {
    if (!currentEvent) {
        showToast('Please select an event first', 'error');
        return;
    }
    
    showLoading(true);
    try {
        const response = await fetch(`/api/settlements/${encodeURIComponent(currentEvent)}`);
        const data = await response.json();
        
        const container = document.getElementById('settlements-container');
        container.innerHTML = '';
        
        if (data.settlements.length === 0) {
            container.innerHTML = `
                <div class="no-settlements">
                    ✅ All Even! No settlements needed
                </div>
            `;
        } else {
            data.settlements.forEach(settlement => {
                const card = document.createElement('div');
                card.className = 'settlement-card';
                card.innerHTML = `
                    <div>
                        <span class="from-player">${settlement.from}</span>
                        <span class="settlement-arrow"> → </span>
                        <span class="to-player">${settlement.to}</span>
                    </div>
                    <div class="amount">$${settlement.amount.toFixed(2)}</div>
                `;
                container.appendChild(card);
            });
            
            const summary = document.createElement('div');
            summary.className = 'summary-box';
            summary.innerHTML = `
                <p style="text-align: center; margin-top: 20px; color: #657786;">
                    💡 ${data.settlements.length} transaction${data.settlements.length > 1 ? 's' : ''} needed to settle
                </p>
            `;
            container.appendChild(summary);
        }
    } catch (error) {
        showToast('Error calculating settlements', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Refresh Charts
function refreshCharts() {
    if (players.length === 0) {
        showToast('Add players first', 'error');
        return;
    }
    
    // Destroy existing charts
    if (profitLossChart) profitLossChart.destroy();
    if (chipsTrendChart) chipsTrendChart.destroy();
    
    // P/L Bar Chart
    const plCtx = document.getElementById('profit-loss-chart').getContext('2d');
    const playersWithData = players.filter(p => p.name);
    const plData = playersWithData.map(p => calculatePL(p));
    const plColors = plData.map(pl => pl >= 0 ? '#17BF63' : '#E0245E');
    
    profitLossChart = new Chart(plCtx, {
        type: 'bar',
        data: {
            labels: playersWithData.map(p => p.name),
            datasets: [{
                label: 'Profit/Loss',
                data: plData,
                backgroundColor: plColors
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Profit/Loss by Player' },
                legend: { display: false }
            },
            scales: {
                y: {
                    ticks: {
                        callback: value => '$' + value
                    }
                }
            }
        }
    });
    
    // Chip Progression Line Chart
    const trendCtx = document.getElementById('chips-trend-chart').getContext('2d');
    const days = ['Start', 'Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
    const colors = ['#1DA1F2', '#17BF63', '#FFAD1F', '#E0245E', '#794BC4'];
    
    const datasets = playersWithData.map((player, i) => {
        const data = [player.start];
        for (let day = 1; day <= 7; day++) {
            const val = parseFloat(player['day' + day]);
            data.push(val || null);
        }
        return {
            label: player.name,
            data: data,
            borderColor: colors[i % colors.length],
            backgroundColor: colors[i % colors.length] + '33',
            tension: 0.4,
            fill: false
        };
    });
    
    chipsTrendChart = new Chart(trendCtx, {
        type: 'line',
        data: { labels: days, datasets: datasets },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Chip Progression Over Days' }
            },
            scales: {
                y: {
                    ticks: {
                        callback: value => '$' + value
                    }
                }
            }
        }
    });
    
    showToast('Charts updated', 'success');
}

// Show Loading Overlay
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

// Show Toast Notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
