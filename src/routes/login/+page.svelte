<script lang="ts">
  import { enhance } from '$app/forms';
  import { resolve } from '$app/paths';
  import type { ActionData } from './$types';
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Input } from '$lib/components/ui/input';
  import { Button } from '$lib/components/ui/button';
  import { Mail, Eye, EyeOff, House } from 'lucide-svelte';

  import adminLoginBg from '$lib/assets/admin-login.jpg?enhanced';

  let { form }: { form: ActionData } = $props();
  let showPassword = $state(false);
</script>

<div class="flex h-screen w-full overflow-y-hidden">
  <!-- Left Panel -->
  <div class="flex w-full flex-col p-8 lg:w-1/2 lg:px-16 xl:px-24 2xl:px-32">
    <!-- Logo -->
    <div class="absolute top-4 left-4 flex items-center gap-2 text-xl font-bold">
      <Button
        href={resolve('/')}
        variant="outline"
        size="icon-lg"
        class="flex  items-center justify-center rounded-lg"
      >
        <House class="h-5 w-5" />
      </Button>
    </div>

    <div class="my-auto flex w-full max-w-sm flex-col justify-center self-center">
      <h1 class="mb-2 font-mono text-3xl font-medium">Admin Login</h1>
      <p class="mb-8 text-sm text-muted-foreground">
        Enter your credentials to access the admin inteface.
      </p>

      <form method="post" action="?/signInEmail" use:enhance class="w-full space-y-6">
        <div class="space-y-4">
          <div class="relative">
            <Input
              type="email"
              name="email"
              placeholder="Enter your email"
              class="h-12 w-full bg-transparent pr-10 pl-6 text-foreground placeholder:text-muted-foreground "
            />
            <Mail class="absolute top-1/2 right-4 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          </div>
          <div class="relative">
            <Input
              type={showPassword ? 'text' : 'password'}
              name="password"
              placeholder="Enter your password"
              class="h-12 w-full bg-transparent pr-10 pl-6 text-foreground placeholder:text-muted-foreground "
            />
            <button
              type="button"
              class="absolute top-1/2 right-4 -translate-y-1/2 p-0.5 text-muted-foreground outline-none hover:text-foreground"
              onclick={() => (showPassword = !showPassword)}
            >
              {#if showPassword}
                <EyeOff class="h-5 w-5" />
              {:else}
                <Eye class="h-5 w-5" />
              {/if}
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center space-x-2">
            <Checkbox id="remember" name="remember" />
            <label
              for="remember"
              class="text-sm leading-none font-medium text-muted-foreground peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Remember me
            </label>
          </div>
        </div>

        <Button type="submit" class="h-12 w-full font-mono transition-colors duration-300">
          Login
        </Button>

        {#if form?.message}
          <p class="text-center text-sm font-medium text-destructive">{form.message}</p>
        {/if}
      </form>
    </div>
  </div>

  <!-- Right Panel -->
  <div class="relative hidden p-2 lg:block lg:w-1/2">
    <div class="group relative h-full w-full overflow-hidden rounded-4xl bg-neutral shadow-inner">
      <enhanced:img
        src={adminLoginBg}
        decoding="async"
        alt="Abstract Fluid Space"
        class="absolute inset-0 h-full w-full mix-blend-difference grayscale transition-transform duration-[15s] ease-in-out group-hover:scale-105"
      />
      <!-- Inner gradient glow for aesthetic -->
      <div
        class="absolute inset-0 bg-linear-to-tr from-neutral-foreground/20 via-transparent to-neutral/20 mix-blend-overlay"
      ></div>
    </div>
  </div>
</div>
