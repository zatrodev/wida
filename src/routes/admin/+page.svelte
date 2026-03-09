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
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Switch } from '$lib/components/ui/switch';
  import { Activity, ShieldAlert, Download, Settings, ServerCrash } from 'lucide-svelte';

  let testingSystem = $state(false);

  async function runSystemTest() {
    testingSystem = true;
    try {
      await fetch('/api/test-alert', { method: 'POST' });
      // Give it a short delay for visual feedback before button resets
      setTimeout(() => {
        testingSystem = false;
      }, 1500);
    } catch (error) {
      console.error('Test failed', error);
      testingSystem = false;
    }
  }
</script>

<main class="container mx-auto max-w-5xl p-4 md:p-8">
  <div class="mb-8 flex items-center gap-3">
    <ShieldAlert class="h-10 w-10 text-primary" />
    <div>
      <h1 class="text-3xl font-extrabold tracking-tight">Administrator Portal</h1>
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
          class="h-16 w-full text-lg font-bold tracking-wider uppercase disabled:opacity-50"
          onclick={runSystemTest}
          disabled={testingSystem}
        >
          {testingSystem ? 'Transmitting Alert...' : 'Push Global Alert Signal'}
        </Button>
      </CardContent>
    </Card>

    <Card class="bg-white/50 backdrop-blur-sm dark:bg-black/50">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Settings class="h-5 w-5" />
          Hardware Configuration
        </CardTitle>
        <CardDescription>Manage the Raspberry Pi edge device thresholds.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="space-y-4">
          <div class="flex flex-col space-y-2">
            <Label for="threshold" class="text-sm font-semibold"
              >Sensor Sensitivity Threshold (G-Force)</Label
            >
            <Input id="threshold" type="number" step="0.1" value="1.5" placeholder="e.g. 1.5" />
            <p class="text-xs text-muted-foreground">
              Lower values will trigger alerts on smaller vibrations.
            </p>
          </div>

          <div class="flex items-center justify-between rounded-lg border p-4">
            <div class="space-y-0.5">
              <Label class="text-base">Telegram Broadcasts</Label>
              <p class="text-sm text-muted-foreground">
                Push notifications to the community channel.
              </p>
            </div>
            <Switch id="telegram-alerts" checked={true} />
          </div>
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
          <Button variant="outline" size="sm" class="gap-2">
            <Download class="h-4 w-4" />
            Export CSV
          </Button>
        </CardTitle>
        <CardDescription>Historical data needed for research profiling.</CardDescription>
      </CardHeader>
      <CardContent>
        <div
          class="flex h-48 items-center justify-center rounded-xl border-2 border-dashed border-border bg-muted/50"
        >
          <p class="text-sm font-medium text-muted-foreground">
            Analytics chart visualization will be mounted here.
          </p>
        </div>
      </CardContent>
    </Card>
  </div>
</main>
