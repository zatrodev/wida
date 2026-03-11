import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import type { PageServerLoad } from './$types';
import { auth } from '$lib/server/auth';
import { APIError } from 'better-auth/api';

export const load: PageServerLoad = async (event) => {
  if (event.locals.user) {
    return redirect(302, '/admin');
  }
  return {};
};

export const actions: Actions = {
  signInEmail: async (event) => {
    const formData = await event.request.formData();
    const email = formData.get('email')?.toString() ?? '';
    const password = formData.get('password')?.toString() ?? '';

    try {
      const response = await auth.api.signInEmail({
        body: {
          email,
          password
        }
      });

      // Only admins are allowed to log in
      if (response.user.role !== 'admin') {
        return fail(403, { message: 'Access denied. Only administrators can log in.' });
      }
    } catch (error) {
      if (error instanceof APIError) {
        return fail(400, { message: error.message || 'Signin failed' });
      }
      return fail(500, { message: 'Unexpected error' });
    }

    return redirect(302, '/admin');
  }
};
