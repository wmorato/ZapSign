// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\company\company.routes.ts
import { Routes } from '@angular/router';
import { CompanyListComponent } from './components/company-list/company-list.component';
import { CompanyFormComponent } from './components/company-form/company-form.component';

export const COMPANY_ROUTES: Routes = [
    { path: '', component: CompanyListComponent },
    { path: 'new', component: CompanyFormComponent },
    { path: ':id/edit', component: CompanyFormComponent }
];