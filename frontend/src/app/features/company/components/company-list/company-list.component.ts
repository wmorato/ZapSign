// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\company\components\company-list\company-list.component.ts
import { Component, OnInit } from '@angular/core';
import { CompanyService } from '../../services/company.service';
import { Company } from '../../../../core/models/company.model';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-company-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './company-list.component.html',
  styleUrls: ['./company-list.component.scss']
})
export class CompanyListComponent implements OnInit {
  companies: Company[] = [];
  loading = true;
  error: string | null = null;

  constructor(private companyService: CompanyService) { }

  ngOnInit(): void {
    this.loadCompanies();
  }

  loadCompanies(): void {
    this.loading = true;
    this.error = null;
    this.companyService.getAllCompanies().subscribe({
      next: (data) => {
        this.companies = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message || 'Falha ao carregar empresas.';
        this.loading = false;
        console.error('Erro ao carregar empresas:', err);
      }
    });
  }

  deleteCompany(id: number | undefined): void {
    if (id === undefined) {
      return;
    }
    if (confirm('Tem certeza que deseja excluir esta empresa?')) {
      this.companyService.deleteCompany(id).subscribe({
        next: () => {
          this.companies = this.companies.filter(company => company.id !== id);
        },
        error: (err) => {
          this.error = err.message || 'Falha ao excluir empresa.';
          console.error('Erro ao excluir empresa:', err);
        }
      });
    }
  }
}