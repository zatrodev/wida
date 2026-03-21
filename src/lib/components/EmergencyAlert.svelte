<script lang="ts">
  import { alertStore } from '$lib/stores/alert-store.svelte';
  import { Button } from '$lib/components/ui/button';
  import { AlertTriangle, Activity } from 'lucide-svelte';
  import { onDestroy } from 'svelte';

  // We synthesize a beep so no external .mp3 is required.
  let audioCtx: AudioContext | null = null;
  let intervalId: number | null = null;

  function playBeep() {
    if (!audioCtx) audioCtx = new window.AudioContext();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.type = 'square';
    osc.frequency.setValueAtTime(800, audioCtx.currentTime); // 800Hz beep

    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    osc.start();
    gain.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + 0.5);
    osc.stop(audioCtx.currentTime + 0.5);
  }

  $effect(() => {
    if (alertStore.isQuakeActive) {
      if (!intervalId) {
        playBeep();
        intervalId = window.setInterval(playBeep, 2000);
      }
    } else {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
    }
  });

  onDestroy(() => {
    if (intervalId) clearInterval(intervalId);
    if (audioCtx) audioCtx.close();
  });

  const severityLabel: Record<string, string> = {
    minor: 'Minor Earthquake',
    moderate: 'Moderate Earthquake',
    dangerous: 'EARTHQUAKE DETECTED'
  };

  const severityBgColor: Record<string, string> = {
    minor: 'var(--threat-minor)',
    moderate: 'var(--threat-moderate)',
    dangerous: 'var(--threat-dangerous)'
  };

  let overlayBg = $derived(
    severityBgColor[alertStore.currentSeverity] ?? 'var(--threat-dangerous)'
  );
</script>

{#if alertStore.isQuakeActive && alertStore.latestAlert}
  <div
    class="fixed inset-0 z-50 flex animate-[pulse_1.5s_ease-in-out_infinite] items-center justify-center backdrop-blur-md"
    style="background-color: color-mix(in srgb, {overlayBg} 95%, transparent);"
    role="alertdialog"
    aria-modal="true"
  >
    <div
      class="w-full max-w-md scale-100 transform rounded-3xl border border-white/20 bg-black/60 p-8 text-center shadow-2xl backdrop-blur-lg transition-all duration-300"
    >
      <AlertTriangle class="mx-auto mb-6 h-32 w-32 animate-bounce text-white drop-shadow-lg" />
      <h1 class="mb-4 text-5xl font-extrabold tracking-tighter text-white uppercase drop-shadow-md">
        {severityLabel[alertStore.currentSeverity] ?? 'ALERT'}
      </h1>

      <p class="mb-8 text-lg font-medium text-white/90">
        Seek cover immediately! Drop, Cover, and Hold on until shaking stops.
      </p>

      <div class="mb-8 rounded-2xl border border-white/20 bg-white/10 p-4 text-left">
        <div class="mb-2 flex items-center text-white/80">
          <Activity class="mr-2 h-4 w-4" />
          <span class="text-sm font-semibold tracking-wider uppercase">Sensor Feedback</span>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="mb-1 block text-xs text-white/60">Confidence</span>
            <span class="text-xl font-bold text-white drop-shadow-sm"
              >{(alertStore.latestAlert.confidence_score * 100).toFixed(1)}%</span
            >
          </div>
          <div>
            <span class="mb-1 block text-xs text-white/60">Frequency</span>
            <span class="text-xl font-bold text-white drop-shadow-sm"
              >{alertStore.latestAlert.frequency_hz.toFixed(1)} Hz</span
            >
          </div>
        </div>
      </div>

      <Button
        variant="outline"
        class="h-16 w-full rounded-xl border-2 border-white/40 text-lg font-bold tracking-widest text-white uppercase transition-colors duration-300 hover:bg-white/20 hover:text-white"
        onclick={() => alertStore.acknowledge()}
      >
        Acknowledge & Dismiss
      </Button>
    </div>
  </div>
{/if}
