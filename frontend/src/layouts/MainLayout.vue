<script setup lang="ts">
import { ref } from 'vue';
import NavItem from 'components/NavItem.vue';

interface NavLink {
  name: string;
  to: string;
  icon: string;
  label: string;
}

const navLinks: NavLink[] = [
  { name: 'home', to: '/', icon: 'home', label: 'Home' },
  { name: 'race', to: '/race', icon: 'flag', label: 'Race' },
  { name: 'track-editor', to: '/track-editor', icon: 'edit_road', label: 'Track Editor' },
  { name: 'leaderboard', to: '/leaderboard', icon: 'leaderboard', label: 'Leaderboard' },
  { name: 'cars', to: '/cars', icon: 'directions_car', label: 'Cars' },
  { name: 'users', to: '/users', icon: 'people', label: 'Users' },
  { name: 'settings', to: '/settings', icon: 'settings', label: 'Settings' },
];

const leftDrawerOpen = ref(false);
const connectionStatus = ref<'connected' | 'disconnected'>('disconnected');

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function startQuickRace() {
  // TODO: Implement quick race start
  console.log('Starting quick race...');
}
</script>

<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-dark">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title class="text-weight-bold">
          <q-icon name="sports_motorsports" class="q-mr-sm" />
          Pi-Lane
        </q-toolbar-title>

        <q-btn
          flat
          round
          :icon="connectionStatus === 'connected' ? 'wifi' : 'wifi_off'"
          :color="connectionStatus === 'connected' ? 'positive' : 'negative'"
        >
          <q-tooltip>{{
            connectionStatus === 'connected' ? 'Connected' : 'Disconnected'
          }}</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered class="bg-grey-10">
      <q-list>
        <q-item-label header class="text-grey-5"> Navigation </q-item-label>

        <NavItem
          v-for="link in navLinks"
          :key="link.name"
          :to="link.to"
          :icon="link.icon"
          :label="link.label"
        />

        <q-separator class="q-my-md" dark />

        <q-item-label header class="text-grey-5"> Quick Actions </q-item-label>

        <q-item clickable v-ripple @click="startQuickRace">
          <q-item-section avatar>
            <q-icon name="play_arrow" color="positive" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Quick Race</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>

      <q-space />

      <div class="q-pa-md text-grey-6 text-caption">Pi-Lane v0.1.0 | Simulation Mode</div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<style lang="scss" scoped>
.q-toolbar-title {
  font-size: 1.4rem;
}
</style>
