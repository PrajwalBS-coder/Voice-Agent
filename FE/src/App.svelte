<script>
  import { onMount } from 'svelte';
  import { getStatus, startAgent, stopAgent } from './services/api.js';

  let status = { running: false, state: 'stopped', pid: null, logs: [] };
  let duration = 15;
  let notice = '';
  let loading = false;
  let polling = true;
  let graphCanvas;
  let networkNodes = [];
  let selectedModule = 'router';
  let selectedNodeKey = 'router-hub';
  let selectedGraphNode = null;
  let hoveredNode = null;
  let focusSelected = false;
  let graphView = { zoom: 1, panX: 0, panY: 0 };

  const POLL_INTERVAL_MS = 3000;
  const modules = [
    { id: 'router', name: 'Command router', group: 'CORE', color: '#8c79f6', description: 'Understands a request and routes it to the right Jarvis skill.' },
    { id: 'voice', name: 'Voice interface', group: 'AUDIO', color: '#39d6ca', description: 'Listens with Whisper and speaks replies with Gemini TTS or the local voice.' },
    { id: 'gemini', name: 'Gemini intelligence', group: 'AI', color: '#328bd5', description: 'Uses Gemini for contextual command routing and grounded answers.' },
    { id: 'memory', name: 'Conversation memory', group: 'MEMORY', color: '#bb75ec', description: 'Keeps recent turns locally so Jarvis can follow the conversation.' },
    { id: 'tools', name: 'Local skills', group: 'TOOLS', color: '#ed9a39', description: 'Runs configured app, document, camera, music, and utility actions.' },
    { id: 'vision', name: 'Camera & screen', group: 'VISION', color: '#45b771', description: 'Captures a webcam photo or a screenshot when you ask.' },
  ];
  $: activeModule = modules.find((item) => item.id === selectedModule) || modules[0];
  $: selectedGraphNode = networkNodes.find((node) => node.key === selectedNodeKey) || null;
  $: selectedNodeLabel = selectedGraphNode?.name || activeModule.name;
  $: stateLabel = status.state.charAt(0).toUpperCase() + status.state.slice(1);
  $: recentLogs = (status.logs || []).slice(-10).reverse();

  async function refreshStatus() {
    try {
      status = await getStatus();
    } catch (error) {
      notice = 'Start the backend API to connect Jarvis.';
    }
  }

  async function control(action) {
    loading = true;
    notice = '';
    try {
      const data = action === 'start' ? await startAgent(duration) : await stopAgent();
      notice = data.message;
      await refreshStatus();
    } catch (error) {
      notice = 'Could not reach the backend API.';
    } finally {
      loading = false;
    }
  }

  function buildNetwork() {
    const clusters = [
      { id: 'router', x: 0.38, y: 0.48, count: 32 },
      { id: 'voice', x: 0.69, y: 0.42, count: 24 },
      { id: 'memory', x: 0.51, y: 0.2, count: 15 },
      { id: 'tools', x: 0.55, y: 0.75, count: 24 },
      { id: 'vision', x: 0.22, y: 0.72, count: 14 },
      { id: 'gemini', x: 0.82, y: 0.73, count: 20 },
    ];
    const result = [];
    let seed = 32647;
    const random = () => {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    };

    for (const cluster of clusters) {
      const module = modules.find((item) => item.id === cluster.id);
      result.push({
        key: `${cluster.id}-hub`, id: cluster.id, name: module.name,
        moduleId: cluster.id, hub: true, x: cluster.x, y: cluster.y,
        radius: 4.8 + random() * 1.5, phase: random() * Math.PI * 2,
      });
      for (let index = 0; index < cluster.count; index += 1) {
        const angle = random() * Math.PI * 2;
        const spread = 0.035 + random() * 0.14;
        result.push({
          key: `${cluster.id}-${index}`, moduleId: cluster.id,
          name: `${module.name} node ${String(index + 1).padStart(2, '0')}`,
          x: cluster.x + Math.cos(angle) * spread,
          y: cluster.y + Math.sin(angle) * spread * 0.62,
          radius: 1.5 + random() * 2.1, phase: random() * Math.PI * 2,
        });
      }
    }
    return result;
  }

  function graphPoint(node, width, height) {
    const centerX = width / 2;
    const centerY = height / 2;
    return {
      x: centerX + (node.x * width - centerX) * graphView.zoom + graphView.panX,
      y: centerY + (node.y * height - centerY) * graphView.zoom + graphView.panY,
    };
  }

  function canvasPosition(event) {
    const bounds = graphCanvas.getBoundingClientRect();
    return { x: event.clientX - bounds.left, y: event.clientY - bounds.top, width: bounds.width, height: bounds.height };
  }

  function graphPosition(screen) {
    const centerX = screen.width / 2;
    const centerY = screen.height / 2;
    return {
      x: (centerX + (screen.x - centerX - graphView.panX) / graphView.zoom) / screen.width,
      y: (centerY + (screen.y - centerY - graphView.panY) / graphView.zoom) / screen.height,
    };
  }

  function findNodeAt(position) {
    let nearest = null;
    let nearestDistance = Infinity;
    for (const node of networkNodes) {
      if (focusSelected && node.moduleId !== selectedModule) continue;
      const point = graphPoint(node, position.width, position.height);
      const distance = Math.hypot(point.x - position.x, point.y - position.y);
      const hitRadius = Math.max(8, node.radius + 5);
      if (distance <= hitRadius && distance < nearestDistance) {
        nearest = node;
        nearestDistance = distance;
      }
    }
    return nearest;
  }

  function selectNode(node) {
    if (!node) return;
    selectedNodeKey = node.key;
    selectedModule = node.moduleId;
  }

  function selectModule(moduleId) {
    selectNode(networkNodes.find((node) => node.key === `${moduleId}-hub`));
  }

  function handlePointerDown(event) {
    if (event.button !== 0) return;
    const position = canvasPosition(event);
    const node = findNodeAt(position);
    if (node) {
      selectNode(node);
      const members = node.hub ? networkNodes.filter((item) => item.moduleId === node.moduleId) : [node];
      graphInteraction = {
        type: 'node', node, start: graphPosition(position),
        originals: members.map((item) => ({ node: item, x: item.x, y: item.y })),
      };
      graphCanvas.style.cursor = 'grabbing';
    } else {
      graphInteraction = { type: 'pan', x: position.x, y: position.y, panX: graphView.panX, panY: graphView.panY };
      graphCanvas.style.cursor = 'grabbing';
    }
    graphCanvas.setPointerCapture(event.pointerId);
  }

  function handlePointerMove(event) {
    const position = canvasPosition(event);
    if (graphInteraction?.type === 'node') {
      const world = graphPosition(position);
      const deltaX = world.x - graphInteraction.start.x;
      const deltaY = world.y - graphInteraction.start.y;
      graphInteraction.originals.forEach(({ node, x, y }) => {
        node.x = Math.max(-0.1, Math.min(1.1, x + deltaX));
        node.y = Math.max(-0.1, Math.min(1.1, y + deltaY));
      });
      return;
    }
    if (graphInteraction?.type === 'pan') {
      graphView.panX = graphInteraction.panX + position.x - graphInteraction.x;
      graphView.panY = graphInteraction.panY + position.y - graphInteraction.y;
      return;
    }
    hoveredNode = findNodeAt(position);
    graphCanvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
  }

  function handlePointerUp(event) {
    if (graphCanvas?.hasPointerCapture(event.pointerId)) graphCanvas.releasePointerCapture(event.pointerId);
    graphInteraction = null;
    graphCanvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
  }

  function handlePointerLeave() {
    if (!graphInteraction) {
      hoveredNode = null;
    }
  }

  function handleWheel(event) {
    event.preventDefault();
    const position = canvasPosition(event);
    const world = graphPosition(position);
    const zoom = Math.max(0.55, Math.min(2.8, graphView.zoom * Math.exp(-event.deltaY * 0.001)));
    graphView.zoom = zoom;
    graphView.panX = position.x - position.width / 2 - (world.x * position.width - position.width / 2) * zoom;
    graphView.panY = position.y - position.height / 2 - (world.y * position.height - position.height / 2) * zoom;
  }

  function resetGraph() {
    graphView = { zoom: 1, panX: 0, panY: 0 };
    focusSelected = false;
    selectNode(networkNodes.find((node) => node.key === 'router-hub'));
  }

  let graphInteraction = null;

  function drawNetwork() {
    const canvas = graphCanvas;
    if (!canvas) return () => {};
    const context = canvas.getContext('2d');
    const moduleColors = Object.fromEntries(modules.map((item) => [item.id, item.color]));
    const hubs = Object.fromEntries(networkNodes.filter((node) => node.hub).map((node) => [node.id, node]));
    const paths = [
      ['router', 'memory'], ['router', 'voice'], ['router', 'tools'],
      ['router', 'vision'], ['voice', 'gemini'], ['tools', 'gemini'],
      ['memory', 'voice'], ['vision', 'tools'],
    ].map(([from, to]) => [hubs[from], hubs[to]]);
    let animationFrame = 0;
    let tick = 0;
    let width = 0;
    let height = 0;
    let pixelRatio = 1;

    const render = () => {
      const bounds = canvas.getBoundingClientRect();
      if (!bounds.width || !bounds.height) {
        animationFrame = requestAnimationFrame(render);
        return;
      }
      const nextRatio = Math.min(window.devicePixelRatio || 1, 2);
      if (width !== bounds.width || height !== bounds.height || pixelRatio !== nextRatio) {
        width = bounds.width;
        height = bounds.height;
        pixelRatio = nextRatio;
        canvas.width = Math.round(width * pixelRatio);
        canvas.height = Math.round(height * pixelRatio);
      }
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      context.clearRect(0, 0, width, height);
      const point = (node) => graphPoint(node, width, height);

      context.save();
      context.strokeStyle = 'rgba(94, 132, 177, 0.055)';
      context.lineWidth = 1;
      for (let x = 0; x < width; x += 42) {
        context.beginPath(); context.moveTo(x, 0); context.lineTo(x, height); context.stroke();
      }
      for (let y = 0; y < height; y += 42) {
        context.beginPath(); context.moveTo(0, y); context.lineTo(width, y); context.stroke();
      }
      context.restore();

      for (const node of networkNodes) {
        if (node.hub || (focusSelected && node.moduleId !== selectedModule)) continue;
        const origin = point(node); const target = point(hubs[node.moduleId]);
        context.beginPath(); context.moveTo(origin.x, origin.y); context.lineTo(target.x, target.y);
        context.strokeStyle = `${moduleColors[node.moduleId]}25`; context.lineWidth = 0.8; context.stroke();
      }

      for (let index = 0; index < networkNodes.length; index += 1) {
        const node = networkNodes[index];
        if (node.hub || (focusSelected && node.moduleId !== selectedModule)) continue;
        const a = point(node);
        for (let next = index + 1; next < networkNodes.length; next += 1) {
          const other = networkNodes[next];
          if (other.hub || other.moduleId === node.moduleId || (focusSelected && other.moduleId !== selectedModule)) continue;
          const b = point(other); const distance = Math.hypot(a.x - b.x, a.y - b.y);
          if (distance < 38) {
            context.beginPath(); context.moveTo(a.x, a.y); context.lineTo(b.x, b.y);
            context.strokeStyle = `rgba(80, 112, 154, ${0.12 * (1 - distance / 38)})`; context.lineWidth = 0.7; context.stroke();
          }
        }
      }

      paths.forEach(([from, to], index) => {
        if (focusSelected) return;
        const a = point(from); const b = point(to);
        context.beginPath(); context.moveTo(a.x, a.y); context.lineTo(b.x, b.y);
        context.strokeStyle = 'rgba(111, 151, 193, 0.24)'; context.lineWidth = 1.1; context.stroke();
        const progress = ((tick * 0.002 + index * 0.16) % 1);
        context.beginPath(); context.arc(a.x + (b.x - a.x) * progress, a.y + (b.y - a.y) * progress, 1.8, 0, Math.PI * 2);
        context.fillStyle = '#9fd9f4'; context.shadowColor = '#72caff'; context.shadowBlur = 9; context.fill(); context.shadowBlur = 0;
      });

      networkNodes.forEach((node) => {
        if (focusSelected && node.moduleId !== selectedModule) return;
        const { x, y } = point(node);
        const picked = node.key === selectedNodeKey;
        const hovered = node.key === hoveredNode?.key;
        const color = moduleColors[node.moduleId];
        if (picked || hovered) {
          context.beginPath(); context.arc(x, y, (node.hub ? 16 : 8) + Math.sin(tick * 0.04 + node.phase) * 1.2, 0, Math.PI * 2);
          context.strokeStyle = `${color}88`; context.lineWidth = 1; context.stroke();
        } else if (node.hub) {
          context.beginPath(); context.arc(x, y, 13 + Math.sin(tick * 0.035 + node.phase) * 1.8, 0, Math.PI * 2);
          context.strokeStyle = `${color}55`; context.lineWidth = 1; context.stroke();
        }
        context.beginPath(); context.arc(x, y, node.radius + (picked || hovered ? 0.8 : 0), 0, Math.PI * 2);
        context.fillStyle = color; context.globalAlpha = node.hub || picked || hovered ? 0.98 : 0.72;
        context.shadowColor = color; context.shadowBlur = node.hub || picked || hovered ? 13 : 3;
        context.fill(); context.globalAlpha = 1; context.shadowBlur = 0;
      });

      const labelNode = hoveredNode || selectedGraphNode;
      if (labelNode && (!focusSelected || labelNode.moduleId === selectedModule)) {
        const { x, y } = point(labelNode);
        const label = labelNode.name;
        context.font = '10px "DM Mono", monospace';
        const labelWidth = context.measureText(label).width + 18;
        const labelX = Math.max(8, Math.min(width - labelWidth - 8, x + 15));
        const labelY = Math.max(20, Math.min(height - 12, y - 13));
        context.fillStyle = 'rgba(10, 15, 22, 0.94)';
        context.strokeStyle = `${moduleColors[labelNode.moduleId]}77`; context.lineWidth = 1;
        context.beginPath(); context.roundRect(labelX, labelY - 12, labelWidth, 23, 4); context.fill(); context.stroke();
        context.fillStyle = '#dce7f1'; context.fillText(label, labelX + 9, labelY + 3);
      }

      tick += 1;
      animationFrame = requestAnimationFrame(render);
    };
    animationFrame = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animationFrame);
  }

  onMount(() => {
    networkNodes = buildNetwork();
    const stopDrawing = drawNetwork();
    async function pollStatus() {
      while (polling) {
        await refreshStatus();
        await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
      }
    }
    pollStatus();
    return () => {
      polling = false;
      stopDrawing();
    };
  });
</script>

<svelte:head>
  <title>Jarvis · Workshop OS</title>
  <meta name="theme-color" content="#07090d" />
</svelte:head>

<main class="dashboard">
  <aside class="sidebar">
    <a class="brand" href="#overview" aria-label="Jarvis overview">
      <span class="brand-mark">J</span>
      <span><strong>J.A.R.V.I.S.</strong><small>WORKSHOP OS</small></span>
    </a>

    <div class="system-line"><span class:live={status.running} class="system-dot"></span><span>{status.running ? 'SYSTEM ONLINE' : 'SYSTEM STANDBY'}</span><b>v1.0</b></div>

    <section class="side-section">
      <p class="section-label">COMMAND CENTER</p>
      <button class="nav-item current" type="button" on:click={() => selectModule('router')}><span class="nav-glyph">◈</span>Network overview<span class="nav-arrow">↗</span></button>
      <button class="nav-item" type="button" on:click={() => selectModule('voice')}><span class="nav-glyph">⌁</span>Voice console</button>
      <button class="nav-item" type="button" on:click={() => selectModule('memory')}><span class="nav-glyph">◉</span>Memory core</button>
    </section>

    <section class="side-section systems-section">
      <p class="section-label">SYSTEMS <span>06</span></p>
      {#each modules as item}
        <button class:chosen={selectedModule === item.id} class="system-item" type="button" on:click={() => selectModule(item.id)}>
          <i style={`--module-color:${item.color}`}></i><span>{item.name}</span><small>{item.group}</small>
        </button>
      {/each}
    </section>

    <section class="launch-panel">
      <div class="launch-heading"><span class="mini-wave">⌁</span><span>VOICE AGENT</span></div>
      <p>{status.running ? 'Jarvis is active and listening.' : 'Start Jarvis to begin a voice session.'}</p>
      <label class="duration-label" for="duration">LISTEN WINDOW <b>{duration}s</b></label>
      <input id="duration" class="duration-range" type="range" min="3" max="60" bind:value={duration} />
      <div class="launch-actions">
        <button class="start-button" disabled={status.running || loading} on:click={() => control('start')}><span>▶</span>{loading ? 'Starting' : 'Start Jarvis'}</button>
        <button class="stop-button" aria-label="Stop Jarvis" title="Stop Jarvis" disabled={!status.running || loading} on:click={() => control('stop')}>■</button>
      </div>
    </section>

    <div class="sidebar-footer"><span class="secure-icon">⌑</span><span>LOCAL-FIRST · PRIVATE BY DESIGN</span></div>
  </aside>

  <section class="network-workspace" id="overview">
    <header class="workspace-header">
      <div><p class="breadcrumb">SYSTEMS <span>/</span> NETWORK MAP</p><h1>Knowledge graph</h1></div>
      <div class="map-tools"><span class="live-pill"><i></i>{status.running ? 'LIVE' : 'IDLE'}</span><span class="map-divider"></span><button title="Reset graph view" aria-label="Reset graph view" on:click={resetGraph}>◎</button><button class:tool-active={focusSelected} title="Focus selected system" aria-label="Focus selected system" on:click={() => (focusSelected = !focusSelected)}>☷</button></div>
    </header>

    <div class="graph-frame">
      <canvas
        bind:this={graphCanvas}
        class="network-canvas"
        aria-label="Interactive network map of Jarvis systems"
        role="button"
        tabindex="0"
        on:pointerdown={handlePointerDown}
        on:pointermove={handlePointerMove}
        on:pointerup={handlePointerUp}
        on:pointercancel={handlePointerUp}
        on:pointerleave={handlePointerLeave}
        on:wheel|nonpassive={handleWheel}
        on:keydown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); const next = modules[(modules.findIndex((item) => item.id === selectedModule) + 1) % modules.length]; selectNode(networkNodes.find((node) => node.key === `${next.id}-hub`)); } }}
      ></canvas>
      <div class="map-readout"><span class="readout-dot"></span>{hoveredNode?.name || selectedNodeLabel}</div>
      <div class="map-count"><span>{modules.length}</span> SYSTEMS <i></i><span>{networkNodes.length}</span> NETWORK NODES</div>
      <div class="graph-scale"><span>HIGH ACTIVITY</span><i></i><i></i><i></i><i></i><i></i><span>LOW</span></div>
      <div class="interaction-help">DRAG NODES <b>·</b> DRAG EMPTY SPACE TO PAN <b>·</b> SCROLL TO ZOOM</div>
      {#if notice}<div class="toast"><span>◉</span>{notice}</div>{/if}
    </div>
    <footer class="workspace-footer"><span>JARVIS SYSTEMS MAP <b>·</b> INTERACTIVE</span><span>LOCAL NETWORK <i></i> ENCRYPTED SESSION</span></footer>
  </section>

  <aside class="inspector">
    <div class="inspector-top"><span>AGENT TELEMETRY</span><button aria-label="More telemetry options">···</button></div>
    <div class:active={status.running} class="reactor">
      <div class="reactor-ring ring-one"></div><div class="reactor-ring ring-two"></div><div class="reactor-ring ring-three"></div>
      <div class="reactor-core"><span class="core-star">✳</span><strong>J.A.R.V.I.S.</strong><small>{stateLabel.toUpperCase()}</small></div>
      <span class="reactor-tick tick-a"></span><span class="reactor-tick tick-b"></span><span class="reactor-tick tick-c"></span>
    </div>
    <div class="status-summary"><span class:ready={status.running} class="status-indicator"></span><div><strong>{status.running ? 'System operational' : 'Awaiting startup'}</strong><small>{status.running ? `Process ${status.pid ?? 'starting'} · ${stateLabel}` : 'Start the agent to connect'}</small></div></div>

    <section class="inspect-card selected-card">
      <div class="card-eyebrow"><span style={`--module-color:${activeModule.color}`}></span> SELECTED SYSTEM <small>{activeModule.group}</small></div>
      <h2>{selectedNodeLabel}</h2>
      <p>{activeModule.description}</p>
      <div class="module-status"><span>CONNECTION</span><b><i></i> {status.running ? 'ACTIVE' : 'READY'}</b></div>
    </section>

    <section class="inspect-card activity-card">
      <div class="activity-heading"><span>RECENT ACTIVITY</span><small>LIVE</small></div>
      {#if recentLogs.length}
        <div class="activity-list">
          {#each recentLogs as log, index}
            <div class="activity-entry"><i class:bright={index === 0}></i><p>{log}</p></div>
          {/each}
        </div>
      {:else}
        <p class="empty-activity">No activity yet. Start Jarvis to begin.</p>
      {/if}
    </section>

    <div class="inspector-footer"><span>CPU <b>--</b></span><span>MEMORY <b>LOCAL</b></span><span>API <b>8000</b></span></div>
  </aside>
</main>
