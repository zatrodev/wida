import { createClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/public';

if (!env.PUBLIC_SUPABASE_URL || !env.PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY) {
  throw new Error('Supabase public environment variables are not set.');
}

// Initialize the Supabase client purely for client-side functionality (e.g. real-time WebSockets)
export const supabase = createClient(
  env.PUBLIC_SUPABASE_URL,
  env.PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY
);
