<script setup lang="ts">
import TrackEditor from '../components/track/TrackEditor.vue';
</script>

<template>
  <q-page class="track-editor-page">
    <TrackEditor />
  </q-page>
</template>

<style lang="scss" scoped>
.track-editor-page {
  padding: 0;
  height: calc(100vh - 50px);
}
</style>
