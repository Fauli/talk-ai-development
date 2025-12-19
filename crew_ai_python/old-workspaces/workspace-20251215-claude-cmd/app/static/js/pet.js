// PixelPet - Pet Interaction JavaScript

const SPECIES_EMOJIS = {
    otter: { baby: '🦦', evolved: '🦭' },
    cat: { baby: '🐱', evolved: '🦁' },
    dragon: { baby: '🐉', evolved: '🐲' },
    axolotl: { baby: '🦎', evolved: '🦖' }
};

// Show message in the message area
function showMessage(message, type = 'info') {
    const messageArea = document.getElementById('message-area');
    if (!messageArea) return;

    messageArea.innerHTML = `<div class="message ${type}">${message}</div>`;

    // Clear message after 3 seconds
    setTimeout(() => {
        messageArea.innerHTML = '';
    }, 3000);
}

// Update pet stats display
function updateStats(pet) {
    if (!pet) return;

    // Update bars
    const hungerBar = document.getElementById('hunger-bar');
    const happinessBar = document.getElementById('happiness-bar');
    const energyBar = document.getElementById('energy-bar');

    if (hungerBar) hungerBar.style.width = `${pet.hunger}%`;
    if (happinessBar) happinessBar.style.width = `${pet.happiness}%`;
    if (energyBar) energyBar.style.width = `${pet.energy}%`;

    // Update values
    const hungerValue = document.getElementById('hunger-value');
    const happinessValue = document.getElementById('happiness-value');
    const energyValue = document.getElementById('energy-value');

    if (hungerValue) hungerValue.textContent = pet.hunger;
    if (happinessValue) happinessValue.textContent = pet.happiness;
    if (energyValue) energyValue.textContent = pet.energy;

    // Update sprite
    const petSprite = document.getElementById('pet-sprite');
    if (petSprite) {
        const emoji = SPECIES_EMOJIS[pet.species]?.[pet.stage] || '🐾';
        let content = emoji;
        if (pet.is_sleeping) {
            content += '<span class="zzz">💤</span>';
            petSprite.classList.add('sleeping');
        } else {
            petSprite.classList.remove('sleeping');
        }
        petSprite.innerHTML = content;
    }

    // Update button states
    const feedBtn = document.getElementById('feed-btn');
    const playBtn = document.getElementById('play-btn');

    if (feedBtn) feedBtn.disabled = pet.is_sleeping;
    if (playBtn) playBtn.disabled = pet.is_sleeping;

    // Update notifications
    const notificationsDiv = document.getElementById('notifications');
    if (notificationsDiv && pet.notifications) {
        notificationsDiv.innerHTML = pet.notifications
            .map(n => `<div class="notification">${n}</div>`)
            .join('');
    }
}

// Perform pet action (feed, play, sleep)
async function performAction(action) {
    try {
        const response = await fetch(`/pets/${action}`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, data.success ? 'success' : 'info');
            if (data.pet) {
                updateStats(data.pet);
            }
        } else {
            showMessage(data.detail || 'Something went wrong', 'error');
        }
    } catch (error) {
        showMessage('Failed to perform action', 'error');
        console.error('Action error:', error);
    }
}

// Create pet form handler
document.addEventListener('DOMContentLoaded', () => {
    const createPetForm = document.getElementById('create-pet-form');

    if (createPetForm) {
        createPetForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(createPetForm);
            const name = formData.get('name');
            const species = formData.get('species');

            try {
                const response = await fetch('/pets/', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, species })
                });

                if (response.ok) {
                    // Reload page to show the new pet
                    window.location.reload();
                } else {
                    const data = await response.json();
                    showMessage(data.detail || 'Failed to create pet', 'error');
                }
            } catch (error) {
                showMessage('Failed to create pet', 'error');
                console.error('Create pet error:', error);
            }
        });
    }

    // Auto-refresh pet status every 30 seconds
    const petDisplay = document.querySelector('.pet-display');
    if (petDisplay) {
        setInterval(async () => {
            try {
                const response = await fetch('/pets/', {
                    credentials: 'include'
                });
                if (response.ok) {
                    const pet = await response.json();
                    if (pet) {
                        updateStats(pet);
                    }
                }
            } catch (error) {
                console.error('Auto-refresh error:', error);
            }
        }, 30000);
    }
});
