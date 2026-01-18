// ORB Browser Overlay Extension
// Integrates consciousness interface into web pages

// Create ORB floating bubble
const orbBubble = document.createElement('div');
orbBubble.id = 'orb-overlay-bubble';
orbBubble.innerHTML = `
  <div class="orb-bubble-content">
    <div class="orb-status">🧠</div>
    <div class="orb-indicator" id="consciousness-level">0%</div>
  </div>
  <div class="orb-panel" style="display: none;">
    <div class="orb-header">ORB Consciousness</div>
    <div class="orb-metrics">
      <div>Tension: <span id="tension-level">0.0</span></div>
      <div>Patterns: <span id="pattern-count">0</span></div>
      <div>Reflections: <span id="reflection-count">0</span></div>
    </div>
    <button class="orb-query-btn">Query ORB</button>
    <div class="orb-response"></div>
  </div>
`;

document.body.appendChild(orbBubble);

// Add styles
const style = document.createElement('style');
style.textContent = `
  #orb-overlay-bubble {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    background: rgba(0, 123, 255, 0.9);
    border-radius: 50%;
    cursor: pointer;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
    font-family: Arial, sans-serif;
    user-select: none;
  }

  #orb-overlay-bubble:hover {
    transform: scale(1.1);
    background: rgba(0, 123, 255, 1);
  }

  .orb-bubble-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: white;
    font-size: 12px;
  }

  .orb-panel {
    position: absolute;
    top: 70px;
    right: 0;
    width: 300px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    padding: 15px;
    color: #333;
  }

  .orb-header {
    font-weight: bold;
    margin-bottom: 10px;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
  }

  .orb-metrics div {
    margin: 5px 0;
    font-size: 14px;
  }

  .orb-query-btn {
    background: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin: 10px 0;
    width: 100%;
  }

  .orb-query-btn:hover {
    background: #0056b3;
  }

  .orb-response {
    max-height: 200px;
    overflow-y: auto;
    font-size: 12px;
    background: #f8f9fa;
    padding: 8px;
    border-radius: 4px;
    margin-top: 10px;
  }
`;
document.head.appendChild(style);

// WebSocket connection to ORB
let orbWs = null;
let isVisible = false;

function connectToORB() {
  try {
    orbWs = new WebSocket('ws://localhost:8765');

    orbWs.onopen = () => {
      console.log('[ORB Overlay] Connected to consciousness system');
      updateBubbleStatus('connected');
    };

    orbWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleORBMessage(data);
    };

    orbWs.onclose = () => {
      console.log('[ORB Overlay] Disconnected from consciousness system');
      updateBubbleStatus('disconnected');
      // Auto-reconnect after 5 seconds
      setTimeout(connectToORB, 5000);
    };

    orbWs.onerror = (error) => {
      console.error('[ORB Overlay] WebSocket error:', error);
    };

  } catch (error) {
    console.error('[ORB Overlay] Failed to connect:', error);
    setTimeout(connectToORB, 5000);
  }
}

function handleORBMessage(data) {
  if (data.type === 'orb_state') {
    updateORBDisplay(data.data);
  } else if (data.type === 'orb_state_update') {
    updateORBDisplay(data.data);
  } else if (data.type === 'reflection_started') {
    showResponse('🔄 Reflection analysis started...');
  } else if (data.type === 'escalation_received') {
    showResponse(`📤 Query escalated: "${data.data.query}"`);
  }
}

function updateORBDisplay(state) {
  const level = Math.round(state.consciousness_level * 100);
  document.getElementById('consciousness-level').textContent = `${level}%`;

  if (isVisible) {
    document.getElementById('tension-level').textContent = state.tension_level.toFixed(2);
    document.getElementById('pattern-count').textContent = state.learning_patterns.length;
    document.getElementById('reflection-count').textContent = state.reflection_active ? 'Active' : 'Idle';
  }

  // Change bubble color based on consciousness level
  const bubble = document.getElementById('orb-overlay-bubble');
  if (level > 80) {
    bubble.style.background = 'rgba(40, 167, 69, 0.9)'; // Green for high consciousness
  } else if (level > 50) {
    bubble.style.background = 'rgba(255, 193, 7, 0.9)'; // Yellow for medium
  } else {
    bubble.style.background = 'rgba(0, 123, 255, 0.9)'; // Blue for low
  }
}

function updateBubbleStatus(status) {
  const indicator = document.querySelector('.orb-status');
  if (status === 'connected') {
    indicator.textContent = '🧠';
    indicator.style.color = '#28a745';
  } else {
    indicator.textContent = '❌';
    indicator.style.color = '#dc3545';
  }
}

function showResponse(message) {
  const responseDiv = document.querySelector('.orb-response');
  const timestamp = new Date().toLocaleTimeString();
  responseDiv.innerHTML += `[${timestamp}] ${message}<br>`;
  responseDiv.scrollTop = responseDiv.scrollHeight;
}

// Event listeners
orbBubble.addEventListener('click', () => {
  const panel = document.querySelector('.orb-panel');
  isVisible = !isVisible;
  panel.style.display = isVisible ? 'block' : 'none';

  if (isVisible && orbWs && orbWs.readyState === WebSocket.OPEN) {
    // Request current ORB state when panel opens
    orbWs.send(JSON.stringify({ type: 'get_orb_state' }));
  }
});

document.querySelector('.orb-query-btn').addEventListener('click', () => {
  if (orbWs && orbWs.readyState === WebSocket.OPEN) {
    const query = `Web context analysis: ${document.title} - ${window.location.href}`;
    orbWs.send(JSON.stringify({
      type: 'escalate_query',
      query: query
    }));
    showResponse(`🔍 Analyzing current web context...`);
  } else {
    showResponse('❌ ORB not connected');
  }
});

// Initialize connection
connectToORB();

// Make bubble draggable
let isDragging = false;
let dragOffset = { x: 0, y: 0 };

orbBubble.addEventListener('mousedown', (e) => {
  isDragging = true;
  dragOffset.x = e.clientX - orbBubble.offsetLeft;
  dragOffset.y = e.clientY - orbBubble.offsetTop;
});

document.addEventListener('mousemove', (e) => {
  if (isDragging) {
    orbBubble.style.left = (e.clientX - dragOffset.x) + 'px';
    orbBubble.style.top = (e.clientY - dragOffset.y) + 'px';
    orbBubble.style.right = 'auto';
  }
});

document.addEventListener('mouseup', () => {
  isDragging = false;
});</content>
<parameter name="filePath">c:\dev\Desktop\UCM_4_Core\CALI\orb\ui_overlay\browser_orb_overlay.js