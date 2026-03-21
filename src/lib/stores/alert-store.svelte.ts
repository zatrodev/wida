import { supabase } from '$lib/supabase';

export type Severity = 'normal' | 'minor' | 'moderate' | 'dangerous';

export type AlertEvent = {
  id: number;
  device_id: string;
  frequency_hz: number;
  raw_x: number;
  raw_y: number;
  raw_z: number;
  severity: Severity;
  confidence_score: number;
  fft_latency_ms?: number;
  sensor_temperature_c?: number;
  recorded_at: string;
};

/** How many data points to keep in the rolling chart buffer */
const CHART_BUFFER_SIZE = 20;

export class AlertStore {
  isQuakeActive = $state(false);
  currentSeverity = $state<Severity>('normal');
  latestAlert = $state<AlertEvent | null>(null);

  /** Rolling buffer of recent alerts for the live waveform chart */
  recentAlerts = $state<AlertEvent[]>([]);

  /** Full alert history (up to 50 most recent) */
  alertHistory = $state<AlertEvent[]>([]);

  private channel: ReturnType<typeof supabase.channel> | null = null;

  async init() {
    if (this.channel) return;

    // 1. Fetch initial history from Supabase
    const { data, error } = await supabase
      .from('alerts')
      .select('*')
      .order('recorded_at', { ascending: false })
      .limit(50);

    if (error) {
      console.error('Error fetching alert history:', error);
    } else if (data) {
      this.alertHistory = data as AlertEvent[];
      // Populate recentAlerts for the chart from the fetched history (oldest to newest)
      this.recentAlerts = [...data].reverse().slice(-CHART_BUFFER_SIZE);

      // Set the latest alert as well
      if (data.length > 0) {
        this.latestAlert = data[0] as AlertEvent;
      }
    }

    // 2. Subscribe to real-time inserts
    this.channel = supabase
      .channel('public:alerts')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'alerts' },
        (payload: Record<string, unknown>) => {
          const newAlert = payload.new as AlertEvent;

          // Update latest
          this.latestAlert = newAlert;

          // Push to rolling chart buffer (keep last N points)
          this.recentAlerts = [...this.recentAlerts, newAlert].slice(-CHART_BUFFER_SIZE);

          // Push to history
          this.alertHistory = [newAlert, ...this.alertHistory].slice(0, 50);

          // Trigger emergency overlay for non-normal events
          if (newAlert.severity !== 'normal') {
            this.isQuakeActive = true;
            this.currentSeverity = newAlert.severity;
          }
        }
      )
      .subscribe();
  }

  acknowledge() {
    this.isQuakeActive = false;
    this.currentSeverity = 'normal';
  }

  destroy() {
    if (this.channel) {
      supabase.removeChannel(this.channel);
      this.channel = null;
    }
  }
}

export const alertStore = new AlertStore();
