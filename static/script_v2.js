// Poker Tracker v2 - With Event Management
console.log('=== SCRIPT_V2.JS LOADING ===');
console.log('Timestamp:', new Date().toISOString());

let players = [];
let currentEvent = '';
let profitLossChart = null;
let chipsTrendChart = null;
let allEvents = [];
let autoSaveTimer = null;
let isSaving = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadEvents();
    attachEventListeners();
    showHomeScreen(); // Start on home screen
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
    console.log('Attaching event listeners...');
    const createNewBtn = document.getElementById('create-new-event-btn');
    const createBtn = document.getElementById('create-event-btn');
    console.log('Create new event button:', createNewBtn);
    console.log('Create event button:', createBtn);
    
    if (createNewBtn) {
        createNewBtn.addEventListener('click', () => {
            console.log('Create new event button clicked!');
            showEventModal();
        });
    } else {
        console.error('create-new-event-btn not found!');
    }
    
    if (createBtn) {
        createBtn.addEventListener('click', () => {
            console.log('Create button clicked!');
            createEvent();
        });
    } else {
        console.error('create-event-btn not found!');
    }
    
    document.getElementById('cancel-event-btn').addEventListener('click', hideEventModal);
    document.getElementById('back-to-home').addEventListener('click', showHomeScreen);
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

// Show Home Screen
function showHomeScreen() {
    document.getElementById('home-screen').style.display = 'block';
    document.getElementById('event-view').style.display = 'none';
    currentEvent = '';
    players = [];
    loadEvents(); // Refresh events list
}

// Show Event View
function showEventView(eventName) {
    document.getElementById('home-screen').style.display = 'none';
    document.getElementById('event-view').style.display = 'block';
    document.getElementById('current-event-name').textContent = eventName;
    currentEvent = eventName;
    loadEventData(eventName);
}

// Load Events List
async function loadEvents() {
    try {
        const response = await fetch('/api/events');
        const data = await response.json();
        allEvents = data.events;
        
        renderEventsGrid();
    } catch (error) {
        showToast('Error loading events', 'error');
        console.error(error);
    }
}

// Render Events Grid on Home Screen
function renderEventsGrid() {
    const grid = document.getElementById('events-grid');
    const noEventsMsg = document.getElementById('no-events-message');
    
    if (allEvents.length === 0) {
        grid.innerHTML = '';
        noEventsMsg.style.display = 'block';
        return;
    }
    
    noEventsMsg.style.display = 'none';
    grid.innerHTML = '';
    
    allEvents.forEach(event => {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.innerHTML = `
            <div class="event-card-header">
                <h3>🎲 ${event}</h3>
            </div>
            <div class="event-card-body">
                <p class="event-date">📅 ${formatEventDate(event)}</p>
                <p class="event-description">Click to view details</p>
            </div>
            <div class="event-card-footer">
                <button class="btn btn-primary btn-small open-btn">Open Event</button>
                <button class="btn btn-danger btn-small delete-btn">🗑️ Delete</button>
            </div>
        `;
        
        card.querySelector('.open-btn').addEventListener('click', () => {
            showEventView(event);
        });
        
        card.querySelector('.delete-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteEvent(event);
        });
        
        grid.appendChild(card);
    });
}

// Format Event Date from event name
function formatEventDate(eventName) {
    // Event format: "EventName - YYYY-MM-DD"
    const parts = eventName.split(' - ');
    if (parts.length > 1) {
        const date = new Date(parts[1]);
        return date.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
    }
    return 'No date set';
}

// Handle Event Selection Change (removed, using event cards instead)
async function handleEventChange(e) {
    // Deprecated - keeping for backwards compatibility
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
    console.log('showEventModal called');
    const modal = document.getElementById('event-modal');
    console.log('Modal element:', modal);
    console.log('Modal classes before:', modal.className);
    
    // Force display with inline style AND remove hidden class
    modal.style.display = 'flex';
    modal.classList.remove('hidden');
    console.log('Modal classes after:', modal.className);
    console.log('Modal display style:', modal.style.display);
    
    document.getElementById('event-name-input').value = '';
    
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('event-date-input').value = today;
    console.log('Modal should now be visible, date set to:', today);
    
    document.getElementById('event-name-input').focus();
}

// Hide Event Modal
function hideEventModal() {
    console.log('hideEventModal called');
    const modal = document.getElementById('event-modal');
    modal.classList.add('hidden');
    modal.style.display = 'none';  // Remove inline style
    console.log('Modal hidden');
}

// Delete Event
async function deleteEvent(eventName) {
    if (!confirm(`Are you sure you want to delete "${eventName}"? This cannot be undone.`)) {
        return;
    }
    
    console.log('Deleting event:', eventName);
    showLoading(true);
    
    try {
        const response = await fetch(`/api/events/${encodeURIComponent(eventName)}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`Event "${eventName}" deleted successfully`, 'success');
            await loadEvents(); // Refresh event list
            showHomeScreen(); // Go back to home
        } else {
            showToast(result.error || 'Error deleting event', 'error');
        }
    } catch (error) {
        showToast('Error deleting event', 'error');
        console.error('Error in deleteEvent:', error);
    } finally {
        showLoading(false);
    }

// Create New Event
async function createEvent() {
    console.log('createEvent called');
    const eventName = document.getElementById('event-name-input').value.trim();
    const eventDate = document.getElementById('event-date-input').value;
    
    console.log('Event name:', eventName, 'Event date:', eventDate);
    
    if (!eventName) {
        showToast('Please enter an event name', 'error');
        return;
    }
    
    if (!eventDate) {
        showToast('Please select an event date', 'error');
        return;
    }
    
    // Format: EventName - Date
    const fullEventName = `${eventName} - ${eventDate}`;
    console.log('Creating event:', fullEventName);
    
    showLoading(true);
    try {
        const response = await fetch('/api/events', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_name: fullEventName })
        });
        
        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Result:', result);
        
        if (result.success) {
            hideEventModal();
            showToast(`Event "${fullEventName}" created!`, 'success');
            await loadEvents(); // Refresh home screen
            showEventView(fullEventName); // Open the new event
        } else {
            showToast(result.error || 'Error creating event', 'error');
            console.error('Event creation failed:', result);
        }
    } catch (error) {
        showToast('Error creating event', 'error');
        console.error('Error in createEvent:', error);
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

// Schedule Auto-Save (Debounced)
function scheduleAutoSave() {
    // Clear existing timer
    if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
    }
    
    // Set new timer - auto-save after 2 seconds of no changes
    autoSaveTimer = setTimeout(() => {
        saveData(true); // true = silent auto-save
    }, 2000);
}

// Save Data
async function saveData(silent = false) {
    if (!currentEvent) {
        if (!silent) showToast('Please select an event first', 'error');
        return;
    }
    
    if (isSaving) return; // Prevent concurrent saves
    
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
    
    if (!silent) showLoading(true);
    isSaving = true;
    
    // Show saving indicator
    if (silent) {
        const saveBtn = document.getElementById('save-data');
        if (saveBtn) {
            saveBtn.textContent = '💾 Saving...';
            saveBtn.style.opacity = '0.7';
        }
    }
    
    try {
        const response = await fetch(`/api/save/${encodeURIComponent(currentEvent)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ players })
        });
        
        const result = await response.json();
        if (result.success) {
            if (!silent) {
                showToast('✅ Data saved successfully!', 'success');
            } else {
                // Briefly show auto-save indicator
                const saveBtn = document.getElementById('save-data');
                if (saveBtn) {
                    saveBtn.textContent = '✓ Saved';
                    saveBtn.style.opacity = '1';
                    setTimeout(() => {
                        saveBtn.textContent = '💾 Save';
                    }, 2000);
                }
            }
            // Just update P/L and totals without reloading entire table (preserves current inputs)
            renderTable();
            updateTotals();
            updateSummary();
        }
    } catch (error) {
        if (!silent) showToast('Error saving data', 'error');
        console.error(error);
    } finally {
        if (!silent) showLoading(false);
        isSaving = false;
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
            scheduleAutoSave(); // Auto-save on input change
        });
        
        // Also auto-save when user finishes editing (blur)
        input.addEventListener('blur', () => {
            if (currentEvent) {
                scheduleAutoSave();
            }
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
                const isPaid = settlement.paid || false;
                
                card.innerHTML = `
                    <div class="settlement-info">
                        <div>
                            <span class="from-player">${settlement.from}</span>
                            <span class="settlement-arrow"> → </span>
                            <span class="to-player">${settlement.to}</span>
                        </div>
                        <div class="amount">$${settlement.amount.toFixed(2)}</div>
                    </div>
                    <div class="settlement-payment">
                        <button class="btn ${isPaid ? 'btn-success' : 'btn-danger'} payment-btn" 
                                data-from="${settlement.from}" 
                                data-to="${settlement.to}"
                                data-paid="${isPaid}">
                            ${isPaid ? '✓ Paid' : '✗ Not Paid'}
                        </button>
                    </div>
                `;
                
                // Add click handler for payment button
                const btn = card.querySelector('.payment-btn');
                btn.addEventListener('click', () => togglePaymentStatus(settlement.from, settlement.to, !isPaid, btn));
                
                container.appendChild(card);
            });
            
            const summary = document.createElement('div');
            summary.className = 'summary-box';
            const paidCount = data.settlements.filter(s => s.paid).length;
            summary.innerHTML = `
                <p style="text-align: center; margin-top: 20px; color: #657786;">
                    💡 ${data.settlements.length} transaction${data.settlements.length > 1 ? 's' : ''} needed to settle
                    <br>
                    <span style="color: #17bf63; font-weight: bold;">${paidCount} paid</span> | 
                    <span style="color: #e0245e; font-weight: bold;">${data.settlements.length - paidCount} unpaid</span>
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

// Toggle Payment Status
async function togglePaymentStatus(fromPlayer, toPlayer, paid, button) {
    try {
        const response = await fetch(`/api/settlements/${encodeURIComponent(currentEvent)}/mark_paid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from: fromPlayer,
                to: toPlayer,
                paid: paid
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update button appearance
            button.className = `btn ${paid ? 'btn-success' : 'btn-danger'} payment-btn`;
            button.textContent = paid ? '✓ Paid' : '✗ Not Paid';
            button.dataset.paid = paid;
            
            // Update click handler
            button.onclick = () => togglePaymentStatus(fromPlayer, toPlayer, !paid, button);
            
            showToast(result.message, 'success');
        }
    } catch (error) {
        showToast('Error updating payment status', 'error');
        console.error(error);
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
