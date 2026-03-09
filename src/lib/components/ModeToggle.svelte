<script lang="ts">
  import { toggleMode } from 'mode-watcher';

  import Moon from './icons/Moon.svelte';
  import Sun from './icons/Sun.svelte';

  import { Button, type ButtonVariant } from '$lib/components/ui/button/index.js';

  type Props = {
    variant?: ButtonVariant;
    class: string;
  };

  const { variant = 'outline', class: className }: Props = $props();
</script>

<Button onclick={toggleMode} {variant} size="icon-sm" class="rounded-full {className}">
  <Moon class="absolute size-4 scale-0 rotate-90 transition-all! dark:scale-100 dark:rotate-0" />
  <Sun class="absolute size-4 scale-100 rotate-0 transition-all! dark:scale-0 dark:-rotate-90" />
  <span class="sr-only">Toggle theme</span>
</Button>
