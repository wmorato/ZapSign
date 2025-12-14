// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-reports\document-reports.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DocumentReportsComponent } from './document-reports.component';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { DocumentService } from '../../services/document.service';
import { CompanyService } from '../../../company/services/company.service';
import { of, throwError } from 'rxjs';
import { Document } from '../../../../core/models/document.model';
import { CommonModule } from '@angular/common';

describe('DocumentReportsComponent', () => {
    let component: DocumentReportsComponent;
    let fixture: ComponentFixture<DocumentReportsComponent>;
    let documentServiceMock: any;
    let companyServiceMock: any;
    let consoleErrorSpy: jest.SpyInstance;

    const mockCompanyId = 10;
    const mockCompanies = [{ id: mockCompanyId, name: 'Empresa Teste' }];

    const mockDocuments: Document[] = [
        { id: 1, name: 'Assinado', status: 'signed', created_at: '2024-01-15T10:00:00Z', ai_analysis: { status: 'completed' } as any },
        { id: 2, name: 'Pendente Novo', status: 'new', created_at: '2024-02-01T10:00:00Z', ai_analysis: { status: 'pending' } as any },
        { id: 3, name: 'Pendente', status: 'pending', created_at: '2024-02-05T10:00:00Z', ai_analysis: { status: 'processing' } as any },
        { id: 4, name: 'Falhado', status: 'failed', created_at: '2024-02-10T10:00:00Z', ai_analysis: { status: 'failed' } as any },
        { id: 5, name: 'Recusado', status: 'rejected', created_at: '2024-02-15T10:00:00Z', ai_analysis: { status: 'completed' } as any },
    ] as Document[];

    const mockReportResponse = {
        summary: {
            totalDocuments: mockDocuments.length,
            signed: 1, pending: 2, failed: 2, aiPending: 2, aiCompleted: 2
        },
        data: {
            documents: mockDocuments
        }
    };

    beforeEach(async () => {
        // Mock the date to ensure consistent results for the 30-day range
        const mockDate = new Date('2024-02-20T12:00:00Z');
        jest.spyOn(global, 'Date').mockImplementation(() => mockDate as any);

        documentServiceMock = {
            getReport: jest.fn().mockReturnValue(of(mockReportResponse)),
        };
        companyServiceMock = {
            getAllCompanies: jest.fn().mockReturnValue(of(mockCompanies))
        };

        await TestBed.configureTestingModule({
            imports: [DocumentReportsComponent, ReactiveFormsModule, CommonModule],
            providers: [
                FormBuilder,
                { provide: DocumentService, useValue: documentServiceMock },
                { provide: CompanyService, useValue: companyServiceMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(DocumentReportsComponent);
        component = fixture.componentInstance;
        consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

        // A chamada ao ngOnInit dispara o getReport
        component.ngOnInit();
    });

    afterEach(() => {
        consoleErrorSpy.mockRestore();
        // Restore Date mock
        (global.Date as any).mockRestore();
    });

    it('should create the component', () => {
        expect(component).toBeTruthy();
    });

    // ===================================
    // Inicialização e Carregamento
    // ===================================
    it('should calculate summary correctly after loading documents', () => {
        expect(component.summary).toEqual({
            totalDocuments: 5,
            signed: 1,
            pending: 2,
            failed: 2,
            aiPending: 2,
            aiCompleted: 2
        });
        expect(component.allDocuments.length).toBe(5);
        expect(component.documents.length).toBe(5); // Padrão é 'all'
    });

    // ===================================
    // Teste de Filtro Dinâmico (Cards)
    // ===================================
    it('should filter documents by "signed" status', () => {
        component.applyFilter('signed');
        expect(component.selectedFilter).toBe('signed');
        expect(component.documents.length).toBe(1);
        expect(component.documents[0].status).toBe('signed');
    });

    it('should filter documents by "pending" status (pending or new)', () => {
        component.applyFilter('pending');
        expect(component.selectedFilter).toBe('pending');
        expect(component.documents.length).toBe(2);
        expect(component.documents.map(d => d.status)).toEqual(['new', 'pending']);
    });

    it('should filter documents by "aiCompleted" status', () => {
        component.applyFilter('aiCompleted');
        expect(component.selectedFilter).toBe('aiCompleted');
        expect(component.documents.length).toBe(2);
        expect(component.documents.map(d => d.name)).toEqual(['Assinado', 'Recusado']);
    });

    it('should reset filter to "all"', () => {
        component.applyFilter('signed');
        expect(component.documents.length).toBe(1);

        component.resetFilter();
        expect(component.selectedFilter).toBe('all');
        expect(component.documents.length).toBe(5);
    });

    // ===================================
    // Exportação (CSV)
    // ===================================


    it('should alert if no data is available for export', () => {
        const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => { });
        component.documents = [];
        component.downloadDetailedReport();

        expect(alertSpy).toHaveBeenCalledWith('Não há dados para exportar.');
        alertSpy.mockRestore();
    });

    // ===================================
    // Outras Ações
    // ===================================
    it('should call window.print on printReport', () => {
        const printSpy = jest.spyOn(window, 'print').mockImplementation(() => { });
        component.printReport();
        expect(printSpy).toHaveBeenCalled();
        printSpy.mockRestore();
    });

    it('should handle error when getting report', () => {
        documentServiceMock.getReport.mockReturnValue(throwError(() => new Error('Report Failed')));

        // Simula a submissão para re-executar com o erro
        component.onSubmit();

        expect(component.error).toBe('Report Failed');
        expect(component.loading).toBeFalsy();
    });
});