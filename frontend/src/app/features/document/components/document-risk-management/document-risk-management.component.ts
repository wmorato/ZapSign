// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-risk-management\document-risk-management.component.ts
import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService } from '../../services/document.service';
import { Document } from '../../../../core/models/document.model';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

interface PendingDocument extends Document {
    daysPending: number;
    riskLevel: 1 | 2 | 3;
    isSelected: boolean; // Para seleção em massa
}

@Component({
    selector: 'app-document-risk-management',
    standalone: true,
    imports: [CommonModule, RouterLink, FormsModule],
    templateUrl: './document-risk-management.component.html',
    styleUrls: ['./document-risk-management.component.scss']
})
export class DocumentRiskManagementComponent implements OnInit {
    private documentService = inject(DocumentService);

    allPendingDocuments: PendingDocument[] = [];
    filteredDocuments: PendingDocument[] = [];
    loading = true;
    error: string | null = null;
    selectedRiskLevel: 1 | 2 | 3 | 'all' = 'all';

    // Mensagens de Ação
    private readonly EMAIL_MESSAGE = 'E-mail de notificação simulado enviado com sucesso!';
    private readonly MEETING_CONFIRMATION = 'Boa tarde, estou entrando em contato para conversarmos sobre o contrato e tirarmos dúvidas que eventualmente ficaram. Temos algumas sugestões que podem ser aplicadas ao contrato. Podemos agendar um horário?';

    ngOnInit(): void {
        this.loadPendingDocuments();
    }

    loadPendingDocuments(): void {
        this.loading = true;
        this.error = null;
        this.documentService.getAllDocuments().subscribe({
            next: (data) => {
                const now = new Date();
                this.allPendingDocuments = data
                    .filter(doc => doc.status === 'pending' || doc.status === 'new')
                    .map(doc => {
                        const createdDate = new Date(doc.created_at || now);

                        // --- CORREÇÃO DE CÁLCULO DE DIAS PENDENTES (Para robustez contra fusos horários) ---
                        // Calcula a diferença em milissegundos
                        const diffTime = Math.abs(now.getTime() - createdDate.getTime());

                        // Usa Math.floor para obter o número de dias COMPLETO decorridos
                        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                        // --- FIM DA CORREÇÃO ---

                        let riskLevel: 1 | 2 | 3;
                        if (diffDays <= 1) {
                            riskLevel = 1;
                        } else if (diffDays <= 5) {
                            riskLevel = 2;
                        } else {
                            riskLevel = 3;
                        }

                        return { ...doc, daysPending: diffDays, riskLevel, isSelected: false };
                    })
                    .sort((a, b) => b.daysPending - a.daysPending);

                this.filterDocuments();
                this.loading = false;
            },
            error: (err) => {
                this.error = err.message || 'Falha ao carregar documentos pendentes.';
                this.loading = false;
            }
        });
    }

    filterDocuments(): void {
        if (this.selectedRiskLevel === 'all') {
            this.filteredDocuments = this.allPendingDocuments;
        } else {
            this.filteredDocuments = this.allPendingDocuments.filter(doc => doc.riskLevel === this.selectedRiskLevel);
        }
    }

    // NOVO MÉTODO: Retorna a contagem de documentos para um nível de risco específico
    getRiskCount(level: 1 | 2 | 3): number {
        return this.allPendingDocuments.filter(d => d.riskLevel === level).length;
    }

    getRiskLabel(level: 1 | 2 | 3): string {
        switch (level) {
            case 1: return 'Baixo Risco (0-1 Dia)';
            case 2: return 'Risco Moderado (2-5 Dias)';
            case 3: return 'Alto Risco (+5 Dias)';
        }
    }

    getRiskClass(level: 1 | 2 | 3): string {
        switch (level) {
            case 1: return 'risk-low';
            case 2: return 'risk-medium';
            case 3: return 'risk-high';
        }
    }

    // Ações Individuais
    simulateEmailNotification(document: PendingDocument): void {
        console.log(`[AÇÃO] Enviando e-mail de notificação para o documento ${document.id}.`);
        alert(this.EMAIL_MESSAGE);
    }

    simulateMeetingRequest(document: PendingDocument): void {
        console.log(`[AÇÃO] Solicitando reunião para o documento ${document.id}.`);

        const confirmed = confirm(`Confirmar solicitação de reunião para o documento "${document.name}"?\n\nMensagem a ser enviada:\n"${this.MEETING_CONFIRMATION}"`);

        if (confirmed) {
            alert('Solicitação de reunião simulada enviada com sucesso!');
        }
    }

    // Ações em Massa
    performMassAction(action: 'email' | 'meeting'): void {
        const selectedDocs = this.filteredDocuments.filter(doc => doc.isSelected);
        if (selectedDocs.length === 0) {
            alert('Selecione pelo menos um documento para realizar a ação.');
            return;
        }

        if (action === 'email') {
            console.log(`[AÇÃO EM MASSA] Enviando e-mail para ${selectedDocs.length} documentos.`);
            alert(`E-mail de notificação simulado enviado para ${selectedDocs.length} documentos.`);
        } else if (action === 'meeting') {
            const confirmed = confirm(`Confirmar solicitação de reunião para ${selectedDocs.length} documentos?\n\nMensagem a ser enviada:\n"${this.MEETING_CONFIRMATION}"`);
            if (confirmed) {
                console.log(`[AÇÃO EM MASSA] Solicitando reunião para ${selectedDocs.length} documentos.`);
                alert(`Solicitação de reunião simulada enviada para ${selectedDocs.length} documentos.`);
            }
        }
        // Desseleciona após a ação
        this.filteredDocuments.forEach(doc => doc.isSelected = false);
    }

    // Seleção em Massa
    toggleSelectAll(event: any): void {
        const isChecked = event.target.checked;
        this.filteredDocuments.forEach(doc => doc.isSelected = isChecked);
    }

    get selectedCount(): number {
        return this.filteredDocuments.filter(doc => doc.isSelected).length;
    }
}