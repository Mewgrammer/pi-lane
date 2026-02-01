<template>
  <q-item clickable v-ripple :to="to" active-class="bg-primary text-white" class="nav-item">
    <q-item-section avatar>
      <q-icon :name="icon" />
    </q-item-section>
    <q-item-section>
      <q-item-label>{{ label }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
defineProps<{
  to: string;
  icon: string;
  label: string;
}>();
</script>

<style lang="scss" scoped>
.nav-item {
  border-radius: 8px;
  margin: 4px 8px;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}
</style>
