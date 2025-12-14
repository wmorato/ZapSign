// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-reports\document-reports.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { DocumentService } from '../../services/document.service';
import { CompanyService } from '../../../company/services/company.service';
import { Document } from '../../../../core/models/document.model';
import { Company } from '../../../../core/models/company.model';
import { RouterLink } from '@angular/router';

interface ReportSummary {
    totalDocuments: number;
    signed: number;
    pending: number;
    failed: number;
    aiPending: number; // <--- NOVO
    aiCompleted: number; // <--- NOVO
}

// Tipos de filtro que podem ser aplicados ao clicar nos cards
type DocumentFilter = 'all' | 'signed' | 'pending' | 'failed' | 'aiPending' | 'aiCompleted'; // <--- NOVO

@Component({
    selector: 'app-document-reports',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, RouterLink],
    templateUrl: './document-reports.component.html',
    styleUrls: ['./document-reports.component.scss']
})
export class DocumentReportsComponent implements OnInit {
    reportForm: FormGroup;
    loading = false;
    error: string | null = null;
    // Documentos brutos carregados do backend (para manter o estado)
    allDocuments: Document[] = []; // <--- NOVO
    // Documentos exibidos na tabela (após filtro de card)
    documents: Document[] = [];
    summary: ReportSummary | null = null;
    companyId: number | null = null;

    selectedFilter: DocumentFilter = 'all'; // <--- NOVO: Filtro ativo

    constructor(
        private fb: FormBuilder,
        private documentService: DocumentService,
        private companyService: CompanyService
    ) {
        // Inicializa o formulário com o período padrão (últimos 30 dias)
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 30);

        this.reportForm = this.fb.group({
            startDate: [this.formatDate(startDate), Validators.required],
            endDate: [this.formatDate(endDate), Validators.required]
        });
    }

    ngOnInit(): void {
        // Obtém o ID da empresa do usuário logado (necessário para o endpoint de automação)
        this.companyService.getAllCompanies().subscribe({
            next: (companies) => {
                if (companies.length > 0) {
                    this.companyId = companies[0].id!; // Assume a primeira empresa do usuário
                    this.onSubmit(); // Gera o relatório inicial
                } else {
                    this.error = 'Nenhuma empresa associada ao usuário.';
                }
            },
            error: (err) => {
                this.error = err.message || 'Falha ao carregar dados da empresa.';
            }
        });
    }

    private formatDate(date: Date): string {
        const d = new Date(date);
        let month = '' + (d.getMonth() + 1);
        let day = '' + d.getDate();
        const year = d.getFullYear();

        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;

        return [year, month, day].join('-');
    }

    onSubmit(): void {
        this.error = null;
        if (this.reportForm.invalid || this.companyId === null) {
            this.error = 'Por favor, selecione um período válido e verifique a associação da empresa.';
            return;
        }

        this.loading = true;
        const { startDate, endDate } = this.reportForm.value;

        this.documentService.getReport(startDate, endDate, this.companyId).subscribe({
            next: (response) => {
                this.allDocuments = response.data.documents || []; // Salva os documentos brutos
                this.calculateSummary(this.allDocuments);
                this.applyFilter(this.selectedFilter); // Aplica o filtro atual (default 'all')
                this.loading = false;
            },
            error: (err) => {
                this.error = err.message || 'Falha ao gerar relatório.';
                this.loading = false;
                console.error('Erro ao gerar relatório:', err);
            }
        });
    }

    private calculateSummary(documents: Document[]): void {
        const summary: ReportSummary = {
            totalDocuments: documents.length,
            signed: 0,
            pending: 0,
            failed: 0,
            aiPending: 0, // <--- NOVO
            aiCompleted: 0 // <--- NOVO
        };

        documents.forEach(doc => {
            const status = doc.status?.toLowerCase();
            if (status === 'signed') {
                summary.signed++;
            } else if (status === 'pending' || status === 'new') {
                summary.pending++;
            } else if (status === 'failed' || status === 'rejected') {
                summary.failed++;
            }

            const aiStatus = doc.ai_analysis?.status?.toLowerCase();
            if (aiStatus === 'completed') {
                summary.aiCompleted++;
            } else if (aiStatus === 'pending' || aiStatus === 'processing') {
                summary.aiPending++;
            }
        });

        this.summary = summary;
    }

    // NOVO MÉTODO: Aplica o filtro com base no card clicado
    applyFilter(filter: DocumentFilter): void {
        this.selectedFilter = filter;
        let filtered: Document[] = [...this.allDocuments];

        switch (filter) {
            case 'signed':
                filtered = filtered.filter(doc => doc.status?.toLowerCase() === 'signed');
                break;
            case 'pending':
                filtered = filtered.filter(doc => doc.status?.toLowerCase() === 'pending' || doc.status?.toLowerCase() === 'new');
                break;
            case 'failed':
                filtered = filtered.filter(doc => doc.status?.toLowerCase() === 'failed' || doc.status?.toLowerCase() === 'rejected');
                break;
            case 'aiCompleted':
                filtered = filtered.filter(doc => doc.ai_analysis?.status?.toLowerCase() === 'completed');
                break;
            case 'aiPending':
                filtered = filtered.filter(doc => doc.ai_analysis?.status?.toLowerCase() === 'pending' || doc.ai_analysis?.status?.toLowerCase() === 'processing');
                break;
            case 'all':
            default:
                // Não faz nada, usa todos os documentos
                break;
        }

        this.documents = filtered;
    }

    // NOVO MÉTODO: Reseta o filtro
    resetFilter(): void {
        this.applyFilter('all');
    }

    downloadDetailedReport(): void {
        if (this.documents.length === 0) {
            alert('Não há dados para exportar.');
            return;
        }

        const headers = ['ID', 'Nome', 'Status', 'Criado Em', 'ID Externo', 'Análise IA Status'];
        const csv = this.documents.map(doc => [
            doc.id,
            `"${doc.name}"`,
            doc.status,
            doc.created_at,
            doc.externalID || 'N/A',
            doc.ai_analysis?.status || 'N/A'
        ].join(','));

        const csvContent = [headers.join(','), ...csv].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `relatorio_documentos_${this.reportForm.value.startDate}_a_${this.reportForm.value.endDate}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Método para simular o "print da tela" (simplesmente abre a página em uma nova aba para impressão)
    printReport(): void {
        window.print();
    }
}