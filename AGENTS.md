### SvelteKit Earthquake Warning Dashboard: Build Outline (v3 with RBAC)

**Project Context for AI:**
Build a real-time web dashboard using SvelteKit. The app receives live accelerometer data and earthquake classifications from a hardware edge device (Raspberry Pi) via a Supabase PostgreSQL database. **Database schemas and server-side queries are managed with Drizzle ORM.** Authentication and **Role-Based Access Control (RBAC)** are handled by `better-auth` using the Drizzle adapter, and real-time frontend updates are handled by `@supabase/supabase-js`.

#### 1. Initialization & Environment

- **Scaffold SvelteKit:** Initialize a barebones SvelteKit project (TypeScript enabled).
- **Dependencies:** Install Tailwind CSS, `drizzle-orm`, `drizzle-kit`, `postgres`, `better-auth`, and `@supabase/supabase-js`.
- **Environment Variables:** Define `.env` requirements:
- `DATABASE_URL` (Supabase connection string for Drizzle and `better-auth`).
- `PUBLIC_SUPABASE_URL` (For the client-side realtime subscription).
- `PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` (For the client-side realtime subscription).
- `BETTER_AUTH_SECRET` (Cryptographic secret for sessions).

#### 2. Database Schema & Authentication (`drizzle-orm` + `better-auth`)

- **Schema Definition (`src/lib/server/db/schema.ts`):** \* Define the required `better-auth` tables. **Crucially, add a `role` text column (default: 'user') to the `user` table.**
- Define the `alerts` table: `id`, `timestamp`, `x_axis`, `y_axis`, `z_axis`, `is_quake` (boolean), and `confidence_score` (real/float).
- Define a `system_settings` table (for the admin config): `id`, `sensor_threshold` (real), `telegram_alerts_enabled` (boolean).

- **Database Adapter:** Configure `better-auth` in `src/lib/auth.ts` to use the Drizzle adapter.
- **Server Hooks:** Implement `hooks.server.ts` to validate sessions on every request and pass the user's `role` to the frontend via `event.locals`.

#### 3. Supabase Real-time Client Integration

- **Client Initialization:** Create `src/lib/supabase.ts` and initialize the Supabase client using the public URL and Anon Key. _(Strictly for client-side WebSockets)._
- **Real-time Subscription:** Write a utility in `onMount` that subscribes to the `alerts` table in Supabase to listen for `INSERT` events and update the UI instantly.

#### 4. The Dashboard UI (Role-Based Views)

- **Routing Split:** Create a protected layout that checks the user's role and renders either the Admin View or the General User View.
- **General User View (`/dashboard`):**
- **Simplified Live Sensor Graph:** A clean, easy-to-read chart of recent vibrations.
- **Event Confidence Panel (Replacing "Forecasts"):** A UI card displaying the ML model's probability score of the current vibration being an actual earthquake versus noise.
- **Safety Instructions:** A static section showing emergency protocols (e.g., "Drop, Cover, and Hold on," evacuation routes).

- **Administrator Portal (`/admin`):**
- **System Configuration:** A form interacting with the `system_settings` table to adjust sensitivity thresholds or toggle external Telegram alerts on/off.
- **Data Analytics:** Deeper historical data views, including event frequency charts and a button to export the `alerts` table to a CSV file (crucial for their thesis data gathering).
- **Manual Alert Trigger:** A high-visibility "Test System" or "Manual Override" button that instantly pushes an `is_quake = true` payload to the database to test the sirens and UI warnings.

#### 5. The Emergency Alert System (Critical Feature)

- **Global State:** Create a Svelte derived store watching incoming real-time data for `is_quake === true`.
- **Visual Warning Component:** Build a full-screen, highly visible modal that overrides the UI for _all_ active users when an earthquake is detected.
- _Styling:_ Deep red background, large bold text ("EARTHQUAKE DETECTED"), CSS pulsing animation.
- _Audio:_ Trigger an HTML5 Audio browser beep.
- _Dismissal:_ Add an "Acknowledge" button.

#### 6. Deployment Prep

- **Adapter:** Install `@sveltejs/adapter-vercel` (or Netlify/Node adapter) and configure `svelte.config.js`.

### REMINDERS!!

- This project is using svelte-shadcn. Please refer to @shadcn-svelte.md for more information.
- Employ clean, compact UI for this project. I want it to have a minimalist vibe. Also, feel free to use any modern design techniques, such as bento grids, glassmorphism, etc IF appropriate.
