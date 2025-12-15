// PixelPet JavaScript functionality

// Global variables
let refreshInterval;
let notificationTimeout;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePetInterface();
});

// Initialize pet interface
function initializePetInterface() {
    // Auto-refresh pet status if on game page
    if (document.querySelector('.game-container')) {
        startAutoRefresh();
    }
    
    // Initialize form handlers
    initializeFormHandlers();
    
    // Initialize action buttons
    initializeActionButtons();
}

// Start auto-refresh for pet status
function startAutoRefresh() {
    // Refresh every 30 seconds
    refreshInterval = setInterval(refreshPetStatus, 30000);
    
    // Also refresh when page becomes visible
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            refreshPetStatus();
        }
    });
}

// Refresh pet status from server
async function refreshPetStatus() {
    try {
        const response = await fetch('/pets/', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const pet = await response.json();
            updatePetDisplay(pet);
        } else if (response.status === 401) {
            // User not authenticated, redirect to login
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error refreshing pet status:', error);
    }
}

// Update pet display with new data
function updatePetDisplay(pet) {
    // Update stats
    updateStatBar('hunger', pet.hunger);
    updateStatBar('happiness', pet.happiness);
    updateStatBar('energy', pet.energy);
    
    // Update sleep status
    updateSleepStatus(pet.is_sleeping, pet.sleep_until);
    
    // Update action buttons
    updateActionButtons(pet);
    
    // Update evolution progress
    updateEvolutionProgress(pet);
    
    // Update pet sprite if evolved
    updatePetSprite(pet);
}

// Update stat bar
function updateStatBar(statName, value) {
    const statFill = document.querySelector(`.stat-fill.${statName}`);
    const statValue = document.querySelector(`.stat:has(.${statName}) .stat-value`);
    
    if (statFill) {
        statFill.style.width = value + '%';
        
        // Add visual feedback for low stats
        if (value <= 20) {
            statFill.style.animation = 'pulse 1s ease-in-out infinite';
        } else {
            statFill.style.animation = 'none';
        }
    }
    
    if (statValue) {
        statValue.textContent = value + '/100';
    }
}

// Update sleep status
function updateSleepStatus(isSleeping, sleepUntil) {
    const sleepIndicator = document.querySelector('.sleep-indicator');
    const petDisplay = document.querySelector('.pet-display');
    
    if (isSleeping && sleepUntil) {
        if (!sleepIndicator && petDisplay) {
            const indicator = document.createElement('div');
            indicator.className = 'sleep-indicator';
            const wakeTime = new Date(sleepUntil).toLocaleTimeString();
            indicator.innerHTML = `😴 Sleeping until ${wakeTime}`;
            petDisplay.appendChild(indicator);
        }
    } else {
        if (sleepIndicator) {
            sleepIndicator.remove();
        }
    }
}

// Update action buttons based on pet state
function updateActionButtons(pet) {
    const actionButtons = document.querySelectorAll('.pet-actions .btn-action:not(.evolve-btn)');
    const evolveButton = document.querySelector('.evolve-btn');
    
    // Hide/show action buttons based on sleep state
    actionButtons.forEach(btn => {
        btn.style.display = pet.is_sleeping ? 'none' : 'inline-block';
        btn.disabled = pet.is_sleeping;
    });
    
    // Update evolve button
    if (evolveButton) {
        const shouldShow = pet.can_evolve && pet.stage === 'baby';
        evolveButton.style.display = shouldShow ? 'inline-block' : 'none';
    }
}

// Update evolution progress
function updateEvolutionProgress(pet) {
    const evolutionProgress = document.querySelector('.evolution-progress');
    
    if (pet.evolution_progress && pet.stage === 'baby') {
        if (evolutionProgress) {
            const progressBar = evolutionProgress.querySelector('.evolution-fill');
            const progressText = evolutionProgress.querySelector('p');
            
            if (progressBar) {
                progressBar.style.width = pet.evolution_progress.percentage + '%';
            }
            
            if (progressText) {
                progressText.textContent = 
                    `${pet.evolution_progress.minutes_eligible.toFixed(1)} / ${pet.evolution_progress.minutes_required} minutes`;
            }
            
            evolutionProgress.style.display = 'block';
        }
    } else if (evolutionProgress) {
        evolutionProgress.style.display = 'none';
    }
}

// Update pet sprite
function updatePetSprite(pet) {
    const petSprite = document.querySelector('.pet-sprite');
    if (!petSprite) return;
    
    const sprites = {
        otter: { baby: '🦦', evolved: '🦦✨' },
        cat: { baby: '🐱', evolved: '🐱✨' },
        dragon: { baby: '🐲', evolved: '🐲✨' },
        axolotl: { baby: '🦎', evolved: '🦎✨' }
    };
    
    const sprite = sprites[pet.species]?.[pet.stage] || '🐾';
    petSprite.textContent = sprite;
}

// Initialize form handlers
function initializeFormHandlers() {
    // Pet creation form
    const createPetForm = document.getElementById('create-pet-form');
    if (createPetForm) {
        createPetForm.addEventListener('submit', handlePetCreation);
    }
    
    // Login/register forms
    const loginForm = document.querySelector('#login-tab form');
    const registerForm = document.querySelector('#register-tab form');
    
    if (registerForm) {
        registerForm.addEventListener('submit', validateRegistration);
    }
}

// Handle pet creation
async function handlePetCreation(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const petData = {
        name: formData.get('name'),
        species: formData.get('species')
    };
    
    try {
        const response = await fetch('/pets/', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(petData)
        });
        
        if (response.ok) {
            showNotification('Pet created successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/game';
            }, 1000);
        } else {
            const error = await response.json();
            showNotification('Error creating pet: ' + error.detail, 'error');
        }
    } catch (error) {
        showNotification('Error creating pet: ' + error.message, 'error');
    }
}

// Validate registration form
function validateRegistration(event) {
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-password-confirm').value;
    
    if (password !== confirmPassword) {
        event.preventDefault();
        showNotification('Passwords do not match!', 'error');
        return false;
    }
    
    if (password.length < 6) {
        event.preventDefault();
        showNotification('Password must be at least 6 characters long!', 'error');
        return false;
    }
    
    return true;
}

// Initialize action buttons
function initializeActionButtons() {
    // Add click handlers for action buttons
    const feedBtn = document.querySelector('.feed-btn');
    const playBtn = document.querySelector('.play-btn');
    const sleepBtn = document.querySelector('.sleep-btn');
    const evolveBtn = document.querySelector('.evolve-btn');
    
    if (feedBtn) feedBtn.addEventListener('click', () => performPetAction('feed'));
    if (playBtn) playBtn.addEventListener('click', () => performPetAction('play'));
    if (sleepBtn) sleepBtn.addEventListener('click', () => performPetAction('sleep'));
    if (evolveBtn) evolveBtn.addEventListener('click', () => performPetAction('evolve'));
}

// Perform pet action
async function performPetAction(action) {
    const endpoints = {
        feed: '/pets/feed',
        play: '/pets/play',
        sleep: '/pets/sleep',
        evolve: '/pets/evolve'
    };

    const actionNames = {
        feed: 'feeding',
        play: 'playing',
        sleep: 'sleeping',
        evolve: 'evolving'
    };

    const buttonIds = {
        feed: 'feed-btn',
        play: 'play-btn',
        sleep: 'sleep-btn',
        evolve: 'evolve-btn'
    };

    try {
        // Disable button during request
        const button = document.getElementById(buttonIds[action]);
        const originalText = button ? button.textContent : '';
        if (button) {
            button.disabled = true;
            button.textContent = `${actionNames[action]}...`;
        }
        
        const response = await fetch(endpoints[action], {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        // Re-enable button
        if (button) {
            button.disabled = false;
            button.textContent = originalText;
        }

        if (response.ok) {
            // Update the display with new pet data (response is PetResponse)
            updatePetDisplay(result);

            // Special handling for evolution
            if (action === 'evolve') {
                showNotification('Your pet evolved!', 'success');
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                const messages = {
                    feed: 'Fed your pet!',
                    play: 'Played with your pet!',
                    sleep: 'Your pet is now sleeping!'
                };
                showNotification(messages[action] || 'Action completed!', 'success');
            }
        } else {
            showNotification(result.detail || 'Action failed', 'error');
        }
    } catch (error) {
        showNotification('Error performing action: ' + error.message, 'error');

        // Re-enable button on error
        const button = document.getElementById(buttonIds[action]);
        if (button) {
            button.disabled = false;
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Clear existing notification
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `message ${type}`;
    notification.textContent = message;
    
    // Add to message area or create one
    let messageArea = document.getElementById('message-area');
    if (!messageArea) {
        messageArea = document.createElement('div');
        messageArea.id = 'message-area';
        messageArea.className = 'message-area';
        
        // Insert at top of main content
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(messageArea, main.firstChild);
        }
    }
    
    messageArea.appendChild(notification);
    
    // Remove notification after 5 seconds
    notificationTimeout = setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Tab switching for auth pages
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName + '-tab');
    const selectedBtn = event.target;
    
    if (selectedTab) selectedTab.classList.add('active');
    if (selectedBtn) selectedBtn.classList.add('active');
}

// Add pulse animation CSS for low stats
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
`;
document.head.appendChild(style);

// Clean up intervals when leaving page
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
});

// Global action functions (called from onclick handlers in HTML)
function feedPet() {
    performPetAction('feed');
}

function playWithPet() {
    performPetAction('play');
}

function putPetToSleep() {
    performPetAction('sleep');
}

function evolvePet() {
    performPetAction('evolve');
}

// Export functions for global access
window.showTab = showTab;
window.performPetAction = performPetAction;
window.feedPet = feedPet;
window.playWithPet = playWithPet;
window.putPetToSleep = putPetToSleep;
window.evolvePet = evolvePet;