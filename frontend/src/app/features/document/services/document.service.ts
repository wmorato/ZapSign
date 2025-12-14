// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\services\document.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Document } from '../../../core/models/document.model';
import { ApiService } from '../../../core/services/api.service';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private documentPath = '/api/document/';
  // NOVO: Adiciona o caminho base para a automação de reanálise
  private reanalyzePath = '/api/automations/documents/';
  // NOVO: Adiciona o caminho base para a automação de relatórios
  private reportPath = '/api/automations/reports/'; // <--- ADICIONADO

  constructor(private apiService: ApiService) { }

  getAllDocuments(): Observable<Document[]> {
    return this.apiService.get<Document[]>(this.documentPath);
  }

  getDocumentById(id: number): Observable<Document> {
    return this.apiService.get<Document>(`${this.documentPath}${id}/`);
  }

  createDocument(document: Document): Observable<Document> {
    return this.apiService.post<Document>(this.documentPath, document);
  }

  updateDocument(id: number, document: Document): Observable<Document> {
    return this.apiService.put<Document>(`${this.documentPath}${id}/`, document);
  }

  deleteDocument(id: number): Observable<any> {
    return this.apiService.delete<any>(`${this.documentPath}${id}/`);
  }

  // MODIFICADO: Espera { file_url: string } em vez de { file_path: string }
  downloadDocumentPdf(id: number): Observable<{ file_url: string }> {
    // O backend agora retorna 'file_url'
    return this.apiService.get<{ file_url: string }>(`${this.documentPath}${id}/pdf/`);
  }

  // NOVO MÉTODO: Sincronização manual de status
  syncDocumentStatus(id: number): Observable<{ new_status: string, message: string }> {
    // O backend agora tem um endpoint POST para sincronização
    return this.apiService.post<{ new_status: string, message: string }>(`${this.documentPath}${id}/sync/`);
  }

  // NOVO MÉTODO: Disparar reanálise de IA
  reanalyzeDocument(id: number): Observable<{ document_id: number, status: string, message: string }> {
    // Chama o endpoint de automação do backend (POST /api/automations/documents/<id>/reanalyze/)
    return this.apiService.post<{ document_id: number, status: string, message: string }>(`${this.reanalyzePath}${id}/reanalyze/`);
  }

  // NOVO MÉTODO: Obter Relatório de Documentos <--- ADICIONADO
  getReport(startDate: string, endDate: string, companyId: number): Observable<any> {
    const body = {
      report_type: 'monthly_summary',
      start_date: startDate,
      end_date: endDate,
      company_id: companyId
    };
    return this.apiService.post<any>(this.reportPath, body);
  }
}