import { pgTable, serial, integer, text, real, boolean, timestamp } from 'drizzle-orm/pg-core';

export const task = pgTable('task', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  priority: integer('priority').notNull().default(1)
});

export const alerts = pgTable('alerts', {
  id: serial('id').primaryKey(),
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  x_axis: real('x_axis').notNull(),
  y_axis: real('y_axis').notNull(),
  z_axis: real('z_axis').notNull(),
  is_quake: boolean('is_quake').notNull(),
  confidence_score: real('confidence_score').notNull()
});

export const system_settings = pgTable('system_settings', {
  id: serial('id').primaryKey(),
  sensor_threshold: real('sensor_threshold').notNull().default(1.5),
  telegram_alerts_enabled: boolean('telegram_alerts_enabled').notNull().default(false)
});

export * from './auth.schema';
