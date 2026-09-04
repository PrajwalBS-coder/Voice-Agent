<script>
  export let status;
</script>

<section class="status-card">
  <p class="eyebrow">AGENT STATUS</p>
  <h2>{status.state.charAt(0).toUpperCase() + status.state.slice(1)}</h2>
  <p class="muted">{status.running ? 'Jarvis is ready for your voice.' : 'Start the agent when you are ready.'}</p>
</section>
