// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\app.routes.ts
import { Routes, CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

import { LoginComponent } from './features/auth/login/login.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { AuthService } from './core/auth/auth.service';
import { DocumentReportsComponent } from './features/document/components/document-reports/document-reports.component'; // <--- ADICIONADO

// AuthGuard para proteger rotas (função standalone)
const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  } else {
    router.navigate(['/login']);
    return false;
  }
};

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  {
    path: 'companies',
    loadChildren: () => import('./features/company/company.routes').then(m => m.COMPANY_ROUTES),
    canActivate: [authGuard]
  },
  {
    path: 'documents', // Nova rota para documentos
    loadChildren: () => import('./features/document/document.routes').then(m => m.DOCUMENT_ROUTES),
    canActivate: [authGuard]
  },
  {
    path: 'reports', // <--- NOVA ROTA DE RELATÓRIOS
    component: DocumentReportsComponent,
    canActivate: [authGuard]
  },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: '/dashboard' }
];