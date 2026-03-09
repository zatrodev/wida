import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  // RBAC: Check if the user is authenticated and is an admin
  if (!locals.user || locals.user.role !== 'admin') {
    // If not authorized, redirect them to the general dashboard
    throw redirect(302, '/dashboard');
  }

  return {};
};
