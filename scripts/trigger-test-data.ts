import postgres from 'postgres';
import { drizzle } from 'drizzle-orm/postgres-js';
import { alerts } from '../src/lib/server/db/schema';

// Run with: DATABASE_URL=... bun scripts/trigger-test-data.ts

async function main() {
    const DATABASE_URL = process.env.DATABASE_URL;
    if (!DATABASE_URL) {
        console.error('DATABASE_URL not set');
        process.exit(1);
    }
    const client = postgres(DATABASE_URL);
    const db = drizzle(client);

    console.log('Inserting test alerts...');
    for (let i = 0; i < 60; i++) {
        await db.insert(alerts).values({
            device_id: 'wida-01',
            frequency_hz: 120 + Math.random() * 5,
            raw_x: 20 + Math.random() * 60,
            raw_y: 20 + Math.random() * 60,
            raw_z: 20 + Math.random() * 60,
            severity: i === 0 ? 'moderate' : (i % 15 === 0 ? 'minor' : 'normal'),
            confidence_score: 0.95,
            recorded_at: new Date(Date.now() - (60 - i) * 1000)
        });
    }
    console.log('Done.');
    process.exit(0);
}

main().catch(console.error);
