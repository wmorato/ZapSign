// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-detail\document-detail.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { DocumentService } from '../../services/document.service';
import { Document, DocumentAnalysis } from '../../../../core/models/document.model';
import { CommonModule } from '@angular/common';
import { CompanyService } from '../../../company/services/company.service';
import { Company } from '../../../../core/models/company.model';
import { Subscription, interval } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';
import { AuthService } from '../../../../core/auth/auth.service';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-document-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './document-detail.component.html',
  styleUrls: ['./document-detail.component.scss']
})
export class DocumentDetailComponent implements OnInit, OnDestroy {
  document: Document | null = null;
  companyName: string = 'Carregando...';
  loading = true;
  error: string | null = null;
  isReanalyzeProcessing = false;
  private ws: WebSocket | null = null;
  private documentId: number | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private documentService: DocumentService,
    private companyService: CompanyService,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.documentId = +id;
        this.loadDocumentDetails(this.documentId);
      } else {
        this.error = 'ID do documento não fornecido.';
        this.loading = false;
      }
    });
  }

  ngOnDestroy(): void {
    this.closeWebSocket();
  }

  loadDocumentDetails(id: number): void {
    this.loading = true;
    this.error = null;
    this.documentService.getDocumentById(id).subscribe({
      next: (data) => {
        this.document = data;
        this.loadCompanyName(data.company);
        this.loading = false;

        if (data.ai_analysis && (data.ai_analysis.status === 'completed' || data.ai_analysis.status === 'failed')) {
          this.isReanalyzeProcessing = false;
        }

        if (this.shouldUseWebSocket(data)) {
          this.isReanalyzeProcessing = true;
          this.initWebSocket(id);
        } else {
          this.closeWebSocket();
        }
      },
      error: (err) => {
        this.error = err.message || 'Falha ao carregar detalhes do documento.';
        this.loading = false;
        this.isReanalyzeProcessing = false;
        console.error('Erro ao carregar documento:', err);
      }
    });
  }

  loadCompanyName(companyId: number): void {
    this.companyService.getCompanyById(companyId).subscribe({
      next: (company: Company) => {
        this.companyName = company.name;
      },
      error: (err) => {
        this.companyName = 'Empresa Desconhecida';
        console.error('Erro ao carregar nome da empresa:', err);
      }
    });
  }

  // --- Lógica de WebSocket (Substitui o Polling) ---

  shouldUseWebSocket(doc: Document): boolean {
    const status = doc.ai_analysis?.status;
    // Usa WS se a análise estiver pendente ou processando
    return status === 'pending' || status === 'processing';
  }

  initWebSocket(id: number): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return; // Já conectado
    }

    const token = this.authService.getToken();
    if (!token) {
      console.error('Token JWT não encontrado para WebSocket.');
      return;
    }

    // MODIFICADO: Usa environment.wsUrl
    const wsUrl = `${environment.wsUrl}/ws/document/${id}/?token=${token}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      // console.log('WebSocket conectado para análise de IA.'); // <--- REMOVIDO
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      // console.log('WS Mensagem recebida:', message); // <--- REMOVIDO

      if (message.type === 'document_update') {
        if (message.event_type === 'analysis_completed') {
          this.updateDocumentFromWs(message.data);
          this.isReanalyzeProcessing = false;
          this.closeWebSocket();
        } else if (message.event_type === 'analysis_status_update') {
          this.updateAnalysisStatusFromWs(message.data);

          if (message.data.status !== 'processing' && message.data.status !== 'pending') {
            this.isReanalyzeProcessing = false;
          }
        }
      }
    };

    this.ws.onclose = (event) => {
      // console.log('WebSocket desconectado:', event.code, event.reason); // <--- REMOVIDO
      this.ws = null;
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      this.error = 'Erro na conexão em tempo real. O status pode não ser atualizado automaticamente.';
      this.isReanalyzeProcessing = false;
    };
  }

  closeWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  updateAnalysisStatusFromWs(data: any): void {
    if (this.document) {
      // Garante que o objeto ai_analysis exista antes de tentar atualizar
      if (!this.document.ai_analysis) {
        this.document.ai_analysis = {} as DocumentAnalysis;
      }
      this.document.ai_analysis.status = data.status;
      if (data.summary) {
        this.document.ai_analysis.summary = data.summary;
      }
    }
  }


  updateDocumentFromWs(data: any): void {
    // Recarrega o documento completo para obter todos os dados da análise
    if (this.documentId) {
      this.loadDocumentDetails(this.documentId);
    }
  }

  // --- Lógica de Reanálise de IA ---

  reanalyzeDocument(): void {
    if (!this.documentId || !this.document?.url_pdf || this.isReanalyzeProcessing) {
      return;
    }

    this.isReanalyzeProcessing = true;
    this.error = null;

    this.documentService.reanalyzeDocument(this.documentId).subscribe({
      next: (response) => {
        // console.log('Reanálise disparada:', response.message); // <--- REMOVIDO
        // Inicia ou reabre o WebSocket para receber o status 'processing'
        this.initWebSocket(this.documentId!);

        if (!this.document!.ai_analysis) {
          this.document!.ai_analysis = {
            status: 'pending',
            summary: null,
            missing_topics: null,
            insights: null,
            model_used: 'gemini',
            created_at: new Date().toISOString(),
            last_updated_at: new Date().toISOString()
          } as DocumentAnalysis;
        } else {
          this.document!.ai_analysis.status = 'pending';
        }
      },
      error: (err) => {
        this.error = err.message || 'Falha ao disparar reanálise de IA.';
        this.isReanalyzeProcessing = false;
        console.error('Erro ao disparar reanálise:', err);
      }
    });
  }

  // --- Métodos Existentes ---

  downloadPdf(): void {
    if (this.document?.id) {
      this.documentService.downloadDocumentPdf(this.document.id).subscribe({
        next: (response) => {
          if (response.file_url) {
            window.open(response.file_url, '_blank');
          } else {
            alert('O link para o PDF assinado não está disponível.');
          }
        },
        error: (err) => {
          this.error = err.message || 'Falha ao obter link do PDF.';
          console.error('Erro ao obter link do PDF:', err);
        }
      });
    }
  }

  getAiAnalysisStatus(analysis: DocumentAnalysis | undefined): string {
    if (!analysis) {
      return 'N/A';
    }
    switch (analysis.status) {
      case 'pending': return 'Pendente (Atualizando...)';
      case 'processing': return 'Processando (Atualizando...)';
      case 'completed': return 'Concluída';
      case 'failed': return 'Falhou';
      default: return analysis.status;
    }
  }
}