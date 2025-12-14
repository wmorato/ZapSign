// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\company\services\company.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Company } from '../../../core/models/company.model';
import { ApiService } from '../../../core/services/api.service';

@Injectable({
  providedIn: 'root'
})
export class CompanyService {
  private companyPath = '/api/company/';

  constructor(private apiService: ApiService) { }

  getAllCompanies(): Observable<Company[]> {
    return this.apiService.get<Company[]>(this.companyPath);
  }

  getCompanyById(id: number): Observable<Company> {
    return this.apiService.get<Company>(`${this.companyPath}${id}/`);
  }

  createCompany(company: Company): Observable<Company> {
    return this.apiService.post<Company>(this.companyPath, company);
  }

  updateCompany(id: number, company: Company): Observable<Company> {
    return this.apiService.put<Company>(`${this.companyPath}${id}/`, company);
  }

  deleteCompany(id: number): Observable<any> {
    return this.apiService.delete<any>(`${this.companyPath}${id}/`);
  }
}