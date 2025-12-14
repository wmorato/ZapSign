// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-list\document-list.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DocumentListComponent } from './document-list.component';
import { DocumentService } from '../../services/document.service';
import { CompanyService } from '../../../company/services/company.service';
import { AuthService } from '../../../../core/auth/auth.service';
import { of, throwError, EMPTY } from 'rxjs';
import { Document } from '../../../../core/models/document.model';
import { Company } from '../../../../core/models/company.model';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, ActivatedRoute } from '@angular/router';

describe('DocumentListComponent', () => {
    let component: DocumentListComponent;
    let fixture: ComponentFixture<DocumentListComponent>;
    let documentServiceMock: any;
    let companyServiceMock: any;
    let authServiceMock: any;
    let consoleErrorSpy: jest.SpyInstance;
    let confirmSpy: jest.SpyInstance;

    const mockCompanies: Company[] = [
        { id: 10, name: 'Alpha Corp', apiToken: 'TKN10' },
        { id: 20, name: 'Beta Ltd', apiToken: 'TKN20' }
    ];

    const mockDocuments: Document[] = [
        { id: 101, name: 'Contrato Z', company: 10, status: 'signed', token: 'Z-101', created_at: '2024-03-05T10:00:00Z' } as Document,
        { id: 102, name: 'Proposta A', company: 20, status: 'new', token: 'A-102', created_at: '2024-03-01T10:00:00Z' } as Document,
        { id: 103, name: 'Acordo B', company: 10, status: 'pending', token: 'B-103', created_at: '2024-03-10T10:00:00Z' } as Document,
        { id: 104, name: 'NDA Teste', company: 20, status: 'signed', token: 'NDA-04', created_at: '2024-03-02T10:00:00Z' } as Document,
        { id: 105, name: 'Doc Sem Token', company: 10, status: 'new', token: undefined, created_at: '2024-03-08T10:00:00Z' } as Document,
    ];

    beforeEach(async () => {
        documentServiceMock = {
            getAllDocuments: jest.fn().mockReturnValue(of(mockDocuments)),
            deleteDocument: jest.fn().mockReturnValue(of({})),
            syncDocumentStatus: jest.fn().mockReturnValue(of({ new_status: 'signed', message: 'synced' })),
        };

        companyServiceMock = {
            getAllCompanies: jest.fn().mockReturnValue(of(mockCompanies)),
        };

        authServiceMock = {
            getToken: jest.fn().mockReturnValue('fake.jwt.token')
        };

        // Mock para RouterLink (depende de ActivatedRoute)
        const activatedRouteMock = {
            snapshot: {
                params: {}
            }
        };

        consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => { });
        confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);

        await TestBed.configureTestingModule({
            imports: [DocumentListComponent, CommonModule, FormsModule, RouterLink],
            providers: [
                { provide: DocumentService, useValue: documentServiceMock },
                { provide: CompanyService, useValue: companyServiceMock },
                { provide: AuthService, useValue: authServiceMock },
                { provide: ActivatedRoute, useValue: activatedRouteMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(DocumentListComponent);
        component = fixture.componentInstance;
        // Não chamar detectChanges aqui, para permitir testes de inicialização com diferentes mocks
    });

    afterEach(() => {
        consoleErrorSpy.mockRestore();
        jest.restoreAllMocks();
    });

    // --- GRUPO 1: Inicialização e Carregamento (5 testes) ---

    it('1. should create the component and call loadData on init', () => {
        fixture.detectChanges();
        expect(component).toBeTruthy();
        expect(companyServiceMock.getAllCompanies).toHaveBeenCalled();
        expect(documentServiceMock.getAllDocuments).toHaveBeenCalled();
        expect(component.loading).toBe(false);
    });

    it('2. should correctly map Company Name on load', () => {
        fixture.detectChanges();
        expect(component.companies.length).toBe(2);
        expect(component.getCompanyName(10)).toBe('Alpha Corp');
        expect(component.getCompanyName(99)).toBe('Empresa Desconhecida');
    });

    it('3. should handle error when loading Companies', () => {
        companyServiceMock.getAllCompanies.mockReturnValue(throwError(() => new Error('Comp Load Error')));
        fixture.detectChanges();
        expect(component.error).toBe('Comp Load Error');
        expect(component.loading).toBe(false);
    });

    it('4. should handle error when loading Documents', () => {
        documentServiceMock.getAllDocuments.mockReturnValue(throwError(() => new Error('Doc Load Error')));
        fixture.detectChanges();
        expect(component.error).toBe('Doc Load Error');
        expect(component.loading).toBe(false);
    });

    it('5. should initialize WebSocket after loading Companies and Documents', () => {
        const wsSpy = jest.spyOn(component as any, 'initWebSocket').mockImplementation(() => { });
        fixture.detectChanges();
        expect(wsSpy).toHaveBeenCalledWith(10); // Assume o ID da primeira empresa
    });

    // --- GRUPO 2: Sincronização (Sync) e Estado (6 testes) ---

    it('6. should call syncDocumentStatus when token is available', () => {
        fixture.detectChanges();
        component.syncStatus(mockDocuments[0]); // Doc 101, com token
        expect(documentServiceMock.syncDocumentStatus).toHaveBeenCalledWith(101);
    });

    it('7. should NOT call syncDocumentStatus when token is missing', () => {
        fixture.detectChanges();
        component.syncStatus(mockDocuments[4]); // Doc 105, sem token
        expect(documentServiceMock.syncDocumentStatus).not.toHaveBeenCalled();
    });

    it('10. should reset isSyncing state on sync success (via complete fallback)', (done) => {
        fixture.detectChanges();

        component.syncStatus(component.documents[0]);

        // O estado deve ser resetado no `complete` (simulando que o WS falhou)
        setTimeout(() => {
            fixture.detectChanges();
            expect(component.isDocumentSyncing(component.documents[0])).toBe(false);
            done();
        }, 0);
    });

    it('11. should indicate syncing via isDocumentSyncing helper', () => {
        fixture.detectChanges();
        (component.documents[0] as any).isSyncing = true;
        expect(component.isDocumentSyncing(component.documents[0])).toBe(true);
        (component.documents[0] as any).isSyncing = false;
        expect(component.isDocumentSyncing(component.documents[0])).toBe(false);
    });

    // --- GRUPO 3: Exclusão (3 testes) ---

    it('12. should call deleteDocument and not remove from local list (rely on WS)', () => {
        fixture.detectChanges();
        const initialCount = component.allDocuments.length;
        component.deleteDocument(101);

        expect(confirmSpy).toHaveBeenCalled();
        expect(documentServiceMock.deleteDocument).toHaveBeenCalledWith(101);
        expect(component.allDocuments.length).toBe(initialCount); // Não remove localmente, espera-se WS
    });

    it('13. should NOT call deleteDocument if confirmation is cancelled', () => {
        confirmSpy.mockReturnValue(false);
        fixture.detectChanges();
        component.deleteDocument(101);

        expect(documentServiceMock.deleteDocument).not.toHaveBeenCalled();
    });

    it('14. should show error on deleteDocument failure', () => {
        documentServiceMock.deleteDocument.mockReturnValue(throwError(() => new Error('Delete Error')));
        fixture.detectChanges();
        component.deleteDocument(101);

        expect(component.error).toBe('Delete Error');
    });

    // --- GRUÁN-SE 4: Ordenação (5 testes) ---

    it('15. should sort by ID descending by default (created_at desc)', () => {
        fixture.detectChanges();
        expect(component.documents[0].id).toBe(103); // created_at: Mar 10
        expect(component.documents[4].id).toBe(102); // created_at: Mar 01
    });

    it('16. should sort by Name ascending', () => {
        fixture.detectChanges();
        component.sortBy('name'); // Ordem: Acordo B (103), Contrato Z (101), Doc Sem Token (105), NDA Teste (104), Proposta A (102)
        expect(component.documents[0].name).toBe('Acordo B');
        expect(component.documents[4].name).toBe('Proposta A');
    });

    it('17. should sort by Company Name descending', () => {
        fixture.detectChanges();
        component.sortBy('companyName'); // Alpha (10) e Beta (20). A > B.
        component.sortBy('companyName'); // Altera para 'desc'
        // Beta Ltd (20) deve vir primeiro que Alpha Corp (10)
        expect(component.documents[0].company).toBe(20);
        expect(component.documents[1].company).toBe(20);
        expect(component.documents[2].company).toBe(10);
    });

    it('18. should toggle sorting direction when clicking same column', () => {
        fixture.detectChanges();
        component.sortBy('name');
        expect(component.sortDirection).toBe('asc');

        component.sortBy('name');
        expect(component.sortDirection).toBe('desc');
        expect(component.documents[0].name).toBe('Proposta A');
    });

    it('19. should reset direction to asc when clicking new column', () => {
        fixture.detectChanges();
        component.sortDirection = 'desc';
        component.sortBy('id'); // Troca a coluna
        expect(component.sortDirection).toBe('asc');
    });

    // --- GRUPO 5: Pesquisa (7 testes) ---

    it('20. should filter by partial document name (Z)', () => {
        fixture.detectChanges();
        component.searchTerm = 'Z';
        component.applyFilterAndSort();
        expect(component.documents.length).toBe(1);
        expect(component.documents[0].name).toBe('Contrato Z');
    });

    it('21. should filter by partial document name (Teste)', () => {
        fixture.detectChanges();
        component.searchTerm = 'Teste';
        component.applyFilterAndSort();
        expect(component.documents.length).toBe(1);
        expect(component.documents[0].name).toBe('NDA Teste');
    });

    it('22. should filter by status (signed)', () => {
        fixture.detectChanges();
        component.searchTerm = 'signed';
        component.applyFilterAndSort();
        expect(component.documents.length).toBe(2);
        expect(component.documents.every(d => d.status === 'signed')).toBe(true);
    });

    it('23. should filter by status (new) and token (A-102)', () => {
        fixture.detectChanges();
        component.searchTerm = 'A-102';
        component.applyFilterAndSort();
        expect(component.documents.length).toBe(1);
        expect(component.documents[0].name).toBe('Proposta A');
    });

    it('24. should filter by company name (Alpha)', () => {
        fixture.detectChanges();
        component.searchTerm = 'Alpha';
        component.applyFilterAndSort();
        expect(component.documents.length).toBe(3);
        expect(component.documents.every(d => d.company === 10)).toBe(true);
    });

    it('25. should filter by document ID (105)', () => {
        fixture.detectChanges();
        component.searchTerm = '105';
        component.applyFilterAndSort();
        expect(component.documents.length).toBe(1);
        expect(component.documents[0].id).toBe(105);
    });

    it('26. should return all documents when search term is empty', () => {
        fixture.detectChanges();
        component.searchTerm = 'Z';
        component.applyFilterAndSort(); // Filtra para 1
        expect(component.documents.length).toBe(1);

        component.searchTerm = '';
        component.applyFilterAndSort(); // Limpa
        expect(component.documents.length).toBe(5);
    });

    it('28. should update existing document on document_updated event', () => {
        fixture.detectChanges();
        const updatedDoc: Document = { id: 101, name: 'Contrato Z', company: 10, status: 'pending', token: 'Z-101', created_at: '2024-03-05T10:00:00Z' } as Document;
        component.handleDocumentListUpdate('document_updated', updatedDoc);

        const docInList = component.allDocuments.find(d => d.id === 101);
        expect(docInList!.status).toBe('pending');
    });

    it('29. should remove document on document_deleted event', () => {
        fixture.detectChanges();
        component.handleDocumentListUpdate('document_deleted', { id: 101 });

        expect(component.allDocuments.length).toBe(4);
        expect(component.allDocuments.some(d => d.id === 101)).toBe(false);
    });

    it('30. should re-apply filter and sort after WS update', () => {
        fixture.detectChanges();
        component.searchTerm = 'Alpha';
        component.applyFilterAndSort(); // Filtra por Alpha (3 docs)
        expect(component.documents.length).toBe(3);

        const newDocBeta: Document = { id: 106, name: 'New Beta', company: 20, status: 'new' } as Document;
        component.handleDocumentListUpdate('document_created', newDocBeta); // Adiciona um documento fora do filtro

        // Como o WS update deve re-aplicar o filtro, a contagem deve permanecer 3 (os 3 da Alpha)
        // O novo documento (Beta) não deve aparecer na lista filtrada.
        expect(component.documents.length).toBe(3);
        expect(component.documents.some(d => d.id === 106)).toBe(false);
    });
});