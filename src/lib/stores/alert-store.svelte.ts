import { supabase } from '$lib/supabase';

// Definition of an alert item from the DB
export type AlertEvent = {
  id: number;
  timestamp: string;
  x_axis: number;
  y_axis: number;
  z_axis: number;
  is_quake: boolean;
  confidence_score: number;
};

// Global reactive state for the current active quake
export class AlertStore {
  isQuakeActive = $state(false);
  latestAlert = $state<AlertEvent | null>(null);

  private channel: ReturnType<typeof supabase.channel> | null = null;

  init() {
    if (this.channel) return;

    this.channel = supabase
      .channel('public:alerts')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'alerts' },
        (payload: Record<string, unknown>) => {
          const newAlert = payload.new as AlertEvent;

          // Update latest alert regardless of type
          this.latestAlert = newAlert;

          // If the newly inserted alert indicates an earthquake, set the global flag
          if (newAlert.is_quake) {
            this.isQuakeActive = true;
          }
        }
      )
      .subscribe();
  }

  acknowledge() {
    this.isQuakeActive = false;
  }

  destroy() {
    if (this.channel) {
      supabase.removeChannel(this.channel);
      this.channel = null;
    }
  }
}

// Export a singleton instance
export const alertStore = new AlertStore();
