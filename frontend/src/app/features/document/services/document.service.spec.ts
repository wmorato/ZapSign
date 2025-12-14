// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\services\document.service.spec.ts
import { of, throwError, firstValueFrom } from 'rxjs';
import { DocumentService } from './document.service';
import { ApiService } from '../../../core/services/api.service';
import { Document } from '../../../core/models/document.model';

describe('DocumentService', () => {
    let service: DocumentService;
    let apiServiceMock: any;

    const documentPath = '/api/document/';
    const reanalyzePath = '/api/automations/documents/'; // NOVO
    const reportPath = '/api/automations/reports/'; // NOVO
    const mockDocument: Document = {
        id: 1,
        name: 'Test Document',
        company: 1,
        signers_db: [], // Corrigido para signers_db
        created_at: '2024-01-01',
        last_updated_at: '2024-01-01'
    } as Document; // Adicionado 'as Document' para garantir tipagem

    beforeEach(() => {
        // Mock do ApiService
        apiServiceMock = {
            get: jest.fn(),
            post: jest.fn(),
            put: jest.fn(),
            delete: jest.fn()
        };

        // Criar instância do serviço com mock
        service = new DocumentService(apiServiceMock as ApiService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('downloadDocumentPdf', () => {
        it('should download document PDF and return file_url', async () => { // <--- MODIFICADO
            const documentId = 1;
            const mockResponse = { file_url: '/media/documents/test.pdf' }; // <--- MODIFICADO
            apiServiceMock.get.mockReturnValue(of(mockResponse));

            const result = await firstValueFrom(service.downloadDocumentPdf(documentId));

            expect(result).toEqual(mockResponse);
            expect(result.file_url).toContain('.pdf'); // <--- MODIFICADO
            expect(apiServiceMock.get).toHaveBeenCalledWith(`${documentPath}${documentId}/pdf/`);
        });

        it('should handle errors when downloading PDF', async () => {
            const documentId = 999;
            const error = new Error('PDF not found');
            apiServiceMock.get.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.downloadDocumentPdf(documentId)))
                .rejects.toThrow('PDF not found');
        });
    });

    describe('syncDocumentStatus', () => { // <--- NOVO TESTE
        it('should sync document status via POST request', async () => {
            const documentId = 1;
            const mockResponse = { new_status: 'signed', message: 'Status atualizado para signed.' };
            apiServiceMock.post.mockReturnValue(of(mockResponse));

            const result = await firstValueFrom(service.syncDocumentStatus(documentId));

            expect(result).toEqual(mockResponse);
            expect(apiServiceMock.post).toHaveBeenCalledWith(`${documentPath}${documentId}/sync/`);
        });

        it('should handle errors when syncing status', async () => {
            const documentId = 999;
            const error = new Error('Falha na sincronização com ZapSign');
            apiServiceMock.post.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.syncDocumentStatus(documentId)))
                .rejects.toThrow('Falha na sincronização com ZapSign');
        });
    });

    // ===================================
    // NOVO: Testes de Reanálise de IA
    // ===================================
    describe('reanalyzeDocument', () => {
        it('1. should call POST to the correct reanalyze endpoint', async () => {
            const documentId = 1;
            const mockResponse = { document_id: 1, status: 'pending', message: 'Reanalysis started' };
            apiServiceMock.post.mockReturnValue(of(mockResponse));

            const result = await firstValueFrom(service.reanalyzeDocument(documentId));

            expect(result).toEqual(mockResponse);
            expect(apiServiceMock.post).toHaveBeenCalledWith(`${reanalyzePath}${documentId}/reanalyze/`);
        });

        it('2. should handle errors when triggering reanalysis', async () => {
            const documentId = 1;
            const error = new Error('Reanalysis failed');
            apiServiceMock.post.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.reanalyzeDocument(documentId)))
                .rejects.toThrow('Reanalysis failed');
        });
    });

    // ===================================
    // NOVO: Testes de Relatório
    // ===================================
    describe('getReport', () => {
        it('3. should call POST to the correct report endpoint with period and companyId', async () => {
            const startDate = '2024-01-01';
            const endDate = '2024-01-31';
            const companyId = 10;
            const mockResponse = { summary: { totalDocuments: 5 }, data: { documents: [] } };
            apiServiceMock.post.mockReturnValue(of(mockResponse));

            const expectedBody = {
                report_type: 'monthly_summary',
                start_date: startDate,
                end_date: endDate,
                company_id: companyId
            };

            const result = await firstValueFrom(service.getReport(startDate, endDate, companyId));

            expect(result).toEqual(mockResponse);
            expect(apiServiceMock.post).toHaveBeenCalledWith(reportPath, expectedBody);
        });

        it('4. should handle errors when fetching report', async () => {
            const error = new Error('Report generation error');
            apiServiceMock.post.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.getReport('2024-01-01', '2024-01-31', 10)))
                .rejects.toThrow('Report generation error');
        });
    });

    describe('Type safety', () => {
        it('should return typed Document for getDocumentById', async () => {
            apiServiceMock.get.mockReturnValue(of(mockDocument));

            const result = await firstValueFrom(service.getDocumentById(1));

            expect(result).toHaveProperty('id');
            expect(result).toHaveProperty('name');
            expect(result).toHaveProperty('company');
            expect(typeof result.id).toBe('number');
            expect(typeof result.name).toBe('string');
        });

        it('should return typed Document array for getAllDocuments', async () => {
            const mockDocuments = [mockDocument];
            apiServiceMock.get.mockReturnValue(of(mockDocuments));

            const result = await firstValueFrom(service.getAllDocuments());

            expect(Array.isArray(result)).toBe(true);
            expect(result[0]).toHaveProperty('id');
            expect(result[0]).toHaveProperty('name');
        });
    });
});