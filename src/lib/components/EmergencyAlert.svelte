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
</script>

{#if alertStore.isQuakeActive}
  <div
    class="fixed inset-0 z-50 flex animate-[pulse_1.5s_ease-in-out_infinite] items-center justify-center bg-destructive/95 backdrop-blur-md"
    role="alertdialog"
    aria-modal="true"
  >
    <div
      class="w-full max-w-md scale-100 transform rounded-3xl border border-destructive bg-black/60 p-8 text-center shadow-2xl backdrop-blur-lg transition-all duration-300"
    >
      <AlertTriangle
        class="mx-auto mb-6 h-32 w-32 animate-bounce text-destructive drop-shadow-lg"
      />
      <h1 class="mb-4 text-5xl font-extrabold tracking-tighter text-white uppercase drop-shadow-md">
        Earthquake<br />Detected
      </h1>

      <p class="text-destructive-foreground mb-8 text-lg font-medium">
        Seek cover immediately! Drop, Cover, and Hold on until shaking stops.
      </p>

      {#if alertStore.latestAlert}
        <div class="mb-8 rounded-2xl border border-destructive/50 bg-destructive/20 p-4 text-left">
          <div class="text-destructive-foreground mb-2 flex items-center">
            <Activity class="mr-2 h-4 w-4" />
            <span class="text-sm font-semibold tracking-wider uppercase">Sensor Feedback</span>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="mb-1 block text-xs text-destructive/80">Confidence</span>
              <span class="text-xl font-bold text-white drop-shadow-sm"
                >{(alertStore.latestAlert.confidence_score * 100).toFixed(1)}%</span
              >
            </div>
            <div>
              <span class="mb-1 block text-xs text-destructive/80">Impact Axis (Z)</span>
              <span class="text-xl font-bold text-white drop-shadow-sm"
                >{alertStore.latestAlert.z_axis.toFixed(2)}G</span
              >
            </div>
          </div>
        </div>
      {/if}

      <Button
        variant="outline"
        class="text-destructive-foreground hover:text-destructive-foreground h-16 w-full rounded-xl border-2 border-destructive/60 text-lg font-bold tracking-widest uppercase transition-colors duration-300 hover:bg-destructive"
        onclick={() => alertStore.acknowledge()}
      >
        Acknowledge & Dismiss
      </Button>
    </div>
  </div>
{/if}
