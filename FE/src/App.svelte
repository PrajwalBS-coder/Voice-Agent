<script>
  import { onMount } from 'svelte';
  import StatusCard from './components/StatusCard.svelte';
  import { getStatus, startAgent, stopAgent } from './services/api.js';
  let status = { running: false, state: 'stopped', pid: null, logs: [] };
  let duration = 15;
  let notice = '';
  let loading = false;

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

  onMount(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 1000);
    return () => clearInterval(interval);
  });

  $: stateLabel = status.state.charAt(0).toUpperCase() + status.state.slice(1);
</script>

<svelte:head>
  <title>Jarvis Control</title>
</svelte:head>

<main class="shell">
  <header class="topbar">
    <div>
      <p class="eyebrow">LOCAL VOICE SYSTEM</p>
      <h1>Jarvis Control</h1>
    </div>
    <div class:online={status.running} class="connection">
      <span class="dot"></span>
      {status.running ? 'Online' : 'Offline'}
    </div>
  </header>

  <section class="hero-panel">
    <div class="hero-copy">
      <div class="orb" class:active={status.running}><span></span></div>
      <StatusCard {status} />
    </div>
    <div class="controls">
      <label>
        <span>Max listening time</span>
        <div class="duration-input">
          <input type="number" min="1" max="120" bind:value={duration} />
          <b>sec</b>
        </div>
      </label>
      <div class="button-row">
        <button class="start" disabled={status.running || loading} on:click={() => control('start')}>Start Jarvis</button>
        <button class="stop" disabled={!status.running || loading} on:click={() => control('stop')}>Stop</button>
      </div>
    </div>
  </section>

  {#if notice}
    <p class="notice">{notice}</p>
  {/if}

  <section class="details-grid">
    <article class="panel">
      <div class="panel-heading"><h3>Runtime</h3><span class="badge">LOCAL</span></div>
      <dl>
        <div><dt>State</dt><dd>{stateLabel}</dd></div>
        <div><dt>Process ID</dt><dd>{status.pid ?? '—'}</dd></div>
        <div><dt>API</dt><dd>127.0.0.1:8000</dd></div>
      </dl>
    </article>
    <article class="panel logs-panel">
      <div class="panel-heading"><h3>Activity</h3><span class="badge">LIVE</span></div>
      <div class="logs">
        {#if status.logs.length}
          {#each status.logs.slice(-8) as log}<p>{log}</p>{/each}
        {:else}
          <p class="muted">No activity yet.</p>
        {/if}
      </div>
    </article>
  </section>
</main>
