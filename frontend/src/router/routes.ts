import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('pages/HomePage.vue'),
        meta: { title: 'Home', icon: 'home' },
      },
      {
        path: 'race',
        name: 'race',
        component: () => import('pages/RacePage.vue'),
        meta: { title: 'Race', icon: 'flag' },
      },
      {
        path: 'track-editor',
        name: 'track-editor',
        component: () => import('pages/TrackEditorPage.vue'),
        meta: { title: 'Track Editor', icon: 'edit_road' },
      },
      {
        path: 'leaderboard',
        name: 'leaderboard',
        component: () => import('pages/LeaderboardPage.vue'),
        meta: { title: 'Leaderboard', icon: 'leaderboard' },
      },
      {
        path: 'cars',
        name: 'cars',
        component: () => import('pages/CarsPage.vue'),
        meta: { title: 'Cars', icon: 'directions_car' },
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('pages/UsersPage.vue'),
        meta: { title: 'Users', icon: 'people' },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('pages/SettingsPage.vue'),
        meta: { title: 'Settings', icon: 'settings' },
      },
    ],
  },

  // Always leave this as last one
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
