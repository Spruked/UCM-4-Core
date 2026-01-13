// UCM_4_Core/CALI/orb/ui_overlay/electron/renderer.js

class ORBRenderer {
    constructor() {
        this.orbState = {
            status: 'observing',
            depth: 0.0,
            tension: 0.0,
            emergence_ready: false
        };

        this.currentResolution = null;
        this.applicationContext = null;

        this.initializeUI();
        this.setupEventListeners();
    }

    initializeUI() {
        this.orbBubble = document.getElementById('orbBubble');
        this.orbStatus = document.getElementById('orbStatus');
        this.depthFill = document.getElementById('depthFill');
        this.resolutionOverlay = document.getElementById('resolutionOverlay');
        this.resolutionContent = document.getElementById('resolutionContent');
        this.resolutionWorker = document.getElementById('resolutionWorker');

        // Update initial state
        this.updateOrbDisplay();
    }

    setupEventListeners() {
        // Bubble click handler
        this.orbBubble.addEventListener('click', () => {
            this.handleBubbleClick();
        });

        // Listen for main process events
        if (window.electronAPI) {
            window.electronAPI.onApplicationContext((event, context) => {
                this.applicationContext = context;
                this.updateApplicationBehavior();
            });

            window.electronAPI.onShowResolution((event, data) => {
                this.showResolutionInterface(data);
            });

            window.electronAPI.onUpdateOrbState((event, state) => {
                this.updateOrbState(state);
            });
        }

        // Handle window blur (user clicked elsewhere)
        window.addEventListener('blur', () => {
            // Could hide or minimize the bubble
        });
    }

    updateOrbState(newState) {
        this.orbState = { ...this.orbState, ...newState };
        this.updateOrbDisplay();
    }

    updateOrbDisplay() {
        const { status, depth, tension, emergence_ready } = this.orbState;

        // Update status text
        this.orbStatus.textContent = status;

        // Update depth indicator
        this.depthFill.style.width = `${Math.min(100, depth * 100)}%`;

        // Update visual state
        this.orbBubble.className = 'orb-bubble';

        if (status === 'resolving') {
            this.orbBubble.classList.add('resolving');
        } else if (emergence_ready) {
            this.orbBubble.classList.add('emergence-ready');
        } else if (tension > 0.7) {
            this.orbBubble.classList.add('tension-high');
        }
    }

    updateApplicationBehavior() {
        if (!this.applicationContext) return;

        const appTitle = this.applicationContext.title || '';

        // Auto-hide behavior for certain applications
        const shouldHide = this.shouldAutoHide(appTitle);

        if (shouldHide && this.orbBubble.style.display !== 'none') {
            // Send hide command to main process
            if (window.electronAPI) {
                window.electronAPI.sendToPython({
                    type: 'ui_command',
                    command: 'auto_hide',
                    reason: 'application_context',
                    application: appTitle
                });
            }
        }
    }

    shouldAutoHide(appTitle) {
        const hideApps = [
            'youtube', 'netflix', 'prime video', 'hulu',
            'fullscreen', 'game', 'vlc', 'media player'
        ];

        return hideApps.some(app =>
            appTitle.toLowerCase().includes(app.toLowerCase())
        );
    }

    handleBubbleClick() {
        // Send interaction to Python
        if (window.electronAPI) {
            window.electronAPI.sendToPython({
                type: 'user_interaction',
                action: 'bubble_click',
                state: this.orbState,
                context: this.applicationContext
            });
        }
    }

    showResolutionInterface(data) {
        this.currentResolution = data;

        // Update header
        this.resolutionWorker.textContent = `Worker ${data.worker_id || 'unknown'} escalation`;

        // Build content
        let content = '';

        if (data.guidance) {
            content += `<div class="guidance-item">`;
            content += `<strong>ORB Guidance:</strong> ${data.guidance}`;
            content += `</div>`;

            if (data.confidence !== undefined) {
                content += `<div>Confidence: ${(data.confidence * 100).toFixed(1)}%</div>`;
                content += `<div class="confidence-bar">`;
                content += `<div class="confidence-fill" style="width: ${data.confidence * 100}%"></div>`;
                content += `</div>`;
            }
        }

        if (data.observations && data.observations.length > 0) {
            content += `<div style="margin-top: 16px;">`;
            content += `<strong>Based on ${data.observations} observations</strong>`;
            content += `</div>`;
        }

        if (data.context) {
            content += `<div style="margin-top: 12px; font-size: 12px; opacity: 0.8;">`;
            content += `<strong>Context:</strong> ${JSON.stringify(data.context, null, 2)}`;
            content += `</div>`;
        }

        this.resolutionContent.innerHTML = content;

        // Show overlay
        this.resolutionOverlay.style.display = 'flex';
    }

    hideResolutionInterface() {
        this.resolutionOverlay.style.display = 'none';
        this.currentResolution = null;
    }
}

// Global functions for button handlers
function acceptResolution() {
    if (window.orbRenderer && window.orbRenderer.currentResolution) {
        window.orbRenderer.sendResolutionResponse('accept');
    }
}

function rejectResolution() {
    if (window.orbRenderer && window.orbRenderer.currentResolution) {
        window.orbRenderer.sendResolutionResponse('reject');
    }
}

function escalateToHuman() {
    if (window.orbRenderer && window.orbRenderer.currentResolution) {
        window.orbRenderer.sendResolutionResponse('escalate');
    }
}

// Add sendResolutionResponse method to ORBRenderer
ORBRenderer.prototype.sendResolutionResponse = function(action) {
    if (window.electronAPI) {
        window.electronAPI.sendToPython({
            type: 'resolution_response',
            action: action,
            resolution_data: this.currentResolution,
            timestamp: new Date().toISOString()
        });
    }

    this.hideResolutionInterface();
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.orbRenderer = new ORBRenderer();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.electronAPI) {
        window.electronAPI.removeAllListeners('application-context');
        window.electronAPI.removeAllListeners('show-resolution');
        window.electronAPI.removeAllListeners('update-orb-state');
    }
});