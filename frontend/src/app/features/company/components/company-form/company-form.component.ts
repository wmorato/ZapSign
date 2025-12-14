// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\company\components\company-form\company-form.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CompanyService } from '../../services/company.service';
import { Company } from '../../../../core/models/company.model';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-company-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './company-form.component.html',
  styleUrls: ['./company-form.component.scss']
})
export class CompanyFormComponent implements OnInit {
  companyForm: FormGroup;
  isEditMode = false;
  companyId: number | null = null;
  errorMessage: string | null = null;
  successMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private companyService: CompanyService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.companyForm = this.fb.group({
      name: ['', Validators.required],
      apiToken: [''] // Opcional, pode ser vazio
    });
  }

  ngOnInit(): void {
    this.companyId = this.route.snapshot.params['id'];
    if (this.companyId) {
      this.isEditMode = true;
      this.companyService.getCompanyById(this.companyId).subscribe({
        next: (company) => {
          this.companyForm.patchValue(company);
        },
        error: (err) => {
          this.errorMessage = err.message || 'Falha ao carregar dados da empresa.';
          console.error('Erro ao carregar empresa:', err);
        }
      });
    }
  }

  onSubmit(): void {
    this.errorMessage = null;
    this.successMessage = null;

    if (this.companyForm.valid) {
      const companyData: Company = this.companyForm.value;

      if (this.isEditMode && this.companyId) {
        this.companyService.updateCompany(this.companyId, companyData).subscribe({
          next: () => {
            this.successMessage = 'Empresa atualizada com sucesso!';
            this.router.navigate(['/companies']);
          },
          error: (err) => {
            this.errorMessage = err.message || 'Falha ao atualizar empresa.';
            console.error('Erro ao atualizar empresa:', err);
          }
        });
      } else {
        this.companyService.createCompany(companyData).subscribe({
          next: () => {
            this.successMessage = 'Empresa criada com sucesso!';
            this.router.navigate(['/companies']);
          },
          error: (err) => {
            this.errorMessage = err.message || 'Falha ao criar empresa.';
            console.error('Erro ao criar empresa:', err);
          }
        });
      }
    } else {
      this.errorMessage = 'Por favor, preencha todos os campos obrigatórios.';
    }
  }

  onCancel(): void {
    this.router.navigate(['/companies']);
  }
}