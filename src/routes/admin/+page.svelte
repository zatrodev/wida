<script lang="ts">
  import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardDescription,
    CardFooter
  } from '$lib/components/ui/card';
  import { Button } from '$lib/components/ui/button';
  import { Label } from '$lib/components/ui/label';
  import { Switch } from '$lib/components/ui/switch';
  import { Activity, ShieldAlert, Download, Settings, ServerCrash, Funnel } from 'lucide-svelte';
  import ModeToggle from '$lib/components/ModeToggle.svelte';
  import { curveNatural } from 'd3-shape';

  import * as Chart from '$lib/components/ui/chart';
  import { LineChart } from 'layerchart';
  import { alertStore } from '$lib/stores/alert-store.svelte';
  import { onMount } from 'svelte';

  let triggeringOverride = $state(false);

  let activeFilters = $state({
    frequency_hz: true,
    raw_x: true,
    raw_y: true,
    raw_z: true
  });

  const chartConfig = {
    frequency_hz: {
      label: 'Natural Frequency',
      color: 'var(--color-chart-1)'
    },
    raw_x: {
      label: 'Raw X Axis',
      color: 'var(--color-chart-2)'
    },
    raw_y: {
      label: 'Raw Y Axis',
      color: 'var(--color-chart-3)'
    },
    raw_z: {
      label: 'Raw Z Axis',
      color: 'var(--color-chart-4)'
    }
  } satisfies Chart.ChartConfig;

  let chartData = $derived([...alertStore.alertHistory].reverse());

  onMount(() => {
    alertStore.init();
  });

  function exportCSV() {
    const data = alertStore.alertHistory;
    if (!data.length) return;

    const headers = [
      'ID',
      'Device ID',
      'Recorded At',
      'Frequency (Hz)',
      'Raw X',
      'Raw Y',
      'Raw Z',
      'Severity',
      'Confidence Score',
      'FFT Latency (ms)',
      'Temperature (C)'
    ];

    const rows = data.map((alert) => [
      alert.id,
      alert.device_id,
      alert.recorded_at,
      alert.frequency_hz,
      alert.raw_x,
      alert.raw_y,
      alert.raw_z,
      alert.severity,
      alert.confidence_score,
      alert.fft_latency_ms ?? '',
      alert.sensor_temperature_c ?? ''
    ]);

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `wida_telemetry_export_${new Date().toISOString().slice(0, 10)}.csv`;
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async function triggerEmergencyOverride() {
    triggeringOverride = true;
    try {
      await fetch('/api/emergency-override', { method: 'POST' });
      // Give it a short delay for visual feedback before button resets
      setTimeout(() => {
        triggeringOverride = false;
      }, 1500);
    } catch (error) {
      console.error('Test failed', error);
      triggeringOverride = false;
    }
  }
</script>

<main
  class="container mx-auto mt-8 flex max-w-5xl flex-col p-4 md:p-8 [&_h1]:font-mono [&_h3]:tracking-tighter"
>
  <ModeToggle class="ml-auto size-10 " />
  <div class="mb-8 flex gap-3">
    <ShieldAlert class="mt-2 text-primary sm:size-8" />
    <div>
      <h1 class="text-xl tracking-tight sm:text-3xl">Administrator Portal</h1>
      <p class="text-muted-foreground">System configuration and emergency overrides</p>
    </div>
  </div>

  <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
    <Card
      class="border-destructive/30 bg-destructive/5 transition-colors hover:border-destructive/50"
    >
      <CardHeader>
        <CardTitle class="flex items-center gap-2 text-destructive">
          <ServerCrash class="h-5 w-5" />
          Emergency Override
        </CardTitle>
        <CardDescription>
          Manually trigger the global earthquake alert system across all active client devices. Use
          strictly for testing or verified undocumented emergencies.
        </CardDescription>
      </CardHeader>
      <CardContent class="pt-4">
        <Button
          variant="destructive"
          class="h-16 w-full font-mono font-bold tracking-wider uppercase disabled:opacity-50 "
          onclick={triggerEmergencyOverride}
          disabled={triggeringOverride}
        >
          {triggeringOverride ? 'Transmitting Alert...' : 'Push Global Alert Signal'}
        </Button>
      </CardContent>
    </Card>

    <Card class="bg-background/80">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Settings class="h-5 w-5" />
          Hardware Configuration
        </CardTitle>
        <CardDescription>Manage the Raspberry Pi edge device thresholds.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="flex items-center justify-between rounded-lg border p-4">
          <div class="space-y-0.5">
            <Label class="text-base">Telegram Broadcasts</Label>
            <p class="text-sm text-muted-foreground">
              Push notifications to the community channel.
            </p>
          </div>
          <Switch id="telegram-alerts" checked={true} />
        </div>
      </CardContent>
      <CardFooter>
        <Button class="w-full">Save Configuration</Button>
      </CardFooter>
    </Card>

    <Card class="md:col-span-2">
      <CardHeader>
        <CardTitle class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Activity class="h-5 w-5" />
            Data Analytics & Export
          </div>
          <Button variant="outline" size="sm" class="gap-2" onclick={exportCSV}>
            <Download class="h-4 w-4" />
            Export CSV
          </Button>
        </CardTitle>
        <CardDescription>Historical data needed for research profiling.</CardDescription>
      </CardHeader>
      <CardContent class="h-full w-full">
        <!-- Interactive Filter Bar -->
        <div class="mb-6 flex flex-wrap items-center gap-3">
          <div class="mr-2 flex items-center gap-2 text-sm text-muted-foreground">
            <Funnel class="h-4 w-4" />
            Filters:
          </div>

          <Button
            variant="outline"
            size="sm"
            onclick={() => (activeFilters.frequency_hz = !activeFilters.frequency_hz)}
            style="background-color: {activeFilters.frequency_hz
              ? 'var(--chart-1)'
              : 'transparent'}; color: {activeFilters.frequency_hz
              ? '#082F49'
              : 'var(--chart-1)'}; border-color: var(--chart-1);"
          >
            Natural Freq
          </Button>

          <Button
            variant="outline"
            size="sm"
            onclick={() => (activeFilters.raw_x = !activeFilters.raw_x)}
            style="background-color: {activeFilters.raw_x
              ? 'var(--chart-2)'
              : 'transparent'}; color: {activeFilters.raw_x
              ? '#1E1B4B'
              : 'var(--chart-2)'}; border-color: var(--chart-2);"
          >
            Raw X
          </Button>

          <Button
            variant="outline"
            size="sm"
            onclick={() => (activeFilters.raw_y = !activeFilters.raw_y)}
            style="background-color: {activeFilters.raw_y
              ? 'var(--chart-3)'
              : 'transparent'}; color: {activeFilters.raw_y
              ? '#022C22'
              : 'var(--chart-3)'}; border-color: var(--chart-3);"
          >
            Raw Y
          </Button>

          <Button
            variant="outline"
            size="sm"
            onclick={() => (activeFilters.raw_z = !activeFilters.raw_z)}
            style="background-color: {activeFilters.raw_z
              ? 'var(--chart-4)'
              : 'transparent'}; color: {activeFilters.raw_z
              ? '#500724'
              : 'var(--chart-4)'}; border-color: var(--chart-4);"
          >
            Raw Z
          </Button>
        </div>

        <!-- The actual Chart Mount -->
        <div class="h-64 w-full sm:h-80 lg:h-96">
          {#if chartData.length > 0}
            <Chart.Container config={chartConfig} class="h-full w-full">
              <LineChart
                data={chartData}
                x="recorded_at"
                padding={{ left: 16, right: 16 }}
                props={{
                  xAxis: { rule: false, format: (v: string) => '' },
                  spline: { curve: curveNatural, motion: 'tween', strokeWidth: 2 },
                  highlight: { points: { r: 4 } }
                }}
                series={[
                  ...(activeFilters.frequency_hz
                    ? [{ key: 'frequency_hz', color: 'var(--color-chart-1)' }]
                    : []),
                  ...(activeFilters.raw_x ? [{ key: 'raw_x', color: 'var(--color-chart-2)' }] : []),
                  ...(activeFilters.raw_y ? [{ key: 'raw_y', color: 'var(--color-chart-3)' }] : []),
                  ...(activeFilters.raw_z ? [{ key: 'raw_z', color: 'var(--color-chart-4)' }] : [])
                ]}
              >
                {#snippet tooltip()}
                  <Chart.Tooltip
                    labelFormatter={(value: string) => new Date(value).toLocaleString()}
                  />
                {/snippet}
              </LineChart>
            </Chart.Container>
          {:else}
            <div
              class="flex h-full w-full items-center justify-center rounded-xl border-2 border-dashed border-border bg-muted/50"
            >
              <p class="animate-pulse text-sm font-medium text-muted-foreground">
                Waiting for telemetry data...
              </p>
            </div>
          {/if}
        </div>
      </CardContent>
    </Card>
  </div>
</main>
