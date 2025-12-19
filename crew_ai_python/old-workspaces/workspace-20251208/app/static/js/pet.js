// PixelPet JavaScript for interactive functionality

class PetInterface {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadPetStatus();
        this.startStatusUpdates();
    }

    bindEvents() {
        // Create pet form
        const createForm = document.getElementById('create-pet-form');
        if (createForm) {
            createForm.addEventListener('submit', (e) => this.createPet(e));
        }

        // Action buttons
        document.getElementById('feed-btn')?.addEventListener('click', () => this.performAction('feed'));
        document.getElementById('play-btn')?.addEventListener('click', () => this.performAction('play'));
        document.getElementById('sleep-btn')?.addEventListener('click', () => this.performAction('sleep'));
        document.getElementById('evolve-btn')?.addEventListener('click', () => this.performAction('evolve'));
    }

    async createPet(event) {
        event.preventDefault();
        const form = event.target;
        const name = form.querySelector('[name="name"]').value;
        const species = form.querySelector('[name="species"]').value;

        try {
            const response = await fetch('/pets/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({ name, species })
            });

            if (response.ok) {
                const pet = await response.json();
                this.showMessage('Pet created successfully!', 'success');
                this.showPetDisplay();
                this.updatePetDisplay(pet);
            } else {
                const error = await response.json();
                this.showMessage(error.detail || 'Failed to create pet', 'error');
            }
        } catch (error) {
            this.showMessage('Error creating pet', 'error');
        }
    }

    async loadPetStatus() {
        try {
            const response = await fetch('/pets/', {
                credentials: 'include'
            });

            if (response.ok) {
                const pet = await response.json();
                this.showPetDisplay();
                this.updatePetDisplay(pet);
            } else if (response.status === 404) {
                // No pet found, show create form
                this.showCreateForm();
            } else if (response.status === 401) {
                // Not logged in, that's okay - page will handle it
                console.log('Not authenticated');
            }
        } catch (error) {
            console.error('Error loading pet status:', error);
        }
    }

    async performAction(action) {
        try {
            const response = await fetch(`/pets/${action}`, {
                method: 'POST',
                credentials: 'include'
            });

            const result = await response.json();

            if (response.ok) {
                this.showMessage(result.message, 'success');
                this.updatePetDisplay(result.pet);
            } else {
                this.showMessage(result.detail || `Failed to ${action}`, 'error');
            }
        } catch (error) {
            this.showMessage(`Error performing ${action}`, 'error');
        }
    }

    updatePetDisplay(pet) {
        // Update pet name and image
        const nameDisplay = document.getElementById('pet-name-display');
        if (nameDisplay) {
            nameDisplay.textContent = pet.name;
        }

        const petImage = document.getElementById('pet-image');
        if (petImage) {
            const imagePath = `/static/img/${pet.species}${pet.stage === 'evolved' ? '_evolved' : ''}.png`;
            petImage.src = imagePath;
            petImage.alt = `${pet.name} the ${pet.species}`;
            // Fallback to emoji if image doesn't exist
            petImage.onerror = () => {
                const emojis = { otter: '🦦', cat: '🐱', dragon: '🐉', axolotl: '🦎' };
                const container = petImage.parentElement;
                container.innerHTML = `<div style="font-size: 60px;">${emojis[pet.species] || '🐾'}</div>`;
            };
        }

        // Update stats
        this.updateStat('hunger', pet.hunger);
        this.updateStat('happiness', pet.happiness);
        this.updateStat('energy', pet.energy);

        // Update sleep status
        const sleepOverlay = document.getElementById('sleep-overlay');
        if (sleepOverlay) {
            if (pet.is_sleeping) {
                sleepOverlay.style.display = 'flex';
                this.disableActionButtons(true);
            } else {
                sleepOverlay.style.display = 'none';
                this.disableActionButtons(false);
            }
        }

        // Update evolution button
        const evolveBtn = document.getElementById('evolve-btn');
        if (evolveBtn) {
            if (pet.can_evolve) {
                evolveBtn.style.display = 'inline-block';
            } else {
                evolveBtn.style.display = 'none';
            }
        }
    }

    updateStat(statName, value) {
        const bar = document.getElementById(`${statName}-bar`);
        const valueSpan = document.getElementById(`${statName}-value`);

        if (bar && valueSpan) {
            bar.style.width = `${value}%`;
            valueSpan.textContent = value;
        }
    }

    disableActionButtons(disabled) {
        const buttons = ['feed-btn', 'play-btn', 'sleep-btn'];
        buttons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.disabled = disabled;
                btn.style.opacity = disabled ? '0.5' : '1';
            }
        });
    }

    showPetDisplay() {
        const noPet = document.getElementById('no-pet');
        const petDisplay = document.getElementById('pet-display');
        if (noPet) noPet.style.display = 'none';
        if (petDisplay) petDisplay.style.display = 'block';
    }

    showCreateForm() {
        const noPet = document.getElementById('no-pet');
        const petDisplay = document.getElementById('pet-display');
        if (noPet) noPet.style.display = 'block';
        if (petDisplay) petDisplay.style.display = 'none';
    }

    showMessage(message, type = 'info') {
        const messageArea = document.getElementById('message-area');
        if (messageArea) {
            messageArea.textContent = message;
            messageArea.className = `message-area ${type}`;

            // Clear message after 3 seconds
            setTimeout(() => {
                messageArea.textContent = '';
                messageArea.className = 'message-area';
            }, 3000);
        }
    }

    startStatusUpdates() {
        // Update pet status every 30 seconds
        setInterval(() => {
            const petDisplay = document.getElementById('pet-display');
            if (petDisplay && petDisplay.style.display !== 'none') {
                this.loadPetStatus();
            }
        }, 30000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PetInterface();
});
