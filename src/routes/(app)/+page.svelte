<script lang="ts">
  import Clock from '$lib/components/Clock.svelte';
  import { alertStore } from '$lib/stores/alert-store.svelte';
  import {
    Ellipsis,
    ArrowUp,
    ArrowDown,
    ChevronDown,
    Shield,
    Hand,
    RefreshCcw
  } from 'lucide-svelte';
  import AlertHistoryModal from '$lib/components/AlertHistoryModal.svelte';
  import Button from '$lib/components/ui/button/button.svelte';

  // ── Derived Live Telemetry data ─────────────────────────────────────────
  let now = $state(Date.now());
  $effect(() => {
    const interval = setInterval(() => {
      now = Date.now();
    }, 1000);
    return () => clearInterval(interval);
  });

  function getTimeAgo(dateString: string | undefined, currentTime: number) {
    if (!dateString) return 'Waiting...';
    const seconds = Math.floor((currentTime - new Date(dateString).getTime()) / 1000);
    if (seconds < 0) return 'Just now';
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  }

  let lastInference = $derived(getTimeAgo(alertStore.latestAlert?.recorded_at, now));
  let lstmConfidence = $derived(alertStore.latestAlert?.confidence_score ?? 0);
  let fftLatency = $derived(alertStore.latestAlert?.fft_latency_ms);
  let sensorTemp = $derived(alertStore.latestAlert?.sensor_temperature_c);

  // ── 4-tier threat legend ───────────────────────────────────────────
  const threatLevels = [
    { label: 'Normal', color: 'bg-threat-normal' },
    { label: 'Minor', color: 'bg-threat-minor' },
    { label: 'Moderate', color: 'bg-threat-moderate' },
    { label: 'Dangerous', color: 'bg-threat-dangerous' }
  ] as const;

  const severityDotColor: Record<string, string> = {
    normal: 'bg-threat-normal',
    minor: 'bg-threat-minor',
    moderate: 'bg-threat-moderate',
    dangerous: 'bg-threat-dangerous'
  };

  // ── Determine the current threat level for the safety card ─────────
  let currentThreat = $derived(alertStore.currentSeverity);
  let threatBg = $derived(
    currentThreat === 'dangerous'
      ? 'bg-threat-dangerous/20 border-threat-dangerous/40'
      : currentThreat === 'moderate'
        ? 'bg-threat-moderate/20 border-threat-moderate/40'
        : currentThreat === 'minor'
          ? 'bg-threat-minor/20 border-threat-minor/40'
          : 'bg-threat-normal/20 border-threat-normal/40'
  );

  // ── Derive display values from live data or fallback ───────────────
  let displayFreq = $derived(alertStore.latestAlert?.frequency_hz);
  let displayX = $derived(alertStore.latestAlert?.raw_x);
  let displayY = $derived(alertStore.latestAlert?.raw_y);
  let displayZ = $derived(alertStore.latestAlert?.raw_z);

  // ── Waveform Chart Logic (Line + Scatter Plot) ─────────────────────
  // We'll normalize the values to a 0-100 range for the SVG viewBox.
  // Assuming a range of 0-250 Hz for the peaks.
  const MAX_VAL = 250;

  function getPath(data: number[]) {
    if (data.length < 2) return '';
    const points = data.map((val, i) => {
      const x = (i / (data.length - 1)) * 100;
      const y = 100 - (Math.min(val, MAX_VAL) / MAX_VAL) * 100;
      return `${x},${y}`;
    });
    return `M ${points.join(' L ')}`;
  }

  function getPoints(data: number[]) {
    return data.map((val, i) => ({
      x: (i / (data.length - 1)) * 100,
      y: 100 - (Math.min(val, MAX_VAL) / MAX_VAL) * 100
    }));
  }

  let lineX = $derived(getPath(alertStore.recentAlerts.map((a) => a.raw_x)));
  let lineY = $derived(getPath(alertStore.recentAlerts.map((a) => a.raw_y)));
  let lineZ = $derived(getPath(alertStore.recentAlerts.map((a) => a.raw_z)));

  let dotsX = $derived(getPoints(alertStore.recentAlerts.map((a) => a.raw_x)));
  let dotsY = $derived(getPoints(alertStore.recentAlerts.map((a) => a.raw_y)));
  let dotsZ = $derived(getPoints(alertStore.recentAlerts.map((a) => a.raw_z)));

  let historyModalOpen = $state(false);

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleString();
  }
</script>

<main
  class="mx-auto min-h-screen max-w-360 p-6 md:mt-2 md:px-16 [&_h3]:font-mono [&_h3]:tracking-tighter"
>
  <!-- Top Header -->
  <div class="mb-8 grid grid-cols-12 items-end gap-6 font-mono text-foreground">
    <div class="col-span-12 text-3xl font-medium tracking-tight lg:col-span-6">Overview</div>
    <div class="col-span-12 text-3xl font-medium tracking-tight lg:col-span-3">
      <Clock />
      <span class="ml-2 text-sm font-normal text-muted-foreground">Time</span>
    </div>
  </div>

  <!-- Bento Grid -->
  <div class="grid grid-cols-12 gap-6">
    <!-- ROW 1 -->

    <!-- ═══ CARD 1: Live Telemetry (Top-Left) ═══ -->
    <div
      class="col-span-12 overflow-hidden rounded-4xl border border-border p-6 lg:col-span-6 lg:p-8"
    >
      <div class="mb-6 flex items-center justify-between">
        <h3 class="text-xl">Live Telemetry</h3>
        <div class="flex items-center gap-2">
          <span class="relative flex h-2.5 w-2.5">
            <span
              class="absolute inline-flex h-full w-full animate-ping rounded-full bg-threat-normal opacity-75"
            ></span>
            <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-threat-normal"></span>
          </span>
          <span class="text-sm text-muted-foreground">Live</span>
        </div>
      </div>

      <!-- Main frequency display -->
      <div class="mb-8 flex items-end gap-4">
        <div class="text-[4.5rem] leading-none font-light tracking-tight">
          {displayFreq ? displayFreq.toFixed(1) : '---'}
        </div>
        <div class="mb-2 text-xl text-muted-foreground">Hz</div>
      </div>

      <!-- 3-axis waveforms (SVG Live Line Charts) -->
      <div class="grid grid-cols-1 gap-12 sm:grid-cols-3 sm:gap-6">
        <!-- X-axis -->
        <div class="flex h-full flex-col justify-end">
          <div class="mb-4 flex items-center justify-between">
            <span class="flex items-center text-sm font-medium text-muted-foreground"
              >X-Axis <ArrowUp class="ml-1 h-3 w-3" /></span
            >
          </div>
          <!-- Line Chart Container -->
          <div class="mb-4 h-24 w-full">
            <svg
              class="h-full w-full overflow-visible"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
            >
              <path
                d={lineX}
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                class="opacity-40"
              />
              {#each dotsX as dot (dot.x)}
                <circle cx={dot.x} cy={dot.y} r="1.2" fill="currentColor" />
              {/each}
            </svg>
          </div>
          <div class="text-2xl leading-none font-light tracking-tight">
            {displayX ? displayX.toFixed(1) : '---'}
          </div>
          <div class="mt-1 text-xs text-muted-foreground">Hz peak</div>
        </div>

        <!-- Y-axis -->
        <div class="flex h-full flex-col justify-end">
          <div class="mb-4 flex items-center justify-between">
            <span class="flex items-center text-sm font-medium text-muted-foreground"
              >Y-Axis <ArrowDown class="ml-1 h-3 w-3" /></span
            >
          </div>
          <div class="mb-4 h-24 w-full">
            <svg
              class="h-full w-full overflow-visible"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
            >
              <path
                d={lineY}
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                class="opacity-40"
              />
              {#each dotsY as dot (dot.x)}
                <circle cx={dot.x} cy={dot.y} r="1.2" fill="currentColor" />
              {/each}
            </svg>
          </div>
          <div class="text-2xl leading-none font-light tracking-tight">
            {displayY ? displayY.toFixed(1) : '---'}
          </div>
          <div class="mt-1 text-xs text-muted-foreground">Hz peak</div>
        </div>

        <!-- Z-axis -->
        <div class="flex h-full flex-col justify-end">
          <div class="mb-4 flex items-center justify-between">
            <span class="flex items-center text-sm font-medium text-muted-foreground"
              >Z-Axis <ArrowDown class="ml-1 h-3 w-3" /></span
            >
          </div>
          <div class="mb-4 h-24 w-full">
            <svg
              class="h-full w-full overflow-visible"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
            >
              <path
                d={lineZ}
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                class="opacity-40"
              />
              {#each dotsZ as dot (dot.x)}
                <circle cx={dot.x} cy={dot.y} r="1.2" fill="currentColor" />
              {/each}
            </svg>
          </div>
          <div class="text-2xl leading-none font-light tracking-tight">
            {displayZ ? displayZ.toFixed(1) : '---'}
          </div>
          <div class="mt-1 text-xs text-muted-foreground">Hz peak</div>
        </div>
      </div>

      <!-- 4-tier threat legend -->
      <div class="mt-8 flex flex-wrap items-center gap-4">
        {#each threatLevels as level (level.label)}
          <div class="flex items-center gap-2">
            <span class="h-3 w-3 rounded-full {level.color}"></span>
            <span class="text-xs text-muted-foreground">{level.label}</span>
          </div>
        {/each}
      </div>
    </div>

    <!-- ═══ CARD 2: Sensor Status & Model (Top-Right, split) ═══ -->
    <div
      class="col-span-12 flex flex-col overflow-hidden rounded-4xl border border-border p-6 lg:col-span-3 lg:p-8"
    >
      <div class="mb-6 flex items-center justify-between">
        <h3 class="text-xl font-medium">Model Health</h3>
        <Ellipsis class="h-5 w-5 text-muted-foreground" />
      </div>

      <div class="mb-6 flex items-center justify-between">
        <span class="text-sm text-muted-foreground"
          >Station <span class="pl-2 text-foreground">Connected</span></span
        >
        <div class="flex h-6 w-11 cursor-pointer items-center rounded-full bg-white p-1">
          <div
            class="h-4 w-4 translate-x-5 rounded-full bg-black shadow-sm transition-transform"
          ></div>
        </div>
      </div>

      <!-- Model metrics -->
      <div class="flex grow flex-col justify-between gap-4">
        <div class="rounded-2xl border border-border/60 bg-transparent p-4">
          <div class="mb-3 text-xs font-medium tracking-wider text-muted-foreground uppercase">
            LSTM Prediction
          </div>
          <div class="flex items-end gap-2">
            <span class="text-3xl font-light tracking-tight"
              >{(lstmConfidence * 100).toFixed(0)}%</span
            >
            <span class="mb-1 text-xs text-muted-foreground">confidence</span>
          </div>
        </div>

        <div class="rounded-2xl border border-border/60 bg-transparent p-4">
          <div class="mb-3 text-xs font-medium tracking-wider text-muted-foreground uppercase">
            FFT Processing
          </div>
          <div class="flex items-end gap-2">
            <span class="text-3xl font-light tracking-tight"
              >{fftLatency ? fftLatency.toFixed(1) : '--'}</span
            >
            <span class="mb-1 text-xs text-muted-foreground">ms latency</span>
          </div>
        </div>

        <div class="mt-2 flex items-center justify-between">
          <span class="text-sm text-muted-foreground">Sensor temp</span>
          <div class="mx-4 h-0.5 grow bg-muted-foreground/30"></div>
          <span
            class="text-xl font-medium {sensorTemp ? 'text-foreground' : 'text-muted-foreground'}"
            >{sensorTemp ? `${sensorTemp.toFixed(1)}°C` : 'N/A'}</span
          >
        </div>
      </div>
    </div>

    <!-- ═══ CARD 3: Duck Cover Hold (Top-Right) ═══ -->
    <div
      class="col-span-12 flex flex-col justify-between overflow-hidden rounded-4xl border p-6 transition-colors duration-500 lg:col-span-3 lg:p-8 {threatBg}"
    >
      <div>
        <div class="mb-6 flex items-center justify-between">
          <h3 class="text-xl font-medium">Safety Protocol</h3>
          <Ellipsis class="h-5 w-5 text-muted-foreground" />
        </div>
        <p class="text-sm text-muted-foreground">In case of an earthquake</p>
      </div>

      <div class="mt-8 flex flex-col gap-4">
        <!-- Duck -->
        <div
          class="flex items-center gap-4 rounded-2xl border border-border/60 bg-background/40 p-4 shadow-sm backdrop-blur-sm"
        >
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-foreground/10"
          >
            <ArrowDown class="h-5 w-5 text-foreground" />
          </div>
          <div>
            <p class="text-sm font-semibold text-foreground">Drop</p>
            <p class="text-xs text-muted-foreground">Get down on your hands and knees</p>
          </div>
        </div>

        <!-- Cover -->
        <div
          class="flex items-center gap-4 rounded-2xl border border-border/60 bg-background/40 p-4 shadow-sm backdrop-blur-sm"
        >
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-foreground/10"
          >
            <Shield class="h-5 w-5 text-foreground" />
          </div>
          <div>
            <p class="text-sm font-semibold text-foreground">Cover</p>
            <p class="text-xs text-muted-foreground">Take cover under a sturdy desk or table</p>
          </div>
        </div>

        <!-- Hold -->
        <div
          class="flex items-center gap-4 rounded-2xl border border-border/60 bg-background/40 p-4 shadow-sm backdrop-blur-sm"
        >
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-foreground/10"
          >
            <Hand class="h-5 w-5 text-foreground" />
          </div>
          <div>
            <p class="text-sm font-semibold text-foreground">Hold On</p>
            <p class="text-xs text-muted-foreground">Stay until the shaking stops</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ROW 2 -->

    <!-- ═══ CARD 4: Tracking / Forecast (Bottom-Left) ═══ -->
    <div
      class="col-span-12 flex flex-col justify-between overflow-hidden rounded-4xl border border-neutral/10 bg-neutral p-6 text-neutral-foreground lg:col-span-4 lg:p-8"
    >
      <div>
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-xl font-medium">Status</h3>
          <Ellipsis class="h-5 w-5 opacity-50" />
        </div>
        <p class="text-sm text-balance opacity-70">Current threat level</p>
      </div>
      <div>
        <div class="mb-2 flex items-center gap-3">
          <span class="h-4 w-4 rounded-full {severityDotColor[currentThreat]}"></span>
          <span class="text-lg font-medium capitalize">{currentThreat}</span>
        </div>
        <div class="mt-2 text-sm opacity-70">
          Last inference: {lastInference}
        </div>
        <div class="text-sm opacity-70">Uptime: N/A</div>
      </div>
    </div>

    <!-- ═══ CARD 6: Alert History (Bottom-Right) ═══ -->
    <div
      class="col-span-12 flex flex-col overflow-hidden rounded-4xl border border-border p-6 lg:col-span-8 lg:p-8"
    >
      <div class="mb-6 flex items-center justify-between">
        <h3 class="text-xl font-medium">Alert history</h3>
        <div class="flex items-center gap-2">
          <Button
            onclick={() => alertStore.init()}
            variant="outline"
            class="aspect-square rounded-full"
            title="Refresh"
          >
            <RefreshCcw class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            onclick={() => (historyModalOpen = true)}
            class="rounded-full   "
          >
            View all
          </Button>
        </div>
      </div>

      <!-- Scrollable alert list -->
      <div class="flex flex-col gap-2 overflow-y-auto" style="max-height: 240px;">
        {#each alertStore.alertHistory as entry (entry.id)}
          <div
            class="flex items-center gap-4 rounded-2xl border border-border/40 px-5 py-3 transition-colors hover:bg-foreground/5"
          >
            <span class="h-3 w-3 shrink-0 rounded-full {severityDotColor[entry.severity]}"></span>
            <span class="grow text-sm text-muted-foreground">{formatDate(entry.recorded_at)}</span>
            <span class="text-sm font-medium text-foreground"
              >{entry.frequency_hz.toFixed(1)} Hz</span
            >
            <span
              class="rounded-full px-2.5 py-0.5 text-xs font-medium capitalize {entry.severity ===
              'normal'
                ? 'bg-threat-normal/20 text-threat-normal'
                : entry.severity === 'minor'
                  ? 'bg-threat-minor/20 text-threat-minor'
                  : entry.severity === 'moderate'
                    ? 'bg-threat-moderate/20 text-threat-moderate'
                    : 'bg-threat-dangerous/20 text-threat-dangerous'}"
            >
              {entry.severity}
            </span>
          </div>
        {/each}
      </div>
    </div>
  </div>
</main>

<AlertHistoryModal bind:open={historyModalOpen} />
