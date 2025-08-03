import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./chat/chat').then(m => m.Chat),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard').then(m => m.Dashboard),
  },
  {
    path: 'markets',
    loadComponent: () => import('./markets/markets').then(m => m.Markets),
  },
  {
    path: '**',
    redirectTo: ''
  }
];
