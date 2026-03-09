<script lang="ts">
  import './layout.css';
  import favicon from '$lib/assets/favicon.svg';
  import { onMount, onDestroy } from 'svelte';
  import { alertStore } from '$lib/stores/alert-store.svelte';
  import { ModeWatcher } from 'mode-watcher';
  import EmergencyAlert from '$lib/components/EmergencyAlert.svelte';

  let { children } = $props();

  onMount(() => {
    alertStore.init();
  });

  onDestroy(() => {
    alertStore.destroy();
  });
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<EmergencyAlert />
<ModeWatcher />

{@render children()}
