<script>
  import { resolve } from '$app/paths';
  import ModeToggle from './ModeToggle.svelte';
</script>

<header
  class="sticky top-0 mx-auto max-w-360 bg-background/10 pt-4 tracking-tight backdrop-blur-md"
>
  <div class="mx-16 flex place-items-center border-b py-6">
    <img src="" alt="" />

    <nav>
      <ul class="flex gap-4">
        <li><a href={resolve('/dashboard')}>Dashboard</a></li>
        <li><a href="">Settings</a></li>
      </ul>
    </nav>

    <ModeToggle class="ml-auto" />
  </div>
</header>
