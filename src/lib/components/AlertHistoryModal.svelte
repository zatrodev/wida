<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { X, ChevronLeft, ChevronRight, RefreshCcw } from 'lucide-svelte';
  import { supabase } from '$lib/supabase';
  import type { AlertEvent, Severity } from '$lib/stores/alert-store.svelte';
  import { fade, fly } from 'svelte/transition';

  let { open = $bindable(false) } = $props();

  // ── State for Filtering & Pagination ─────────────────────────────
  let alerts = $state<AlertEvent[]>([]);
  let loading = $state(false);
  let page = $state(1);
  const pageSize = 20;
  let totalCount = $state(0);

  let filterSeverity = $state<Severity | 'all'>('all');
  let minConfidence = $state(0);
  let scrollY = $state(0);

  // ── Fetch Logic ──────────────────────────────────────────────────
  async function fetchHistory() {
    loading = true;
    try {
      let query = supabase
        .from('alerts')
        .select('*', { count: 'exact' })
        .order('recorded_at', { ascending: false });

      if (filterSeverity !== 'all') {
        query = query.eq('severity', filterSeverity);
      }

      if (minConfidence > 0) {
        query = query.gte('confidence_score', minConfidence / 100);
      }

      const from = (page - 1) * pageSize;
      const to = from + pageSize - 1;

      const { data, count, error } = await query.range(from, to);

      if (error) throw error;

      alerts = (data as AlertEvent[]) || [];
      totalCount = count || 0;
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      loading = false;
    }
  }

  // Refetch when filters or page change
  $effect(() => {
    if (open) {
      fetchHistory();
    }
  });

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleString();
  }

  const severityColors: Record<string, string> = {
    normal: 'text-threat-normal bg-threat-normal/10 border-threat-normal/20',
    minor: 'text-threat-minor bg-threat-minor/10 border-threat-minor/20',
    moderate: 'text-threat-moderate bg-threat-moderate/10 border-threat-moderate/20',
    dangerous: 'text-threat-dangerous bg-threat-dangerous/10 border-threat-dangerous/20'
  };

  const totalPages = $derived(Math.ceil(totalCount / pageSize));
</script>

<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm">
      {#snippet child({ props })}
        <div {...props} transition:fade={{ duration: 150 }}></div>
      {/snippet}
    </Dialog.Overlay>

    <Dialog.Content
      class="fixed top-[50%] left-[50%] z-50 flex max-h-[95dvh] w-full max-w-4xl translate-x-[-50%] translate-y-[-50%] flex-col overflow-hidden rounded-4xl border border-border bg-background shadow-2xl outline-none"
    >
      {#snippet child({ props })}
        {@const stickyVisible = scrollY > 200}
        <div
          {...props}
          transition:fly={{ y: 8, duration: 200 }}
          class="{props.class} flex h-full flex-col overflow-hidden"
        >
          <!-- Fixed Top Header -->
          <div class="flex items-center justify-between p-8 pb-4">
            <div>
              <Dialog.Title class="font-mono text-3xl font-medium tracking-tighter">
                Full Alert History
              </Dialog.Title>
              <Dialog.Description class="text-sm text-muted-foreground">
                Browse and filter through all recorded seismic events.
              </Dialog.Description>
            </div>
            <Dialog.Close
              class="rounded-full border border-border p-2 transition-colors hover:bg-foreground/5"
            >
              <X class="h-6 w-6" />
            </Dialog.Close>
          </div>

          <!-- Sticky Header (Appears on scroll) -->
          {#if stickyVisible}
            <div
              transition:fly={{ y: -20, duration: 200 }}
              class="absolute inset-x-0 top-0 z-30 flex items-center justify-between border-b border-border bg-background/80 px-8 py-8 backdrop-blur-md"
            >
              <div class="flex items-center gap-4">
                <Dialog.Title class="font-mono text-xl font-medium tracking-tighter"
                  >History</Dialog.Title
                >
                <div class="h-4 w-px bg-border"></div>
                <div class="flex items-center gap-3">
                  <select
                    bind:value={filterSeverity}
                    class="h-8 rounded-lg border border-border bg-background px-2 text-xs outline-none focus:border-foreground"
                    onchange={() => (page = 1)}
                  >
                    <option value="all">All</option>
                    <option value="normal">Normal</option>
                    <option value="minor">Minor</option>
                    <option value="moderate">Moderate</option>
                    <option value="dangerous">Dangerous</option>
                  </select>
                  <span class="text-[10px] font-bold text-muted-foreground uppercase"
                    >{minConfidence}% Conf</span
                  >
                </div>
              </div>
              <Dialog.Close
                class="rounded-full border border-border p-1.5 transition-colors hover:bg-foreground/5"
              >
                <X class="h-4 w-4" />
              </Dialog.Close>
            </div>
          {/if}

          <!-- Scrollable Body -->
          <div
            class="flex-1 overflow-y-auto px-8 pb-8"
            onscroll={(e) => (scrollY = (e.target as HTMLElement).scrollTop)}
          >
            <!-- Original Filters -->
            <div
              class="mb-8 flex flex-wrap items-end gap-6 rounded-3xl border border-border/50 bg-foreground/5 p-6"
            >
              <div class="flex flex-col gap-2">
                <label
                  for="severity"
                  class="text-xs font-semibold tracking-wider text-muted-foreground uppercase"
                >
                  Severity
                </label>
                <select
                  id="severity"
                  bind:value={filterSeverity}
                  class="h-10 rounded-xl border border-border bg-background px-4 text-sm transition-all outline-none focus:border-foreground"
                  onchange={() => (page = 1)}
                >
                  <option value="all">All Severities</option>
                  <option value="normal">Normal</option>
                  <option value="minor">Minor</option>
                  <option value="moderate">Moderate</option>
                  <option value="dangerous">Dangerous</option>
                </select>
              </div>

              <div class="flex flex-col gap-2">
                <label
                  for="confidence"
                  class="text-xs font-semibold tracking-wider text-muted-foreground uppercase"
                >
                  Min Confidence ({minConfidence}%)
                </label>
                <input
                  id="confidence"
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  bind:value={minConfidence}
                  onchange={() => (page = 1)}
                  class="h-10 w-48 accent-foreground"
                />
              </div>

              <button
                onclick={() => {
                  page = 1;
                  fetchHistory();
                }}
                class="flex h-10 items-center gap-2 rounded-xl border border-border bg-background px-6 text-sm font-medium transition-all hover:bg-foreground hover:text-background active:scale-95"
              >
                <RefreshCcw class="h-4 w-4 {loading ? 'animate-spin' : ''}" />
                Refresh
              </button>
            </div>

            <!-- Table -->
            <div class="relative min-h-100 overflow-hidden rounded-3xl border border-border">
              {#if loading}
                <div
                  class="absolute inset-0 z-10 flex items-center justify-center bg-background/50 backdrop-blur-[1px]"
                >
                  <RefreshCcw class="h-8 w-8 animate-spin opacity-40" />
                </div>
              {/if}

              <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                  <thead
                    class="bg-foreground/5 font-mono text-xs tracking-widest text-muted-foreground uppercase"
                  >
                    <tr>
                      <th class="px-6 py-4">Timestamp</th>
                      <th class="px-6 py-4 text-center">Severity</th>
                      <th class="px-6 py-4 text-center">Frequency</th>
                      <th class="px-6 py-4 text-center">Confidence</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-border">
                    {#each alerts as alert (alert.id)}
                      <tr class="transition-colors hover:bg-foreground/2">
                        <td class="px-6 py-4 font-mono text-muted-foreground">
                          {formatDate(alert.recorded_at)}
                        </td>
                        <td class="px-6 py-4">
                          <div class="flex justify-center">
                            <span
                              class="rounded-full border px-3 py-1 text-xs font-semibold capitalize {severityColors[
                                alert.severity
                              ] || ''}"
                            >
                              {alert.severity}
                            </span>
                          </div>
                        </td>
                        <td class="px-6 py-4 text-center font-medium">
                          {alert.frequency_hz.toFixed(2)}
                          <span class="text-[10px] text-muted-foreground">Hz</span>
                        </td>
                        <td class="px-6 py-4">
                          <div class="flex flex-col items-center gap-1">
                            <div class="h-1.5 w-24 overflow-hidden rounded-full bg-border">
                              <div
                                class="h-full bg-foreground transition-all duration-500"
                                style="width: {alert.confidence_score * 100}%"
                              ></div>
                            </div>
                            <span class="text-[10px] text-muted-foreground"
                              >{(alert.confidence_score * 100).toFixed(0)}%</span
                            >
                          </div>
                        </td>
                      </tr>
                    {:else}
                      <tr>
                        <td colspan="4" class="px-6 py-20 text-center text-muted-foreground">
                          No alerts found matching your criteria.
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Fixed Footer -->
          <div class="border-t border-border bg-foreground/5 p-6 px-8">
            <div class="flex items-center justify-between">
              <div class="text-xs text-muted-foreground">
                Showing <span class="font-bold text-foreground">{(page - 1) * pageSize + 1}</span>
                to
                <span class="font-bold text-foreground"
                  >{Math.min(page * pageSize, totalCount)}</span
                >
                of
                <span class="font-bold text-foreground">{totalCount}</span>
              </div>

              <div class="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onclick={() => {
                    page -= 1;
                    document.querySelector('.flex-1.overflow-y-auto')?.scrollTo(0, 0);
                  }}
                  class="flex items-center gap-1 rounded-xl border border-border p-2 px-3 text-xs font-bold transition-all hover:bg-foreground/5 disabled:opacity-30"
                >
                  <ChevronLeft class="h-3.5 w-3.5" />
                  Prev
                </button>
                <div class="flex items-center gap-1">
                  {#each Array.from({ length: Math.min(5, totalPages) }, (_, i) => i + 1) as p (p)}
                    <button
                      onclick={() => (page = p)}
                      class="h-8 w-8 rounded-lg text-xs font-bold transition-all {page === p
                        ? 'bg-foreground text-background'
                        : 'hover:bg-foreground/5'}"
                    >
                      {p}
                    </button>
                  {/each}
                </div>
                <button
                  disabled={page >= totalPages}
                  onclick={() => {
                    page += 1;
                    document.querySelector('.flex-1.overflow-y-auto')?.scrollTo(0, 0);
                  }}
                  class="flex items-center gap-1 rounded-xl border border-border p-2 px-3 text-xs font-bold transition-all hover:bg-foreground/5 disabled:opacity-30"
                >
                  Next
                  <ChevronRight class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      {/snippet}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
