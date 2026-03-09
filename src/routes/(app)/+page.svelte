<script lang="ts">
  import Clock from '$lib/components/Clock.svelte';
  import { MoreHorizontal, ArrowUp, ArrowDown, ChevronDown } from 'lucide-svelte';

  const chart1 = [20, 25, 30, 40, 50, 45, 60, 55, 70, 65, 80, 75, 90, 85, 100, 95];
  const chart2 = [40, 35, 30, 25, 20, 30, 40, 50, 45, 55, 60, 50, 60, 45, 55];
  const chart3 = [30, 40, 50, 60, 70, 65, 80, 90, 85, 75, 65, 55, 80, 95, 85, 70];

  const timeline = [
    { time: '11AM', state: 'empty' },
    { time: '11AM', state: 'filled' },
    { time: '12PM', state: 'filled' },
    { time: '1PM', state: 'filled' },
    { time: '2PM', state: 'filled' },
    { time: '3PM', state: 'filled' },
    { time: '4PM', state: 'empty' }
  ];

  const reportData = [
    { day: 'Mon', arrow: ArrowUp, val: 276, active: false },
    { day: 'Tue', arrow: ArrowUp, val: 282, active: false },
    { day: 'Wed', arrow: ArrowUp, val: 297, active: true },
    { day: 'Thu', arrow: ArrowDown, val: 269, active: false },
    { day: 'Fri', arrow: ArrowUp, val: 274, active: false },
    { day: 'Sat', arrow: ArrowDown, val: 175, active: false },
    { day: 'Sun', arrow: ArrowDown, val: 138, active: false }
  ];
</script>

<main
  class="mx-auto min-h-screen max-w-360 p-6 md:mt-2 md:px-16 [&_h3]:font-mono [&_h3]:tracking-tighter"
>
  <!-- Top Header aligned exactly to grid -->
  <div class="mb-8 grid grid-cols-12 items-end gap-6 font-mono text-foreground">
    <div class="col-span-12 text-3xl font-medium tracking-tight lg:col-span-6">Overview</div>
    <div class="col-span-12 text-3xl font-medium tracking-tight lg:col-span-3">
      <Clock />
      <span class="ml-2 text-sm font-normal text-muted-foreground">Time</span>
    </div>
    <div class="col-span-12 text-right text-3xl font-medium tracking-tight lg:col-span-3">
      9 September
    </div>
  </div>

  <!-- Bento Grid -->
  <div class="grid grid-cols-12 gap-6">
    <!-- ROW 1 -->
    <!-- Card 1: Total energy consumption => Seismic Activity -->
    <div
      class="col-span-12 overflow-hidden rounded-[2rem] border border-border p-6 lg:col-span-6 lg:p-8"
    >
      <div class="mb-10 flex items-center justify-between">
        <h3 class="text-xl">Total seismic activities</h3>
        <button
          class="rounded-full border border-border bg-transparent px-4 py-1.5 text-sm transition-colors hover:bg-white/10"
        >
          Change sensors
        </button>
      </div>

      <div class="grid grid-cols-3 gap-6">
        <!-- Sub-chart 1 -->
        <div class="flex h-full flex-col justify-end">
          <div class="mb-6 flex items-center justify-between">
            <span class="flex items-center text-sm font-medium text-muted-foreground"
              >Primary <ArrowUp class="ml-1 h-3 w-3" /></span
            >
            <MoreHorizontal class="h-4 w-4 text-muted-foreground" />
          </div>
          <div class="mb-6 flex h-28 items-end gap-[3px]">
            {#each chart1 as height, i (i)}
              <div
                class="w-full rounded-full transition-all {i > chart1.length - 6
                  ? 'bg-foreground'
                  : 'bg-foreground/20'}"
                style="height: {height}%"
              ></div>
            {/each}
          </div>
          <div class="text-[2.5rem] leading-none font-light tracking-tight">52-71</div>
          <div class="mt-2 text-xs text-muted-foreground">hz per month</div>
        </div>

        <!-- Sub-chart 2 -->
        <div class="flex h-full flex-col justify-end">
          <div class="mb-6 flex items-center justify-between">
            <span class="flex items-center text-sm font-medium text-muted-foreground"
              >Secondary <ArrowDown class="ml-1 h-3 w-3" /></span
            >
            <MoreHorizontal class="h-4 w-4 text-muted-foreground" />
          </div>
          <div class="mb-6 flex h-28 items-end gap-[3px]">
            {#each chart2 as height, i}
              <div
                class="w-full rounded-full transition-all {i < 5
                  ? 'bg-foreground'
                  : 'bg-foreground/20'}"
                style="height: {height}%"
              ></div>
            {/each}
          </div>
          <div class="text-[2.5rem] leading-none font-light tracking-tight">29-37</div>
          <div class="mt-2 text-xs text-muted-foreground">hz per month</div>
        </div>

        <!-- Sub-chart 3 -->
        <div class="flex h-full flex-col justify-end">
          <div class="mb-6 flex items-center justify-between">
            <span class="flex items-center text-sm font-medium text-muted-foreground"
              >Tertiary <ArrowDown class="ml-1 h-3 w-3" /></span
            >
            <MoreHorizontal class="h-4 w-4 text-muted-foreground" />
          </div>
          <div class="mb-6 flex h-28 items-end gap-[3px]">
            {#each chart3 as height, i}
              <div
                class="w-full rounded-full transition-all {i > chart3.length - 8 &&
                i < chart3.length - 2
                  ? 'bg-foreground'
                  : 'bg-foreground/20'}"
                style="height: {height}%"
              ></div>
            {/each}
          </div>
          <div class="text-[2.5rem] leading-none font-light tracking-tight">49-85</div>
          <div class="mt-2 text-xs text-muted-foreground">hz per month</div>
        </div>
      </div>
    </div>

    <!-- Card 2: Green connections => Sensor connections -->
    <div
      class="col-span-12 flex flex-col overflow-hidden rounded-[2rem] border border-border p-6 lg:col-span-3 lg:p-8"
    >
      <div class="mb-6 flex items-center justify-between">
        <h3 class="text-xl font-medium">Sensor connections</h3>
        <MoreHorizontal class="h-5 w-5 text-muted-foreground" />
      </div>

      <div class="mb-6 flex items-center justify-between">
        <span class="text-sm text-muted-foreground"
          >Station <span class="pl-2 text-foreground">Connected</span></span
        >
        <!-- Custom styled toggle mirroring the screenshot -->
        <div class="flex h-6 w-11 cursor-pointer items-center rounded-full bg-white p-1">
          <div
            class="h-4 w-4 translate-x-5 rounded-full bg-black shadow-sm transition-transform"
          ></div>
        </div>
      </div>

      <!-- Glowing Isometric abstract room graphic -->
      <div
        class="relative my-4 flex aspect-video w-full flex-grow items-center justify-center overflow-hidden rounded-xl border border-border/20 bg-black/20"
      >
        <div
          class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:15px_15px]"
        ></div>
        <!-- Scanning glowing line -->
        <div
          class="absolute top-1/2 left-0 z-10 h-[1.5px] w-full bg-green-400/80 shadow-[0_0_20px_4px_rgba(74,222,128,0.5)]"
        ></div>
        <!-- Abstract central box -->
        <div
          class="absolute inset-4 flex items-center justify-center rounded-lg border-2 border-dashed border-green-500/20"
        >
          <div class="relative h-10 w-16 rounded-sm border border-green-500/40">
            <div class="absolute -bottom-3 left-1/2 h-3 w-5 -translate-x-1/2 bg-green-500/20"></div>
            <div
              class="absolute -bottom-4 left-1/2 h-[2px] w-10 -translate-x-1/2 bg-green-500/40"
            ></div>
          </div>
        </div>
      </div>

      <div class="mt-4 flex items-center justify-between">
        <span class="text-sm text-muted-foreground">Available memory</span>
        <div class="mx-4 h-[2px] flex-grow bg-muted-foreground/30"></div>
        <span class="text-xl font-medium">83%</span>
      </div>
    </div>

    <!-- Card 3: Recommendations -->
    <div
      class="col-span-12 flex flex-col justify-between overflow-hidden rounded-[2rem] border border-border p-6 lg:col-span-3 lg:p-8"
    >
      <div>
        <div class="mb-6 flex items-center justify-between">
          <h3 class="text-xl font-medium">Recommendations</h3>
          <MoreHorizontal class="h-5 w-5 text-muted-foreground" />
        </div>
        <p class="text-sm text-muted-foreground">Personalized tips for optimizing safety</p>
      </div>

      <div class="mt-8 flex flex-col gap-4">
        <!-- Light neutral recommendation box -->
        <div class="rounded-[1.5rem] bg-neutral p-6 text-neutral-foreground">
          <p class="mb-6 text-sm leading-relaxed">
            Stable day ahead! We recommend maximizing sensor battery usage b...
          </p>
          <p class="text-xs opacity-60">Today recommendation</p>
        </div>

        <!-- Dark recommendation box -->
        <div class="rounded-[1.5rem] border border-border/60 bg-transparent p-6">
          <p class="mb-6 text-sm leading-relaxed text-foreground">
            Run diagnostics after 8 PM to reduce network load.
          </p>
          <div class="flex items-center justify-between text-xs text-muted-foreground">
            <span>Analysis</span>
            <span>5 min</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ROW 2 -->
    <!-- Card 4: Tracking (Light neutral card) -->
    <div
      class="col-span-12 flex flex-col justify-between overflow-hidden rounded-[2rem] border border-neutral/10 bg-neutral p-6 text-neutral-foreground lg:col-span-2 lg:p-8"
    >
      <div>
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-xl font-medium">Tracking</h3>
          <MoreHorizontal class="h-5 w-5 opacity-50" />
        </div>
        <p class="text-sm opacity-70">Seismic energy tomorrow</p>
      </div>
      <div>
        <div class="text-[5rem] leading-none font-light tracking-tight">5.7</div>
        <div class="mt-2 text-sm opacity-70">Mag</div>
      </div>
    </div>

    <!-- Card 5: Detailed report -->
    <div
      class="col-span-12 flex flex-col justify-between overflow-hidden rounded-[2rem] border border-border p-6 lg:col-span-4 lg:p-8"
    >
      <div>
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-xl font-medium">Detailed report</h3>
          <button
            class="flex items-center gap-1 rounded-full border border-border px-4 py-1.5 text-sm transition-colors hover:bg-white/10"
          >
            Week <ChevronDown class="h-3 w-3" />
          </button>
        </div>
        <p class="text-sm text-muted-foreground">Graphs of seismic activities</p>
      </div>

      <div class="mt-8 flex w-full flex-col">
        <div class="flex w-full justify-between pb-6 text-xs text-muted-foreground">
          {#each reportData as d}
            <div class="-mr-2 flex flex-col justify-end last:mr-0">
              <span class="mb-4 flex items-center"
                >{d.day} <d.arrow class="ml-[2px] h-3 w-3" /></span
              >
              <span class="text-[13px] {d.active ? 'font-bold text-foreground' : 'text-foreground'}"
                >{d.val}</span
              >
              <span class="mt-0.5">Hz</span>
            </div>
          {/each}
        </div>
        <!-- Bar below the graphs matching the screenshot exactly -->
        <div class="flex h-[6px] w-full overflow-hidden rounded bg-border">
          <div class="w-[28.5%] bg-transparent"></div>
          <!-- Skips Mon & Tue -->
          <div class="w-[14.28%] bg-white"></div>
          <!-- Highlights Wed -->
        </div>
      </div>
    </div>

    <!-- Card 6: Green energy usage => Clean system usage (Light neutral card) -->
    <div
      class="col-span-12 flex flex-col justify-between overflow-hidden rounded-[2rem] border border-neutral/10 bg-neutral p-6 text-neutral-foreground lg:col-span-6 lg:p-8"
    >
      <div class="mb-10 flex items-center justify-between">
        <h3 class="text-xl font-medium">Clean system usage</h3>
        <button
          class="rounded-full border border-neutral-foreground/20 px-5 py-2 text-sm transition-colors hover:bg-black/5"
        >
          Change
        </button>
      </div>

      <div class="grid flex-grow grid-cols-12 items-end">
        <div class="col-span-4 flex flex-col">
          <p class="mb-6 text-sm opacity-70">Clean system usage</p>
          <div class="text-[5rem] leading-none font-light tracking-tight">47%</div>
          <div class="mt-3 text-sm font-medium tracking-wide opacity-70">11AM — 3PM</div>
        </div>

        <div class="col-span-8 flex justify-end pb-2">
          <!-- Timeline graphic -->
          <div class="relative flex w-full max-w-sm items-center justify-between">
            <!-- Dashed line connecting circles -->
            <div
              class="absolute top-[11px] left-0 -z-10 w-full border-b-[1.5px] border-dashed border-neutral-foreground/30"
            ></div>

            {#each timeline as t}
              <div class="flex flex-col items-center gap-3">
                {#if t.state === 'empty'}
                  <div
                    class="h-[22px] w-[22px] rounded-full border-[1.5px] border-neutral-foreground/50 bg-neutral"
                  ></div>
                {:else}
                  <div class="h-[22px] w-[22px] rounded-full bg-neutral-foreground shadow-sm"></div>
                {/if}
                <span class="text-[10px] font-medium tracking-wider uppercase opacity-70"
                  >{t.time}</span
                >
              </div>
            {/each}
          </div>
        </div>
      </div>
    </div>
  </div>
</main>
