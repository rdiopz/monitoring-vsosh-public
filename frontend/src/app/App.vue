<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
#app {
  min-height: 100vh;
  font-family: var(--font-family);
  background: var(--bg);
  color: var(--text-primary);
  transition:
    background-color 0.5s,
    color 0.5s;
}
</style>
