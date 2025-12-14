// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\document.routes.ts
import { Routes } from '@angular/router';
import { DocumentListComponent } from './components/document-list/document-list.component';
import { DocumentDetailComponent } from './components/document-detail/document-detail.component';
import { DocumentFormComponent } from './components/document-form/document-form.component'; // Importe o DocumentFormComponent
import { DocumentRiskManagementComponent } from './components/document-risk-management/document-risk-management.component'; // <--- ADICIONADO

export const DOCUMENT_ROUTES: Routes = [
    { path: '', component: DocumentListComponent },
    { path: 'new', component: DocumentFormComponent },
    { path: 'risk', component: DocumentRiskManagementComponent }, // <--- NOVA ROTA
    { path: ':id', component: DocumentDetailComponent },
    { path: ':id/edit', component: DocumentFormComponent }
];