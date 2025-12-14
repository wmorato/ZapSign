// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\components\notification-panel\notification-panel.component.ts
import { Component, OnInit, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService } from '../../../features/document/services/document.service';
import { RouterLink } from '@angular/router';
import { Document } from '../../models/document.model';

interface RiskSummary {
  totalPending: number;
  level1: number;
  level2: number;
  level3: number;
}

@Component({
  selector: 'app-notification-panel',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './notification-panel.component.html',
  styleUrls: ['./notification-panel.component.scss']
})
export class NotificationPanelComponent implements OnInit {
  @Output() closePanel = new EventEmitter<void>();

  private documentService = inject(DocumentService);

  summary: RiskSummary = { totalPending: 0, level1: 0, level2: 0, level3: 0 };
  loading = true;
  error: string | null = null;

  ngOnInit(): void {
    this.loadRiskSummary();
  }

  loadRiskSummary(): void {
    this.loading = true;
    this.documentService.getAllDocuments().subscribe({
      next: (data) => {
        const now = new Date();
        const pendingDocs = data.filter(doc => doc.status === 'pending' || doc.status === 'new');

        const newSummary: RiskSummary = { totalPending: pendingDocs.length, level1: 0, level2: 0, level3: 0 };

        pendingDocs.forEach(doc => {
          const createdDate = new Date(doc.created_at || now);

          // --- CORREÇÃO DE CÁLCULO DE DIAS PENDENTES (Para robustez contra fusos horários) ---
          // Calcula a diferença em milissegundos
          const diffTime = Math.abs(now.getTime() - createdDate.getTime());

          // Usa Math.floor para obter o número de dias COMPLETO decorridos
          const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
          // --- FIM DA CORREÇÃO ---

          if (diffDays <= 1) {
            newSummary.level1++;
          } else if (diffDays <= 5) {
            newSummary.level2++;
          } else {
            newSummary.level3++;
          }
        });

        this.summary = newSummary;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message || 'Falha ao carregar resumo de risco.';
        this.loading = false;
      }
    });
  }

  // Método auxiliar para obter a classe de risco
  getRiskClass(level: 1 | 2 | 3): string {
    switch (level) {
      case 1: return 'risk-low';
      case 2: return 'risk-medium';
      case 3: return 'risk-high';
    }
  }
}