import { pgTable, serial, text, real, boolean, timestamp } from 'drizzle-orm/pg-core';

// ── Alerts (every classified reading from the RPi LSTM model) ────────
// Every reading goes through the classifier, so every data point has a
// severity. This table serves as both live telemetry AND alert history.
export const alerts = pgTable('alerts', {
  id: serial('id').primaryKey(),
  device_id: text('device_id').notNull().default('wida-01'),
  frequency_hz: real('frequency_hz').notNull(),
  raw_x: real('raw_x').notNull(),
  raw_y: real('raw_y').notNull(),
  raw_z: real('raw_z').notNull(),
  severity: text('severity').notNull().default('normal'), // normal | minor | moderate | dangerous
  confidence_score: real('confidence_score').notNull(),
  fft_latency_ms: real('fft_latency_ms'),
  sensor_temperature_c: real('sensor_temperature_c'),
  recorded_at: timestamp('recorded_at').notNull().defaultNow()
});

// ── System Settings (admin config) ───────────────────────────────────
export const system_settings = pgTable('system_settings', {
  id: serial('id').primaryKey(),
  sensor_threshold: real('sensor_threshold').notNull().default(1.5),
  telegram_alerts_enabled: boolean('telegram_alerts_enabled').notNull().default(false)
});

export * from './auth.schema';
