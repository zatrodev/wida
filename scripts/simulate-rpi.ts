import postgres from 'postgres';
import { drizzle } from 'drizzle-orm/postgres-js';
import { alerts } from '../src/lib/server/db/schema';

// Run with: bun scripts/simulate-rpi.ts
// Bun automatically loads .env files

async function main() {
  const DATABASE_URL = process.env.DATABASE_URL;
  if (!DATABASE_URL) {
    console.error('❌ DATABASE_URL not set in .env or environment');
    process.exit(1);
  }

  const client = postgres(DATABASE_URL);
  const db = drizzle(client);

  console.log('🚀 Starting RPi simulation...');
  console.log('📡 Inserting a random reading every 5 seconds. Press Ctrl+C to stop.\n');

  setInterval(async () => {
    try {
      const isQuake = Math.random() > 0.2; // 5% chance of a minor quake for testing
      const severity = isQuake ? 'dangerous' : 'normal';

      const newReading = {
        device_id: 'wida-01',
        frequency_hz: 120 + (Math.random() * 10 - 5), // 115 - 125 Hz range
        raw_x: 20 + Math.random() * 50,
        raw_y: 20 + Math.random() * 50,
        raw_z: 20 + Math.random() * 50,
        severity: severity,
        confidence_score: 0.9 + Math.random() * 0.1,
        recorded_at: new Date()
      };

      await db.insert(alerts).values(newReading as any);

      const time = new Date().toLocaleTimeString();
      console.log(
        `[${time}] Sent reading: ${newReading.frequency_hz.toFixed(2)} Hz | Severity: ${severity}`
      );
    } catch (err) {
      console.error('❌ Failed to insert reading:', err);
    }
  }, 5000);
}

main().catch(console.error);
