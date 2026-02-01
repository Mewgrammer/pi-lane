<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const connectionStatus = ref<'connected' | 'disconnected'>('disconnected');
const testingConnection = ref(false);

const settings = reactive({
  backendUrl: 'http://localhost:8000',
  autoReconnect: true,
  hardwareMode: 'simulation',
  activeTrack: null as number | null,
  numberOfLanes: 2,
  defaultRaceMode: 'race_laps',
  defaultLaps: 10,
  defaultTimeLimit: 5,
  fuelSimulation: false,
  simBaseLapTime: 5000,
  simLapTimeVariance: 500,
  darkMode: true,
  showLapTimes: true,
  showPositionEstimate: true,
  fullscreenRace: false,
});

const lanePowerLevels = ref([100, 100, 100, 100, 100, 100, 100, 100]);

const laneColors = [
  '#ff3b3b', // Red - Lane 1
  '#3b8bff', // Blue - Lane 2
  '#00ff88', // Green - Lane 3
  '#ffcc00', // Yellow - Lane 4
  '#ff8800', // Orange - Lane 5
  '#cc44ff', // Purple - Lane 6
  '#00cccc', // Cyan - Lane 7
  '#ff66b2', // Pink - Lane 8
];

const hardwareModeOptions = [
  { label: 'Simulation Mode', value: 'simulation' },
  { label: 'Raspberry Pi Hardware', value: 'raspberry_pi' },
];

const raceModeOptions = [
  { label: 'Practice (Free Run)', value: 'practice' },
  { label: 'Time Trial (Best Lap)', value: 'time_trial' },
  { label: 'Race (Fixed Laps)', value: 'race_laps' },
  { label: 'Race (Time Limit)', value: 'race_time' },
];

const availableTracks = ref([
  { label: 'Default Track', value: 1 },
  { label: 'Figure 8', value: 2 },
]);

function getSliderColor(lane: number): string {
  const colors = ['red', 'blue', 'green', 'amber', 'orange', 'purple', 'cyan', 'pink'];
  return colors[(lane - 1) % colors.length] ?? 'primary';
}

async function testConnection() {
  testingConnection.value = true;
  try {
    const response = await fetch(`${settings.backendUrl}/api/health`);
    if (response.ok) {
      connectionStatus.value = 'connected';
      $q.notify({
        type: 'positive',
        message: 'Connected to backend successfully!',
        icon: 'check_circle',
      });
    } else {
      throw new Error('Connection failed');
    }
  } catch (err) {
    connectionStatus.value = 'disconnected';
    console.error(err);
    $q.notify({
      type: 'negative',
      message: 'Failed to connect to backend',
      icon: 'error',
    });
  } finally {
    testingConnection.value = false;
  }
}

function toggleDarkMode(value: boolean) {
  $q.dark.set(value);
}

function resetSettings() {
  $q.dialog({
    title: 'Reset Settings',
    message: 'Are you sure you want to reset all settings to defaults?',
    cancel: true,
    persistent: true,
  }).onOk(() => {
    Object.assign(settings, {
      backendUrl: 'http://localhost:8000',
      autoReconnect: true,
      hardwareMode: 'simulation',
      activeTrack: null,
      numberOfLanes: 2,
      defaultRaceMode: 'race_laps',
      defaultLaps: 10,
      defaultTimeLimit: 5,
      fuelSimulation: false,
      simBaseLapTime: 5000,
      simLapTimeVariance: 500,
      darkMode: true,
      showLapTimes: true,
      showPositionEstimate: true,
      fullscreenRace: false,
    });
    lanePowerLevels.value = [100, 100, 100, 100, 100, 100, 100, 100];
    $q.notify({
      type: 'info',
      message: 'Settings reset to defaults',
      icon: 'restore',
    });
  });
}

function saveSettings() {
  // TODO: Save to backend/localStorage
  localStorage.setItem('pilane-settings', JSON.stringify(settings));
  localStorage.setItem('pilane-power-levels', JSON.stringify(lanePowerLevels.value));
  $q.notify({
    type: 'positive',
    message: 'Settings saved!',
    icon: 'save',
  });
}

// Load settings on mount
function loadSettings() {
  const saved = localStorage.getItem('pilane-settings');
  if (saved) {
    Object.assign(settings, JSON.parse(saved));
  }
  const savedPower = localStorage.getItem('pilane-power-levels');
  if (savedPower) {
    lanePowerLevels.value = JSON.parse(savedPower);
  }
  $q.dark.set(settings.darkMode);
}

loadSettings();
</script>

<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">
      <q-icon name="settings" class="q-mr-sm" />
      Settings
    </div>

    <div class="row q-col-gutter-md">
      <!-- Backend Connection -->
      <div class="col-12 col-md-6">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="cloud" class="q-mr-sm" />
              Backend Connection
            </div>

            <q-input v-model="settings.backendUrl" label="Backend URL" filled dark class="q-mb-md">
              <template v-slot:append>
                <q-btn
                  flat
                  round
                  icon="refresh"
                  @click="testConnection"
                  :loading="testingConnection"
                />
              </template>
            </q-input>

            <div class="row items-center q-mb-md">
              <q-icon
                :name="connectionStatus === 'connected' ? 'check_circle' : 'error'"
                :color="connectionStatus === 'connected' ? 'positive' : 'negative'"
                size="sm"
                class="q-mr-sm"
              />
              <span :class="connectionStatus === 'connected' ? 'text-positive' : 'text-negative'">
                {{ connectionStatus === 'connected' ? 'Connected' : 'Disconnected' }}
              </span>
            </div>

            <q-toggle v-model="settings.autoReconnect" label="Auto-reconnect on disconnect" dark />
          </q-card-section>
        </q-card>
      </div>

      <!-- Hardware Mode -->
      <div class="col-12 col-md-6">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="memory" class="q-mr-sm" />
              Hardware Mode
            </div>

            <q-option-group
              v-model="settings.hardwareMode"
              :options="hardwareModeOptions"
              color="primary"
              dark
              class="q-mb-md"
            />

            <q-banner
              v-if="settings.hardwareMode === 'simulation'"
              class="bg-info text-white q-mb-md"
              rounded
            >
              <template v-slot:avatar>
                <q-icon name="info" />
              </template>
              Simulation mode generates fake lap times for testing
            </q-banner>
          </q-card-section>
        </q-card>
      </div>

      <!-- Track Configuration -->
      <div class="col-12 col-md-6">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="edit_road" class="q-mr-sm" />
              Track Configuration
            </div>

            <q-select
              v-model="settings.activeTrack"
              :options="availableTracks"
              label="Active Track"
              filled
              dark
              emit-value
              map-options
              class="q-mb-md"
            />

            <q-slider
              v-model="settings.numberOfLanes"
              :min="1"
              :max="8"
              :step="1"
              label
              label-always
              color="primary"
              class="q-mb-md q-px-sm"
            />
            <div class="text-caption text-grey-5 q-mb-md">
              Number of Lanes: {{ settings.numberOfLanes }}
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Race Settings -->
      <div class="col-12 col-md-6">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="flag" class="q-mr-sm" />
              Default Race Settings
            </div>

            <q-select
              v-model="settings.defaultRaceMode"
              :options="raceModeOptions"
              label="Default Race Mode"
              filled
              dark
              emit-value
              map-options
              class="q-mb-md"
            />

            <q-input
              v-model.number="settings.defaultLaps"
              type="number"
              label="Default Laps"
              filled
              dark
              :min="1"
              :max="100"
              class="q-mb-md"
            />

            <q-input
              v-model.number="settings.defaultTimeLimit"
              type="number"
              label="Default Time Limit (minutes)"
              filled
              dark
              :min="1"
              :max="60"
              class="q-mb-md"
            />

            <q-toggle v-model="settings.fuelSimulation" label="Enable Fuel Simulation" dark />
          </q-card-section>
        </q-card>
      </div>

      <!-- Lane Power Levels -->
      <div class="col-12">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="electric_bolt" class="q-mr-sm" />
              Lane Power Levels
            </div>

            <div class="text-caption text-grey-5 q-mb-md">
              Adjust maximum power for each lane (useful for balancing cars with different speeds)
            </div>

            <div class="row q-col-gutter-md">
              <div
                v-for="lane in settings.numberOfLanes"
                :key="lane"
                class="col-12 col-sm-6 col-md-4"
              >
                <q-card class="lane-card" :style="{ borderColor: laneColors[lane - 1] }">
                  <q-card-section>
                    <div class="row items-center justify-between q-mb-sm">
                      <div class="text-subtitle1">
                        <q-icon
                          name="directions_car"
                          :style="{ color: laneColors[lane - 1] }"
                          class="q-mr-sm"
                        />
                        Lane {{ lane }}
                      </div>
                      <div
                        class="text-h6 text-weight-bold"
                        :style="{ color: laneColors[lane - 1] }"
                      >
                        {{ lanePowerLevels[lane - 1] }}%
                      </div>
                    </div>

                    <q-slider
                      v-model="lanePowerLevels[lane - 1]"
                      :min="0"
                      :max="100"
                      :step="5"
                      :color="getSliderColor(lane)"
                      track-size="10px"
                      thumb-size="24px"
                      class="power-slider"
                    />

                    <div class="row q-mt-sm q-gutter-sm">
                      <q-btn
                        flat
                        dense
                        label="0%"
                        size="sm"
                        @click="lanePowerLevels[lane - 1] = 0"
                      />
                      <q-btn
                        flat
                        dense
                        label="50%"
                        size="sm"
                        @click="lanePowerLevels[lane - 1] = 50"
                      />
                      <q-btn
                        flat
                        dense
                        label="100%"
                        size="sm"
                        @click="lanePowerLevels[lane - 1] = 100"
                      />
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Simulation Settings -->
      <div class="col-12 col-md-6" v-if="settings.hardwareMode === 'simulation'">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="science" class="q-mr-sm" />
              Simulation Settings
            </div>

            <q-input
              v-model.number="settings.simBaseLapTime"
              type="number"
              label="Base Lap Time (ms)"
              filled
              dark
              :min="1000"
              :max="30000"
              class="q-mb-md"
            />

            <q-input
              v-model.number="settings.simLapTimeVariance"
              type="number"
              label="Lap Time Variance (ms)"
              filled
              dark
              :min="0"
              :max="5000"
              class="q-mb-md"
            />

            <div class="text-caption text-grey-5">
              Simulated lap times will be: {{ settings.simBaseLapTime }}ms ±
              {{ settings.simLapTimeVariance }}ms
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Display Settings -->
      <div class="col-12 col-md-6">
        <q-card class="bg-grey-9">
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="display_settings" class="q-mr-sm" />
              Display Settings
            </div>

            <q-toggle
              v-model="settings.darkMode"
              label="Dark Mode"
              dark
              class="q-mb-md"
              @update:model-value="toggleDarkMode"
            />

            <q-toggle
              v-model="settings.showLapTimes"
              label="Show Lap Times During Race"
              dark
              class="q-mb-md"
            />

            <q-toggle
              v-model="settings.showPositionEstimate"
              label="Show Position Estimate"
              dark
              class="q-mb-md"
            />

            <q-toggle v-model="settings.fullscreenRace" label="Fullscreen Race Mode" dark />
          </q-card-section>
        </q-card>
      </div>

      <!-- Actions -->
      <div class="col-12">
        <div class="row q-gutter-md justify-end">
          <q-btn
            outline
            color="negative"
            icon="restore"
            label="Reset to Defaults"
            @click="resetSettings"
          />
          <q-btn push color="primary" icon="save" label="Save Settings" @click="saveSettings" />
        </div>
      </div>
    </div>
  </q-page>
</template>

<style lang="scss" scoped>
.lane-card {
  background: rgba(30, 30, 40, 0.8);
  border-left: 4px solid;
}

.power-slider {
  :deep(.q-slider__track) {
    opacity: 0.3;
  }
}
</style>
