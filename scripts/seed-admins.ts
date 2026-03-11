import postgres from 'postgres';
import { drizzle } from 'drizzle-orm/postgres-js';
import { eq } from 'drizzle-orm';
import { user, account } from '../src/lib/server/db/auth.schema';
import { hashPassword } from 'better-auth/crypto';
import { randomUUID } from 'crypto';

// ─── Predefined Admin Users ───────────────────────────
const ADMIN_USERS = [
    {
        name: 'Admin',
        email: 'admin@wida.com',
        password: 'admin123'
    }
];

// ─── Main ─────────────────────────────────────────────
async function main() {
    const DATABASE_URL = process.env.DATABASE_URL;
    if (!DATABASE_URL) {
        console.error('❌ DATABASE_URL environment variable is not set.');
        process.exit(1);
    }

    const client = postgres(DATABASE_URL);
    const db = drizzle(client);

    console.log('🌱 Seeding admin users...\n');

    for (const admin of ADMIN_USERS) {
        // Check if user already exists
        const existing = await db.select().from(user).where(eq(user.email, admin.email)).limit(1);

        if (existing.length > 0) {
            console.log(`  ⏭️  ${admin.email} already exists, skipping.`);
            continue;
        }

        const userId = randomUUID();
        const hashedPassword = await hashPassword(admin.password);
        const now = new Date();

        // Insert user
        await db.insert(user).values({
            id: userId,
            name: admin.name,
            email: admin.email,
            emailVerified: true,
            role: 'admin',
            createdAt: now,
            updatedAt: now
        });

        // Insert credential account (required by better-auth for email/password login)
        await db.insert(account).values({
            id: randomUUID(),
            accountId: userId,
            providerId: 'credential',
            userId: userId,
            password: hashedPassword,
            createdAt: now,
            updatedAt: now
        });

        console.log(`  ✅ Seeded: ${admin.email}`);
    }

    console.log('\n🎉 Seed complete.');

    await client.end();
    process.exit(0);
}

main().catch((err) => {
    console.error('❌ Seed failed:', err);
    process.exit(1);
});
