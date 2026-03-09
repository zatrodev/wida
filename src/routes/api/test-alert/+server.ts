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
      x_axis: Math.random() * 5,
      y_axis: Math.random() * 5,
      z_axis: 2.5 + Math.random() * 5, // high G-force to simulate quake
      is_quake: true,
      confidence_score: 0.98
    });

    return json({ success: true, message: 'Global emergency alert transmitted.' });
  } catch (e) {
    return json({ error: String(e) }, { status: 500 });
  }
};
