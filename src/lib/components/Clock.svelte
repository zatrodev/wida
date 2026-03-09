<script>
  let now = $state(new Date());

  $effect(() => {
    const interval = setInterval(() => (now = new Date()), 1000);
    return () => clearInterval(interval);
  });

  let formattedTime = $derived(
    now.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  );
</script>

{formattedTime}
