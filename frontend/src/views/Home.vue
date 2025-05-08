<template>
  <div class="home-page">
    <section class="hero">
      <h1>Welcome to FilmTrack</h1>
      <p>
        Keep track of every movie you've watched and those you want to watch next.
        Rate films, leave a short review explaining your rating, and never lose
        sight of your favorites or upcoming must-sees.
      </p>
    </section>

    <section class="features">
      <h2>Features</h2>
      <ul>
        <li><strong>Add new movies</strong> with your own comments.</li>
        <li><strong>Rate and review</strong> why you loved (or hated) a film.</li>
        <li><strong>Watchlist</strong> to mark what you have watched, what you plan to watch, and when.</li>
        <li><strong>Export reminders</strong> with calendar invites for scheduled viewings.</li>
      </ul>
      <h3>Rules</h3>
      <p>
        We are committed to creating a safe and inclusive environment for all users.
        Report any innappropriate content to any admin.
      </p>
    </section>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-page {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
  line-height: 1.6;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.1rem;
  color: #555;
  max-width: 600px;
  margin: 0.5rem auto 1.5rem;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.features {
  background: #f9f9f9;
  padding: 2rem;
  border-radius: 8px;
}

.features h2 {
  margin-bottom: 1rem;
  font-size: 1.8rem;
}

.features ul {
  list-style: disc inside;
  padding-left: 1rem;
}

.features li {
  margin-bottom: 0.75rem;
}
</style>
