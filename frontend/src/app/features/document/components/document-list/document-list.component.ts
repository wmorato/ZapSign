// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-list\document-list.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { DocumentService } from '../../services/document.service';
import { Document } from '../../../../core/models/document.model';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { CompanyService } from '../../../company/services/company.service';
import { Company } from '../../../../core/models/company.model';
import { Subscription, interval } from 'rxjs';
import { AuthService } from '../../../../core/auth/auth.service';
import { environment } from '../../../../../environments/environment';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-document-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './document-list.component.html',
  styleUrls: ['./document-list.component.scss']
})
export class DocumentListComponent implements OnInit, OnDestroy {
  // Documentos brutos carregados da API
  allDocuments: Document[] = [];
  // Documentos exibidos na tabela (após filtro/ordenação)
  documents: Document[] = [];
  companies: Company[] = [];
  loading = true;
  error: string | null = null;
  private ws: WebSocket | null = null;
  private pollingSubscription: Subscription | null = null;

  // Variáveis de estado para Pesquisa e Ordenação
  searchTerm: string = '';
  sortColumn: keyof Document | 'companyName' = 'created_at';
  sortDirection: 'asc' | 'desc' = 'desc';

  constructor(
    private documentService: DocumentService,
    private companyService: CompanyService,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    this.loadData();
    // this.startPolling(); // REMOVIDO: Substituído por WebSocket
  }

  ngOnDestroy(): void {
    this.stopPolling(); // Garante que o polling antigo seja limpo se ainda existir
    this.closeWebSocket();
  }

  loadData(): void {
    this.loading = true;
    this.error = null;

    this.companyService.getAllCompanies().subscribe({
      next: (companiesData) => {
        this.companies = companiesData;
        this.documentService.getAllDocuments().subscribe({
          next: (documentsData) => {
            this.allDocuments = documentsData;
            this.applyFilterAndSort();
            this.loading = false;

            // Inicia o WebSocket APÓS carregar os dados e ter o ID da empresa
            if (this.companies.length > 0) {
              this.initWebSocket(this.companies[0].id!); // Assume que o usuário só tem 1 empresa
            }
          },
          error: (err) => {
            this.error = err.message || 'Falha ao carregar documentos.';
            this.loading = false;
            console.error('Erro ao carregar documentos:', err);
          }
        });
      },
      error: (err) => {
        this.error = err.message || 'Falha ao carregar empresas.';
        this.loading = false;
        console.error('Erro ao carregar empresas para documentos:', err);
      }
    });
  }

  // --- Lógica de Pesquisa e Ordenação ---

  applyFilterAndSort(): void {
    let tempDocuments = [...this.allDocuments];

    // 1. Filtragem
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      tempDocuments = tempDocuments.filter(doc =>
        doc.name.toLowerCase().includes(term) ||
        doc.status?.toLowerCase().includes(term) ||
        doc.token?.toLowerCase().includes(term) ||
        this.getCompanyName(doc.company).toLowerCase().includes(term) ||
        doc.id?.toString().includes(term)
      );
    }

    // 2. Ordenação
    tempDocuments.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      if (this.sortColumn === 'companyName') {
        aValue = this.getCompanyName(a.company);
        bValue = this.getCompanyName(b.company);
      } else {
        aValue = a[this.sortColumn as keyof Document];
        bValue = b[this.sortColumn as keyof Document];
      }

      // Trata valores nulos/indefinidos
      if (aValue === undefined || aValue === null) aValue = '';
      if (bValue === undefined || bValue === null) bValue = '';

      // Compara strings ou números
      let comparison = 0;
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        comparison = aValue.localeCompare(bValue);
      } else if (aValue > bValue) {
        comparison = 1;
      } else if (aValue < bValue) {
        comparison = -1;
      }

      return this.sortDirection === 'asc' ? comparison : comparison * -1;
    });

    this.documents = tempDocuments;
  }

  sortBy(column: keyof Document | 'companyName'): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc'; // Padrão: asc na primeira ordenação
    }
    this.applyFilterAndSort();
  }

  // --- Lógica de WebSocket (Atualiza allDocuments e re-aplica filtro/sort) ---

  initWebSocket(companyId: number): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return; // Já conectado
    }

    const token = this.authService.getToken();
    if (!token) {
      console.error('Token JWT não encontrado para WebSocket.');
      return;
    }

    // MODIFICADO: Usa environment.wsUrl
    const wsUrl = `${environment.wsUrl}/ws/document/list/?token=${token}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      // console.log('WebSocket Lista conectado.'); // <--- REMOVIDO
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      // console.log('WS Lista Mensagem recebida:', message); // <--- REMOVIDO

      if (message.type === 'document_list_update') {
        this.handleDocumentListUpdate(message.event_type, message.data);
      }
    };

    this.ws.onclose = (event) => {
      // console.log('WebSocket Lista desconectado:', event.code, event.reason); // <--- REMOVIDO
      this.ws = null;
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket Lista Error:', error);
      this.error = 'Erro na conexão em tempo real. A lista pode não ser atualizada automaticamente.';
    };
  }

  closeWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  handleDocumentListUpdate(eventType: string, data: any): void {
    switch (eventType) {
      case 'document_created':
        // Adiciona o novo documento ao topo da lista
        this.allDocuments = [data, ...this.allDocuments];
        break;
      case 'document_updated':
        // Encontra e substitui o documento atualizado
        const updatedDocIndex = this.allDocuments.findIndex(d => d.id === data.id);
        if (updatedDocIndex !== -1) {
          // Substitui o objeto completo vindo do WS (com o status correto)
          this.allDocuments[updatedDocIndex] = data;
        }
        break;
      case 'document_deleted':
        // Remove o documento da lista
        this.allDocuments = this.allDocuments.filter(d => d.id !== data.id);
        break;
      default:
        console.warn(`Evento desconhecido: ${eventType}`);
    }
    // Re-aplica filtro e ordenação após qualquer atualização
    this.applyFilterAndSort();
  }

  startPolling(): void {
    // Lógica de polling removida
  }

  stopPolling(): void {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
      this.pollingSubscription = null;
    }
  }

  getCompanyName(companyId: number | undefined): string {
    if (companyId === undefined) {
      return 'N/A';
    }
    const company = this.companies.find(c => c.id === companyId);
    return company ? company.name : 'Empresa Desconhecida';
  }

  /**
   * Retorna se o documento está sincronizando (estado de UI)
   */
  isDocumentSyncing(document: Document): boolean {
    // Usa a checagem 'in' para verificar a presença da propriedade 'isSyncing'
    return 'isSyncing' in document && (document as any).isSyncing === true;
  }

  /**
   * Sincroniza o status do documento com a ZapSign.
   */
  syncStatus(document: Document): void {
    if (document.id === undefined || !document.token || this.isDocumentSyncing(document)) {
      return;
    }

    const docIndex = this.documents.findIndex(d => d.id === document.id);
    if (docIndex === -1) return;

    // Adiciona um estado temporário (propriedade nova) para indicar visualmente no botão
    (this.documents[docIndex] as any).isSyncing = true;
    this.documents = [...this.documents]; // Força a atualização do botão

    this.documentService.syncDocumentStatus(document.id).subscribe({
      next: (response) => {
        // Sucesso: A atualização real virá via WebSocket (document_updated).
        // Apenas exibe o feedback visual.
        alert(`Sincronização iniciada com sucesso para o Documento ${document.id}. Status: ${response.message}`);
        // console.log(`[Sync] Disparo de sincronização para Documento ${document.id}. Aguardando WS.`); // <--- REMOVIDO
      },
      error: (err) => {
        // Erro: Remove o estado temporário e mostra erro
        (this.documents[docIndex] as any).isSyncing = false;
        this.documents = [...this.documents]; // Força a atualização da view

        // CORREÇÃO: Usando alert para feedback pontual e não o erro global
        alert(`Falha ao sincronizar o documento ${document.id}. Detalhes: ${err.message}`);
        console.warn(`[Sync] Falha na sincronização do documento ${document.id}.`, err);
      },
      complete: () => {
        // FALLBACK: Resetar o estado de UI após a conclusão da chamada HTTP
        if (docIndex !== -1) {
          (this.documents[docIndex] as any).isSyncing = false;
          this.documents = [...this.documents];
        }
      }
    });
  }

  deleteDocument(id: number | undefined): void {
    if (id === undefined) {
      return;
    }
    if (confirm('Tem certeza que deseja excluir este documento? Isso também removerá os signatários associados.')) {
      this.documentService.deleteDocument(id).subscribe({
        next: () => {
          // A remoção da lista será tratada pelo WebSocket (document_deleted)
          // console.log(`Documento ${id} excluído. Aguardando notificação WS.`); // <--- REMOVIDO
        },
        error: (err) => {
          this.error = err.message || 'Falha ao excluir documento.';
          console.error('Erro ao excluir documento:', err);
        }
      });
    }
  }
}