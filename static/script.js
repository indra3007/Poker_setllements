// Poker Tracker Web App - JavaScript (Table Version)

let players = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadData();
    attachEventListeners();
});

// Tab Navigation
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

// Attach Event Listeners
function attachEventListeners() {
    document.getElementById('save-data').addEventListener('click', saveData);
    document.getElementById('calculate-settlements').addEventListener('click', calculateSettlements);
    document.getElementById('refresh-charts').addEventListener('click', refreshCharts);
    
    const clearBtn = document.getElementById('clear-data');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAllData);
    }
    
    // Player chip click handlers
    document.querySelectorAll('.player-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            const name = this.getAttribute('data-name');
            addPlayer(name);
        });
    });
    
    // Custom player input handler
    document.getElementById('add-custom-player').addEventListener('click', function() {
        const nameInput = document.getElementById('custom-player-name');
        const name = nameInput.value.trim();
        if (name) {
            addPlayer(name);
            nameInput.value = '';
        } else {
            showToast('Please enter a player name', 'error');
        }
    });
    
    // Allow Enter key in custom player input
    document.getElementById('custom-player-name').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('add-custom-player').click();
        }
    });
}

// Load Data from Server
async function loadData() {
    showLoading(true);
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        players = data.players || [];
        
        if (players.length === 0) {
            // Add default empty player
            addPlayer();
        } else {
            renderTable();
        }
        
        updateTotals();
        updateSummary();
    } catch (error) {
        showToast('Error loading data', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Save Data to Server
async function saveData() {
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
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ players })
        });
        
        const result = await response.json();
        if (result.success) {
            showToast('✅ Data saved successfully!', 'success');
            await loadData(); // Reload to get calculated P/L
        }
    } catch (error) {
        showToast('Error saving data', 'error');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Clear All Data
async function clearAllData() {
    if (confirm('⚠️ This will delete ALL player data. Are you sure?')) {
        try {
            const response = await fetch('/api/clear', { method: 'POST' });
            const result = await response.json();
            if (result.success) {
                players = [];
                renderTable();
                updateTotals();
                updateSummary();
                showToast('All data cleared', 'success');
            }
        } catch (error) {
            showToast('Error clearing data', 'error');
            console.error(error);
        }
    }
}

// Add Player
function addPlayer(name = '') {
    // Check if player already exists
    if (name && players.some(p => p.name.toLowerCase() === name.toLowerCase())) {
        showToast(`${name} is already added!`, 'error');
        return;
    }
    
    // First, collect data from existing rows to preserve inputs
    const tbody = document.getElementById('players-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach((row, index) => {
        if (players[index]) {
            // Update player data from current input values
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
    
    // Now add new player with optional name
    const player = {
        name: name,
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
    updatePlayerChips();
    if (name) {
        showToast(`${name} added!`, 'success');
    }
    updateTotals();
    updateSummary();
    
    // Focus on the name input of the new row
    const lastRow = tbody.lastElementChild;
    if (lastRow) {
        const nameInput = lastRow.querySelector('[data-field="name"]');
        if (nameInput) nameInput.focus();
    }
}

// Remove Player
function removePlayer(index) {
    if (confirm('Remove this player?')) {
        players.splice(index, 1);
        renderTable();
        updateTotals();
        updateSummary();
        showToast('Player removed', 'success');
    }
}

// Update player chip states
function updatePlayerChips() {
    const existingNames = players.map(p => p.name.toLowerCase());
    document.querySelectorAll('.player-chip').forEach(chip => {
        const chipName = chip.getAttribute('data-name').toLowerCase();
        if (existingNames.includes(chipName)) {
            chip.classList.add('added');
            chip.disabled = true;
        } else {
            chip.classList.remove('added');
            chip.disabled = false;
        }
    });
}

// Update player chip states
function updatePlayerChips() {
    const existingNames = players.map(p => p.name.toLowerCase());
    document.querySelectorAll('.player-chip').forEach(chip => {
        const chipName = chip.getAttribute('data-name').toLowerCase();
        if (existingNames.includes(chipName)) {
            chip.classList.add('added');
            chip.disabled = true;
        } else {
            chip.classList.remove('added');
            chip.disabled = false;
        }
    });
}

// Render Table
function renderTable() {
    const tbody = document.getElementById('players-tbody');
    tbody.innerHTML = '';
    
    players.forEach((player, index) => {
        const row = createTableRow(player, index);
        tbody.appendChild(row);
    });
    
    updatePlayerChips();
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
        <td><input type="number" data-field="start" value="${player.start || 20}" min="0" step="1"></td>
        <td><input type="number" data-field="buyins" value="${player.buyins || 0}" min="0" step="1" title="Number of $20 buy-ins"></td>
        <td><input type="number" data-field="day1" value="${player.day1 || ''}" placeholder="0" step="0.01"></td>
        <td><input type="number" data-field="day2" value="${player.day2 || ''}" placeholder="0" step="0.01"></td>
        <td><input type="number" data-field="day3" value="${player.day3 || ''}" placeholder="0" step="0.01"></td>
        <td><input type="number" data-field="day4" value="${player.day4 || ''}" placeholder="0" step="0.01"></td>
        <td><input type="number" data-field="day5" value="${player.day5 || ''}" placeholder="0" step="0.01"></td>
        <td><input type="number" data-field="day6" value="${player.day6 || ''}" placeholder="0" step="0.01"></td>
        <td><input type="number" data-field="day7" value="${player.day7 || ''}" placeholder="0" step="0.01"></td>
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
        
        // Calculate PL from row
        const name = row.querySelector('[data-field="name"]').value;
        if (name) {
            const start = parseFloat(row.querySelector('[data-field="start"]').value) || 20;
            const buyins = parseInt(row.querySelector('[data-field="buyins"]').value) || 0;
            let daysPlayed = 0;
            let lastValue = start;
            
            for (let day = 1; day <= 7; day++) {
                const dayValue = parseFloat(row.querySelector(`[data-field="day${day}"]`).value);
                if (dayValue) {
                    daysPlayed++;
                    lastValue = dayValue;
                }
            }
            
            if (daysPlayed > 0) {
                const totalInvestment = start + (buyins * 20);
                totals.pl += (lastValue - totalInvestment);
            }
        }
    });
    
    // Update footer
    const buyinsCell = document.getElementById('total-buyins');
    if (buyinsCell) {
        buyinsCell.textContent = totals.buyins;
    }
    
    for (let day = 1; day <= 7; day++) {
        const cell = document.getElementById(`total-day${day}`);
        if (cell) {
            cell.textContent = totals[`day${day}`] ? `$${totals[`day${day}`].toFixed(2)}` : '$0';
        }
    }
    
    const plCell = document.getElementById('total-pl');
    if (plCell) {
        const plClass = totals.pl > 0 ? 'positive' : totals.pl < 0 ? 'negative' : 'neutral';
        const plSign = totals.pl > 0 ? '+' : '';
        plCell.textContent = `${plSign}$${Math.abs(totals.pl).toFixed(2)}`;
        plCell.className = `pl-cell ${plClass}`;
    }
}

// Update Summary
function updateSummary() {
    const tbody = document.getElementById('players-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    let totalPlayers = 0;
    let totalProfit = 0;
    let totalLoss = 0;
    
    rows.forEach(row => {
        const name = row.querySelector('[data-field="name"]').value;
        if (name) {
            totalPlayers++;
            
            // Calculate P/L
            const start = parseFloat(row.querySelector('[data-field="start"]').value) || 20;
            const buyins = parseInt(row.querySelector('[data-field="buyins"]').value) || 0;
            let daysPlayed = 0;
            let lastValue = start;
            
            for (let day = 1; day <= 7; day++) {
                const dayValue = parseFloat(row.querySelector(`[data-field="day${day}"]`).value);
                if (dayValue) {
                    daysPlayed++;
                    lastValue = dayValue;
                }
            }
            
            if (daysPlayed > 0) {
                const totalInvestment = start + (buyins * 20);
                const pl = lastValue - totalInvestment;
                
                if (pl > 0) totalProfit += pl;
                if (pl < 0) totalLoss += Math.abs(pl);
            }
        }
    });
    
    document.getElementById('total-players').textContent = totalPlayers;
    document.getElementById('total-profit').textContent = `$${totalProfit.toFixed(2)}`;
    document.getElementById('total-loss').textContent = `$${totalLoss.toFixed(2)}`;
}

// Calculate Settlements
async function calculateSettlements() {
    showLoading(true);
    try {
        const response = await fetch('/api/settlements');
        const data = await response.json();
        
        const container = document.getElementById('settlements-container');
        container.innerHTML = '';
        
        if (data.settlements.length === 0) {
            container.innerHTML = `
                <div class="info-box">
                    <p>📊 No settlements needed</p>
                    <p>Make sure you've saved player data first!</p>
                </div>
            `;
        } else {
            data.settlements.forEach(settlement => {
                const card = document.createElement('div');
                card.className = 'settlement-card';
                card.innerHTML = `
                    <div class="settlement-from">${settlement.from}</div>
                    <div class="settlement-arrow">→</div>
                    <div class="settlement-to">${settlement.to}</div>
                    <div class="settlement-amount">$${settlement.amount.toFixed(2)}</div>
                `;
                container.appendChild(card);
            });
            
            // Add summary
            const summary = document.createElement('div');
            summary.className = 'summary-box';
            summary.innerHTML = `
                <h3>💡 Settlement Summary</h3>
                <p style="text-align: center; margin-top: 10px;">
                    ${data.settlements.length} transaction${data.settlements.length > 1 ? 's' : ''} needed
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
    toast.className = `toast ${type}`;
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Chart instances
let profitLossChart = null;
let chipsTrendChart = null;

// Refresh Charts
function refreshCharts() {
    const tbody = document.getElementById('players-tbody');
    const rows = tbody.querySelectorAll('tr');
    
    if (rows.length === 0) {
        showToast('Add players first!', 'error');
        return;
    }
    
    const playerNames = [];
    const playerPL = [];
    const playerColors = [];
    
    rows.forEach(row => {
        const name = row.querySelector('[data-field="name"]').value;
        if (name) {
            const start = parseFloat(row.querySelector('[data-field="start"]').value) || 20;
            const buyins = parseInt(row.querySelector('[data-field="buyins"]').value) || 0;
            let daysPlayed = 0;
            let lastValue = start;
            
            for (let day = 1; day <= 7; day++) {
                const dayValue = parseFloat(row.querySelector(`[data-field="day${day}"]`).value);
                if (dayValue) {
                    daysPlayed++;
                    lastValue = dayValue;
                }
            }
            
            if (daysPlayed > 0) {
                const totalInvestment = start + (buyins * 20);
                const pl = lastValue - totalInvestment;
                playerNames.push(name);
                playerPL.push(pl);
                playerColors.push(pl >= 0 ? '#17BF63' : '#E0245E');
            }
        }
    });
    
    // Profit/Loss Bar Chart
    const plCtx = document.getElementById('profit-loss-chart').getContext('2d');
    if (profitLossChart) profitLossChart.destroy();
    
    profitLossChart = new Chart(plCtx, {
        type: 'bar',
        data: {
            labels: playerNames,
            datasets: [{
                label: 'Profit/Loss ($)',
                data: playerPL,
                backgroundColor: playerColors,
                borderColor: playerColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: '📊 Player Profit/Loss',
                    font: { size: 16, weight: 'bold' }
                },
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#E1E8ED' },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
    
    // Chips Trend Line Chart
    const trendCtx = document.getElementById('chips-trend-chart').getContext('2d');
    if (chipsTrendChart) chipsTrendChart.destroy();
    
    const datasets = [];
    const colors = ['#1DA1F2', '#17BF63', '#FFAD1F', '#E0245E', '#794BC4'];
    
    rows.forEach((row, index) => {
        const name = row.querySelector('[data-field="name"]').value;
        if (name) {
            const chipData = [parseFloat(row.querySelector('[data-field="start"]').value) || 20];
            
            for (let day = 1; day <= 7; day++) {
                const dayValue = parseFloat(row.querySelector(`[data-field="day${day}"]`).value);
                if (dayValue) {
                    chipData.push(dayValue);
                } else {
                    break;
                }
            }
            
            if (chipData.length > 1) {
                datasets.push({
                    label: name,
                    data: chipData,
                    borderColor: colors[index % colors.length],
                    backgroundColor: colors[index % colors.length] + '33',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false
                });
            }
        }
    });
    
    chipsTrendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: ['Start', 'Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'].slice(0, Math.max(...datasets.map(d => d.data.length))),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: '📈 Chip Count Progression',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#E1E8ED' },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
    
    showToast('Charts updated!', 'success');
}
