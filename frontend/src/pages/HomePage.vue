<script setup lang="ts">
import { ref } from 'vue';

const stats = ref({
  totalRaces: 0,
  totalLaps: 0,
  bestLapTime: 0,
  activeCars: 0,
});

function formatTime(ms: number): string {
  if (ms === 0) return '--:--.---';
  const seconds = Math.floor(ms / 1000);
  const millis = ms % 1000;
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}.${millis.toString().padStart(3, '0')}`;
}
</script>

<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">
      <q-icon name="home" class="q-mr-sm" />
      Welcome to Pi-Lane
    </div>

    <div class="row q-col-gutter-md">
      <!-- Quick Stats -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-grey-5">Total Races</div>
            <div class="text-h4 text-white">{{ stats.totalRaces }}</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-grey-5">Total Laps</div>
            <div class="text-h4 text-white">{{ stats.totalLaps }}</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-grey-5">Best Lap Time</div>
            <div class="text-h4 text-positive">{{ formatTime(stats.bestLapTime) }}</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-grey-5">Active Cars</div>
            <div class="text-h4 text-white">{{ stats.activeCars }}</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Quick Actions -->
      <div class="col-12">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">Quick Actions</div>
            <div class="row q-gutter-md">
              <q-btn push color="positive" icon="flag" label="Start Race" size="lg" to="/race" />
              <q-btn
                push
                color="primary"
                icon="edit_road"
                label="Edit Track"
                size="lg"
                to="/track-editor"
              />
              <q-btn
                push
                color="secondary"
                icon="settings"
                label="Settings"
                size="lg"
                to="/settings"
              />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>
