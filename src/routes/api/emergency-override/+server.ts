import type { RequestHandler } from './$types';
import { db } from '$lib/server/db';
import { alerts } from '$lib/server/db/schema';
import { json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ locals }) => {
  // Strict RBAC: Only allow admins to trigger manual alerts
  if (!locals.user || locals.user.role !== 'admin') {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    // Insert a mock earthquake trigger into the DB.
    // Supabase real-time will catch this INSERT and broadcast it to all connected clients!
    await db.insert(alerts).values({
      device_id: 'wida-01',
      frequency_hz: 15.0 + Math.random() * 10,
      raw_x: 100 + Math.random() * 150,
      raw_y: 100 + Math.random() * 150,
      raw_z: 100 + Math.random() * 150,
      severity: 'dangerous',
      confidence_score: 0.92 + Math.random() * 0.08
    });

    return json({ success: true, message: 'Global emergency alert transmitted.' });
  } catch (e) {
    return json({ error: String(e) }, { status: 500 });
  }
};
