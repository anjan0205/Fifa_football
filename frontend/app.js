// FIFA World Cup AI Command Center - Application Logic

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  lucide.createIcons();

  // State Management
  const state = {
    currentRole: 'operator',
    activePage: 'page-landing',
    isRecordingVoice: false,
    activeDoc: 'rules',
    theme: 'dark',
    accessibility: {
      colorFilter: 'none',
      dyslexicFriendly: false,
      textZoom: false,
      screenReader: false
    },
    metrics: {
      capacity: 78540,
      activeIncidents: 3,
      energySaving: 14.2,
      emissionsOffset: 98.2,
      gateCFlow: 152
    },
    emergencyActive: false
  };

  // Mock Database for RAG (Knowledge Base Chunks)
  const knowledgeBase = {
    rules: [
      { id: 1, text: "Bag Policy: Only clear bags smaller than 12x6x12 inches are allowed. Small clutch bags (4.5x6.5 inches) do not need to be clear." },
      { id: 2, text: "Prohibited Items: Weapons, lasers, professional cameras (lenses > 6 inches), glass bottles, cans, banners larger than 3x5 feet, and air horns." },
      { id: 3, text: "Re-entry Policy: Re-entry is strictly prohibited. Once you exit MetLife Stadium, you cannot enter again using the same ticket." }
    ],
    evac: [
      { id: 4, text: "Emergency Evacuation: Exit planning directs fans to use the closest stairwell. Elevators and escalators will be automatically shut down during fire alarms." },
      { id: 5, text: "Emergency Routes: East gates (Gate C and D) lead to main parking lot assembly zones. North Gate (Gate B) leads to shuttle terminal zones." },
      { id: 6, text: "Medical Rooms: First Aid stations are located near Section 109, Section 143, Section 216, and Section 302." }
    ],
    tickets: [
      { id: 7, text: "Mobile Ticket policy: All tickets must be digital via the official FIFA App. Paper printouts or screenshots of QR codes will not scan." },
      { id: 8, text: "Child Tickets: Children under 2 years old do not require a ticket but must sit on an adult's lap during the match." },
      { id: 9, text: "Ticket Assistance: Resolution offices are located adjacent to Gate A and Gate C ticketing booths." }
    ],
    transit: [
      { id: 10, text: "NJ Transit Trains: Express service to Penn Station NYC departs every 8-12 minutes starting immediately in the 2nd half of matches." },
      { id: 11, text: "FIFA Shuttle Buses: Free shuttle buses run between MetLife Stadium Lot K and downtown park-and-ride hubs every 5 minutes." },
      { id: 12, text: "Uber/Lyft Rideshare: Designated pick-up zone is located at Lot G, a 15-minute walk from Gate D." }
    ]
  };

  // Agent Thinking Simulations
  const agentThoughts = {
    navigation: [
      "Navigation Agent: Fetching fan seat: Sec 112, Row 12, Seat 4.",
      "Navigation Agent: Accessing accessibility profile: wheelchair=true.",
      "Navigation Agent: Routing active. Calculated ramp path from Gate C via West Elevators. Estimated distance: 220m."
    ],
    crowd: [
      "Crowd Agent: Analyzing live gate telemetry.",
      "Crowd Agent: Queue bottleneck detected at Gate B scanners. Estimated delay: 14.5 mins.",
      "Crowd Agent: Generating recommendation: Direct new arrivals to Gate A. Stagger ticket scanning teams."
    ],
    emergency: [
      "Emergency Agent: HAZARD DETECTED! Smoke alarm sector B concourse.",
      "Emergency Agent: Synthesizing safe exit vectors. Sector B path blocked.",
      "Emergency Agent: Routing evacuation lines towards East gates. Initiating fire system audio broadcast."
    ],
    transport: [
      "Transport Agent: Analyzing post-match rideshare and train station parking grids.",
      "Transport Agent: High congestion alert for Lot G rideshare queue.",
      "Transport Agent: Recommending staging shuttle bus release times: stagger intervals by 8 minutes."
    ],
    volunteer: [
      "Volunteer Agent: Parsing dispatcher queue.",
      "Volunteer Agent: Task assigned to Support Team 4: Scanner assistance at Gate B.",
      "Volunteer Agent: Generating Spanish-to-English translation cards."
    ]
  };

  // -------------------------------------------------------------
  // Router Logic
  // -------------------------------------------------------------
  const menuItems = document.querySelectorAll('.menu-item');
  const pages = document.querySelectorAll('.page-container');
  const pageHeaderTitle = document.getElementById('page-header-title');

  function navigateToPage(pageId) {
    state.activePage = pageId;
    
    // Hide all pages, show target
    pages.forEach(p => p.classList.remove('active-page'));
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
      targetPage.classList.add('active-page');
    }

    // Set active class on matching menu items
    menuItems.forEach(item => {
      if (item.getAttribute('data-target') === pageId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Update Header Title
    const activeItem = document.querySelector(`.menu-item[data-target="${pageId}"]`);
    if (activeItem) {
      pageHeaderTitle.textContent = activeItem.textContent.trim();
    }
  }

  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      const pageId = item.getAttribute('data-target');
      navigateToPage(pageId);
    });
  });

  // -------------------------------------------------------------
  // Role Switcher Logic
  // -------------------------------------------------------------
  const roleSelect = document.getElementById('role-select');
  const userAvatar = document.getElementById('user-avatar-initial');
  const userName = document.getElementById('user-display-name');
  const userRole = document.getElementById('user-display-role');

  const roleProfiles = {
    operator: {
      initial: 'O',
      name: 'FIFA Operator',
      role: 'Level 3 Admin',
      defaultPage: 'page-landing'
    },
    volunteer: {
      initial: 'V',
      name: 'Sarah Connor',
      role: 'Gate B Volunteer',
      defaultPage: 'page-volunteer'
    },
    fan: {
      initial: 'F',
      name: 'Alex Johnson',
      role: 'Visitor (Sec 112)',
      defaultPage: 'page-fan'
    }
  };

  roleSelect.addEventListener('change', (e) => {
    const role = e.target.value;
    state.currentRole = role;
    const profile = roleProfiles[role];
    
    // Update sidebar profile
    userAvatar.textContent = profile.initial;
    userName.textContent = profile.name;
    userRole.textContent = profile.role;

    // Navigate to default view for role
    navigateToPage(profile.defaultPage);
    addLogLine('system', `Switched view profile to: ${profile.name} (${profile.role})`);
  });

  // -------------------------------------------------------------
  // Live Telemetry / Data Simulation
  // -------------------------------------------------------------
  setInterval(() => {
    // Fluctuating capacity
    const capacityJitter = Math.floor(Math.random() * 20) - 10;
    state.metrics.capacity = Math.min(82500, Math.max(70000, state.metrics.capacity + capacityJitter));
    
    // Emissions offset accumulation
    state.metrics.emissionsOffset = parseFloat((state.metrics.emissionsOffset + 0.05).toFixed(1));
    
    // Gate flow jitter
    const flowJitter = Math.floor(Math.random() * 10) - 5;
    state.metrics.gateCFlow = Math.max(80, state.metrics.gateCFlow + flowJitter);

    // Update UI components if visible
    const capacityEl = document.getElementById('land-capacity');
    if (capacityEl) {
      capacityEl.textContent = `${state.metrics.capacity.toLocaleString()} / 82,500`;
    }

    const ecoEl = document.getElementById('land-eco');
    if (ecoEl) {
      // Simulate index changes slightly
      ecoEl.textContent = `${(94.5 + (Math.random() * 0.6)).toFixed(1)}%`;
    }

    // Add randomized logs sometimes
    if (Math.random() > 0.7) {
      const logs = [
        "Crowd Agent: Sector A escalators reporting normal transit load.",
        "Transport Agent: NJ Transit departure corridor clearing rapidly.",
        "Sustainability Agent: Renewable grid supplying 64% of lighting demands.",
        "Operations Agent: Trash bin load sensors reporting emptying actions complete."
      ];
      const randomLog = logs[Math.floor(Math.random() * logs.length)];
      addLogLine('system', `[Telemetry Update] ${randomLog}`);
    }
  }, 4000);

  // Helper: Append line to logs panel
  function addLogLine(type, text) {
    const logBox = document.getElementById('ops-incident-log');
    if (logBox) {
      const line = document.createElement('div');
      line.className = `agent-log-line ${type === 'system' ? 'system' : `agent-${type}`}`;
      const timeStr = new Date().toLocaleTimeString();
      line.textContent = `[${timeStr}] ${text}`;
      logBox.appendChild(line);
      logBox.scrollTop = logBox.scrollHeight;
    }
  }

  // -------------------------------------------------------------
  // RAG Platform & AI Chat Engine
  // -------------------------------------------------------------
  const chatInput = document.getElementById('chat-text-input');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const chatHistoryBox = document.getElementById('chat-history-box');
  const docItems = document.querySelectorAll('.doc-list .doc-item');

  // Change active loaded doc
  docItems.forEach(item => {
    item.addEventListener('click', () => {
      docItems.forEach(d => d.classList.remove('active'));
      item.classList.add('active');
      state.activeDoc = item.getAttribute('data-doc');
      
      const docName = item.textContent.trim();
      addLogLine('ops', `Loaded context database: ${docName}`);
      appendSystemMessage(`Knowledge base reference focus swapped to: ${docName}`);
    });
  });

  function appendSystemMessage(text) {
    const msg = document.createElement('div');
    msg.className = 'chat-msg msg-assistant';
    msg.innerHTML = `
      <div class="chat-msg-bubble" style="border-color: rgba(255,255,255,0.05); background: rgba(255,255,255,0.02); font-style: italic;">
        ${text}
      </div>
    `;
    chatHistoryBox.appendChild(msg);
    chatHistoryBox.scrollTop = chatHistoryBox.scrollHeight;
  }

  function handleChatSubmit() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Append User Message
    appendMessage('user', 'You', text);
    chatInput.value = '';

    // Trigger AI thoughts + RAG lookup simulator
    simulateAgentWorkflow(text);
  }

  chatSendBtn.addEventListener('click', handleChatSubmit);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleChatSubmit();
  });

  function appendMessage(role, sender, text, agentSteps = []) {
    const msg = document.createElement('div');
    msg.className = `chat-msg ${role === 'user' ? 'msg-user' : 'msg-assistant'}`;
    
    let stepsHtml = '';
    if (agentSteps.length > 0) {
      stepsHtml = `
        <div class="chat-agent-thinking">
          <strong><i data-lucide="bot" style="width:12px; height:12px; display:inline; vertical-align:middle;"></i> Multi-Agent Orchestration Log:</strong>
          ${agentSteps.map(step => `<div>${step}</div>`).join('')}
        </div>
      `;
    }

    msg.innerHTML = `
      <div class="chat-msg-bubble">
        <div class="chat-msg-sender">${sender}</div>
        <div>${text}</div>
        ${stepsHtml}
      </div>
    `;
    chatHistoryBox.appendChild(msg);
    chatHistoryBox.scrollTop = chatHistoryBox.scrollHeight;
    lucide.createIcons();

    // Trigger TTS if screenreader toggle is enabled
    if (role === 'assistant' && state.accessibility.screenReader) {
      speakText(text);
    }
  }

  // Simulator RAG + Multi Agent planning pipeline
  function simulateAgentWorkflow(query) {
    const lowerQuery = query.toLowerCase();
    let reply = "";
    let matchedDoc = state.activeDoc;
    let agentLogs = [];

    // Step 1: Detect intent and choose focus doc if not manually selected
    if (lowerQuery.includes('bag') || lowerQuery.includes('prohibited') || lowerQuery.includes('rules')) {
      matchedDoc = 'rules';
    } else if (lowerQuery.includes('evacuate') || lowerQuery.includes('emergency') || lowerQuery.includes('medical') || lowerQuery.includes('exit')) {
      matchedDoc = 'evac';
    } else if (lowerQuery.includes('ticket') || lowerQuery.includes('mobile')) {
      matchedDoc = 'tickets';
    } else if (lowerQuery.includes('train') || lowerQuery.includes('bus') || lowerQuery.includes('rideshare') || lowerQuery.includes('transport')) {
      matchedDoc = 'transit';
    }

    // Step 2: Assemble Multi-Agent orchestrator simulated logic logs
    agentLogs.push(`[1] Planner Agent: Classifying intent. Found focus topic context: "${matchedDoc}"`);
    
    // RAG Search simulation
    const docTextList = knowledgeBase[matchedDoc];
    let retrievedChunks = [];
    docTextList.forEach(chunk => {
      // Simple keyword matching for demo
      retrievedChunks.push(chunk.text);
    });

    agentLogs.push(`[2] Retrieval Agent (RAG): Found ${retrievedChunks.length} documents matching tags.`);
    agentLogs.push(`[3] Evaluation Agent: Selecting highest score chunk: "${retrievedChunks[0].substring(0, 40)}..."`);
    
    // Step 3: Formulate answer based on matching documents
    if (matchedDoc === 'rules') {
      reply = "According to the stadium rules, clear bags must be smaller than 12x6x12 inches. Professional cameras with lenses longer than 6 inches, weapons, glass bottles, and banners larger than 3x5 feet are strictly prohibited.";
      agentLogs.push(`[4] Answer Generator: Assembling rules guidelines output.`);
    } else if (matchedDoc === 'evac') {
      reply = "If there is an evacuation, please walk to the nearest exit stairs. East gates (Gate C & D) connect to the primary parking lot assembly areas. First Aid stations are fully staffed and located near Section 109, 143, 216, and 302.";
      agentLogs.push(`[5] Answer Generator: Rendering emergency route map vectors.`);
    } else if (matchedDoc === 'tickets') {
      reply = "FIFA World Cup 2026 operates on a 100% mobile-only ticket policy via the official app. screenshots and paper tickets will not scan. Ticket help points are located outside Gates A and C.";
      agentLogs.push(`[6] Answer Generator: Validating ticketing scanner schemas.`);
    } else if (matchedDoc === 'transit') {
      reply = "NJ Transit trains run every 8-12 minutes direct to NYC Penn Station. Shuttle buses operate to the parking lots every 5 minutes. Rideshare pick-up is at Lot G (15 min walk from Gate D).";
      agentLogs.push(`[7] Answer Generator: Querying live transit arrival timers.`);
    } else {
      reply = "I understand you are asking about: '" + query + "'. I can help you with stadium navigation, ticketing policies, sustainable concession recommendations, and transit departures. Could you clarify your question?";
      agentLogs.push(`[8] General Agent fallback: Prompting for refinement.`);
    }

    // Delay response slightly to simulate thinking time
    setTimeout(() => {
      appendMessage('assistant', 'AI Stadium Assistant', reply, agentLogs);
      
      // Update global dashboard incident log as well
      addLogLine('ops', `AI Agent processed query: "${query}" -> Response generated.`);
    }, 1200);
  }

  // -------------------------------------------------------------
  // Web Speech API: Voice Assistant UI
  // -------------------------------------------------------------
  const voiceMicBtn = document.getElementById('voice-assistant-mic');
  const voiceStatus = document.getElementById('voice-assistant-status');
  const voiceTranscript = document.getElementById('voice-assistant-transcript');
  
  const chatVoiceBtn = document.getElementById('chat-voice-btn');

  // Check speech recognition availability
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
      state.isRecordingVoice = true;
      voiceStatus.textContent = "Listening closely... Speak now.";
      voiceMicBtn.classList.add('recording');
      chatVoiceBtn.classList.add('recording');
    };

    recognition.onerror = (e) => {
      console.error(e);
      voiceStatus.textContent = "Error capturing speech. Click to try again.";
      stopVoiceRecording();
    };

    recognition.onend = () => {
      stopVoiceRecording();
    };

    recognition.onresult = (event) => {
      const transcriptText = event.results[0][0].transcript;
      voiceTranscript.textContent = `"${transcriptText}"`;
      
      // If we are in the Fan Dashboard, automatically run the simulation
      if (state.activePage === 'page-fan') {
        setTimeout(() => {
          navigateToPage('page-chat');
          chatInput.value = transcriptText;
          handleChatSubmit();
        }, 1000);
      } else if (state.activePage === 'page-chat') {
        chatInput.value = transcriptText;
        handleChatSubmit();
      }
    };
  }

  function stopVoiceRecording() {
    state.isRecordingVoice = false;
    voiceMicBtn.classList.remove('recording');
    chatVoiceBtn.classList.remove('recording');
    if (recognition) recognition.stop();
  }

  function toggleVoice() {
    if (!recognition) {
      alert("Speech recognition is not supported in this browser. Please type your query in the chat console.");
      return;
    }

    if (state.isRecordingVoice) {
      stopVoiceRecording();
    } else {
      voiceStatus.textContent = "Requesting microphone permission...";
      recognition.start();
    }
  }

  if (voiceMicBtn) voiceMicBtn.addEventListener('click', toggleVoice);
  if (chatVoiceBtn) chatVoiceBtn.addEventListener('click', toggleVoice);

  // Text-To-Speech function
  function speakText(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // Cancel active speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  }

  // -------------------------------------------------------------
  // Emergency Evacuation simulation
  // -------------------------------------------------------------
  const simEgressBtn = document.getElementById('trigger-emergency-simulation');
  const alertBanner = document.getElementById('alert-banner-status');
  const executeEvacBtn = document.getElementById('ops-execute-evac-ai');
  const triggerAlarmBtn = document.getElementById('trigger-alarm-btn');

  function triggerEmergencySystem() {
    state.emergencyActive = !state.emergencyActive;

    if (state.emergencyActive) {
      // Activate emergency state
      alertBanner.className = "status-pill danger";
      alertBanner.innerHTML = `<span class="pulse-dot" style="width:8px; height:8px; background:var(--accent-red); border-radius:50%; display:inline-block; animation: pulseRecording 0.8s infinite;"></span><span>🚨 CRITICAL: EVACUATION ORDER</span>`;
      
      // Flash SVG paths
      const fanPath = document.getElementById('fan-path-line');
      if (fanPath) {
        fanPath.style.stroke = "var(--accent-red)";
      }

      // Add Incident Logs
      addLogLine('emg', "Emergency Agent: SENSOR TRIGGERED smoke detection concourse B.");
      addLogLine('emg', "Emergency Agent Action: Initiating full digital evacuation route directives.");
      addLogLine('ops', "Operations Agent: Sounding alarms. Public Transit notification broadcast sent.");

      // Swap to emergency page to show results
      navigateToPage('page-emergency');

      speakText("Attention! An emergency condition has been detected. Please evacuate the stadium immediately using the green lit escape paths.");
    } else {
      // Revert to normal
      alertBanner.className = "status-pill success";
      alertBanner.innerHTML = `<span class="pulse-dot" style="width:8px; height:8px; background:var(--accent-green); border-radius:50%; display:inline-block; animation: pulseRecording 1.5s infinite;"></span><span>All sectors clear</span>`;
      
      const fanPath = document.getElementById('fan-path-line');
      if (fanPath) {
        fanPath.style.stroke = "var(--accent-cyan)";
      }
      
      addLogLine('system', "Emergency clear code entered. System returning to standby.");
    }
  }

  if (simEgressBtn) simEgressBtn.addEventListener('click', triggerEmergencySystem);
  if (executeEvacBtn) executeEvacBtn.addEventListener('click', triggerEmergencySystem);
  if (triggerAlarmBtn) triggerAlarmBtn.addEventListener('click', triggerEmergencySystem);

  // -------------------------------------------------------------
  // Accessibility Control System
  // -------------------------------------------------------------
  const themeToggle = document.getElementById('theme-toggle');
  const filterNone = document.getElementById('filter-none');
  const filterProtanopia = document.getElementById('filter-protanopia');
  const filterDeuteranopia = document.getElementById('filter-deuteranopia');
  const filterTritanopia = document.getElementById('filter-tritanopia');
  const filterContrast = document.getElementById('filter-contrast');

  const toggleDyslexic = document.getElementById('toggle-dyslexic');
  const toggleZoom = document.getElementById('toggle-zoom');
  const toggleScreenReader = document.getElementById('toggle-screenreader');

  // Theme switch
  themeToggle.addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.body.classList.toggle('light-mode');
    
    // Update theme toggle icon
    const icon = themeToggle.querySelector('i');
    if (state.theme === 'light') {
      icon.setAttribute('data-lucide', 'moon');
    } else {
      icon.setAttribute('data-lucide', 'sun');
    }
    lucide.createIcons();
    addLogLine('system', `Theme toggled to: ${state.theme}`);
  });

  // Color Filter toggles
  function applyColorFilter(filterName) {
    document.body.classList.remove('protanopia', 'deuteranopia', 'tritanopia', 'high-contrast');
    
    const allFilters = [filterNone, filterProtanopia, filterDeuteranopia, filterTritanopia, filterContrast];
    allFilters.forEach(f => { if (f) f.classList.remove('active'); });

    state.accessibility.colorFilter = filterName;
    if (filterName !== 'none') {
      document.body.classList.add(filterName);
      const activeBtn = document.getElementById(`filter-${filterName}`);
      if (activeBtn) activeBtn.classList.add('active');
    } else {
      if (filterNone) filterNone.classList.add('active');
    }
    addLogLine('system', `Applied vision contrast filter: ${filterName}`);
  }

  if (filterNone) filterNone.addEventListener('click', () => applyColorFilter('none'));
  if (filterProtanopia) filterProtanopia.addEventListener('click', () => applyColorFilter('protanopia'));
  if (filterDeuteranopia) filterDeuteranopia.addEventListener('click', () => applyColorFilter('deuteranopia'));
  if (filterTritanopia) filterTritanopia.addEventListener('click', () => applyColorFilter('tritanopia'));
  if (filterContrast) filterContrast.addEventListener('click', () => applyColorFilter('contrast'));

  // Text Adjustments
  if (toggleDyslexic) {
    toggleDyslexic.addEventListener('click', () => {
      state.accessibility.dyslexicFriendly = !state.accessibility.dyslexicFriendly;
      document.body.classList.toggle('easy-reading');
      toggleDyslexic.classList.toggle('active');
    });
  }

  if (toggleZoom) {
    toggleZoom.addEventListener('click', () => {
      state.accessibility.textZoom = !state.accessibility.textZoom;
      if (state.accessibility.textZoom) {
        document.documentElement.style.fontSize = '18px';
        toggleZoom.classList.add('active');
      } else {
        document.documentElement.style.fontSize = '16px';
        toggleZoom.classList.remove('active');
      }
    });
  }

  if (toggleScreenReader) {
    toggleScreenReader.addEventListener('click', () => {
      state.accessibility.screenReader = !state.accessibility.screenReader;
      toggleScreenReader.classList.toggle('active');
      if (state.accessibility.screenReader) {
        speakText("Screen reader announcements enabled.");
      }
    });
  }

  // -------------------------------------------------------------
  // Report Generator
  // -------------------------------------------------------------
  const generateReportBtn = document.getElementById('generate-report-btn');
  const reportTypeSelect = document.getElementById('report-type');
  const reportOutputBox = document.getElementById('report-output-box');

  const mockReports = {
    exec: `### FIFA World Cup 2026 Operations Summary - MetLife Stadium

**Reporting Period:** Today 18:00 - 22:00 EST  
**Match Context:** USA vs England (Group B)  
**Total Attendance:** 78,540 / 82,500 (95.2% capacity)  

---

#### 📈 Key Operations Data
- **Average Entry Delay:** 4.2 minutes (Gate C Scanner anomaly resolved)
- **Sustainability Savings:** 12.4 Tons CO₂ equivalent offset
- **Active Incidents:** 3 minor incidents reported (2 medical first-aid, 1 lost items)
- **Response Team ETA:** 3.8 minutes average dispatcher transit time

---

#### 🤖 AI Recommendations Applied
1. **Shuttle Transit:** Staggered lot release intervals by 8 minutes, avoiding traffic lock on Route 120.
2. **Concourse Staging:** Dispatched 4 additional volunteers to Gate B scanners, lowering backup queues.
3. **Smart Power Grid:** Adjusted HVAC targets in non-crowded corridors, saving 18 kW power load.`,

    sustain: `### FIFA ESG Sustainability compliance Report

**Reporting Location:** MetLife Stadium (Digital Twin Telemetry)  
**Match Context:** USA vs England (Group B)  
**Date:** July 16, 2026  

---

#### 🌿 Environmental Impact metrics
- **Renewable Energy Share:** 64% (Solar + local micro-grid offsets)
- **Water Consumption:** 18,450 gallons (92% recycled greywater usage)
- **Total Energy Saved:** 420 kWh (LED micro-zoning active)
- **Recycling Diversion Rate:** 82% (Optimized bin placements)

---

#### 💡 Sustainability AI Actions Taken
- Sensor arrays detected 15% lower attendee load in Upper Deck (Sectors 301-308). Localized HVAC cooling output was lowered by 2°C, saving 32 kW/h power draw.
- Smart sensors routed bin replacement teams to Concourse C before capacity overflows.`,

    incidents: `### FIFA Incident Management and Security Dispatch log

**Reporting Period:** Today 18:00 - 20:30 EST  
**Filter:** All incidents (Closed, Pending, Active)  

---

#### 📋 Incident Registry
1. **ID #1024 - Medical Assistance (Sector 109)**  
   - *Status:* [CLOSED]  
   - *Type:* Severe dehydration / heat distress  
   - *Response:* Dispatch medical squad 1. Administered cooling packs. Patient stabilized and returned to seat.  
   - *AI Support:* Pre-authorized fastest walking route bypassing crowded hallways.

2. **ID #1025 - Scanner Queue Congestion (Gate B Entrance)**  
   - *Status:* [RESOLVED]  
   - *Type:* Ticket reader hardware glitch  
   - *Response:* Dispatched Volunteer squad 4 to run mobile ticket readers.  

3. **ID #1026 - Lost & Found (Sector 212 Concourse)**  
   - *Status:* [ACTIVE]  
   - *Type:* Wallet lost  
   - *Response:* Inquiry registered in vector database search index.`
  };

  if (generateReportBtn) {
    generateReportBtn.addEventListener('click', () => {
      reportOutputBox.style.display = 'block';
      reportOutputBox.innerHTML = `
        <div style="display:flex; align-items:center; gap:12px; color:var(--accent-cyan); font-family:var(--font-sans); font-size:12px; margin-bottom:12px;">
          <span style="display:inline-block; width:12px; height:12px; border:2px solid var(--accent-cyan); border-top-color:transparent; border-radius:50%; animation:dash 1s linear infinite;"></span>
          Agentic Ops system generating executive summaries... Planning, Retrieving telemetry DB, Rendering Markdown...
        </div>
      `;

      setTimeout(() => {
        const reportType = reportTypeSelect.value;
        const reportMd = mockReports[reportType];
        
        // Convert mock markdown headings and bullets to basic HTML for preview
        let formattedHtml = reportMd
          .replace(/### (.*)/g, '<h3 style="color:var(--accent-cyan); font-family:var(--font-display); font-size:16px; margin: 12px 0 6px 0;">$1</h3>')
          .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
          .replace(/#### (.*)/g, '<h4 style="font-size:12px; font-weight:700; margin:10px 0 4px 0; color:var(--text-primary);">$1</h4>')
          .replace(/- \*\*(.*)\*\*/g, '<li><strong>$1</strong>')
          .replace(/- (.*)/g, '<li>$1')
          .replace(/\n\n/g, '<br>')
          .replace(/---/g, '<hr style="border:0; border-top:1px solid var(--border-light); margin:12px 0;">');

        reportOutputBox.innerHTML = formattedHtml;
        addLogLine('ops', `Executive report generated successfully: [Type: ${reportType}]`);
      }, 1500);
    });
  }

  // Interactive buttons in volunteer page
  window.completeVolunteerTask = function(button) {
    const card = button.parentElement.parentElement;
    card.style.opacity = '0.5';
    card.style.pointerEvents = 'none';
    button.textContent = "Completed";
    button.style.background = "#4b5563";
    const title = card.querySelector('h4').textContent;
    addLogLine('volunteer', `Volunteer Task Complete: "${title}"`);
  };

  // Translation triggers
  const translateAnnouncementBtn = document.getElementById('translate-announcement-btn');
  const translationOutput = document.getElementById('translation-output');

  if (translateAnnouncementBtn) {
    translateAnnouncementBtn.addEventListener('click', () => {
      translationOutput.textContent = "AI Translation Engine Processing...";
      setTimeout(() => {
        translationOutput.textContent = `"Please proceed to Gate C if your seat is in sectors 110 to 115 to avoid overcrowding."`;
        addLogLine('volunteer', "Intercom announcement Spanish translation verified.");
      }, 800);
    });
  }
});
