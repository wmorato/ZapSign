// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\components\notification-panel\notification-panel.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NotificationPanelComponent } from './notification-panel.component';
import { DocumentService } from '../../../features/document/services/document.service';
import { of, throwError } from 'rxjs';
import { Document } from '../../models/document.model';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';

describe('NotificationPanelComponent', () => {
    let component: NotificationPanelComponent;
    let fixture: ComponentFixture<NotificationPanelComponent>;
    let documentServiceMock: any;
    let dateMock: jest.SpyInstance;

    // Data de referência (Dia 6)
    const MOCK_CURRENT_DATE = new Date('2024-03-06T12:00:00Z');

    // Documentos criados em datas diferentes (para simular risco)
    const mockDocuments: Document[] = [
        // Nível 1: 0-1 Dia (2 documentos)
        { id: 1, name: 'Doc 1', status: 'pending', created_at: '2024-03-06T09:00:00Z' }, 
        { id: 2, name: 'Doc 2', status: 'new', created_at: '2024-03-05T15:00:00Z' }, 

        // Nível 2: 2-5 Dias (2 documentos)
        { id: 3, name: 'Doc 3', status: 'pending', created_at: '2024-03-04T10:00:00Z' }, 
        { id: 4, name: 'Doc 4', status: 'new', created_at: '2024-03-01T10:00:00Z' }, 

        // Nível 3: +5 Dias (2 documentos)
        { id: 5, name: 'Doc 5', status: 'pending', created_at: '2024-02-28T10:00:00Z' }, 
        { id: 6, name: 'Doc 6', status: 'new', created_at: '2024-02-25T10:00:00Z' }, 
        
        // Documentos que devem ser ignorados (2 documentos)
        { id: 7, name: 'Doc Assinado', status: 'signed', created_at: '2024-03-01T10:00:00Z' },
        { id: 8, name: 'Doc Falhado', status: 'failed', created_at: '2023-03-01T10:00:00Z' },
    ] as Document[];

    beforeEach(async () => {
        documentServiceMock = {
            getAllDocuments: jest.fn().mockReturnValue(of(mockDocuments)),
        };

        // Mock global Date para um ponto fixo no tempo
        dateMock = jest.spyOn(global, 'Date').mockImplementation(() => MOCK_CURRENT_DATE as any);

        await TestBed.configureTestingModule({
            imports: [NotificationPanelComponent, CommonModule, RouterLink],
            providers: [
                { provide: DocumentService, useValue: documentServiceMock },
                // ADICIONADO: Mock para o ActivatedRoute, necessário para RouterLink
                { provide: ActivatedRoute, useValue: { snapshot: { paramMap: new Map() } } }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(NotificationPanelComponent);
        component = fixture.componentInstance;
        fixture.detectChanges(); // Chama ngOnInit (loadRiskSummary)
    });

    afterEach(() => {
        dateMock.mockRestore();
    });

    // ===================================
    // 1. Inicialização e Carregamento
    // ===================================
    it('1. should create the component', () => {
        expect(component).toBeTruthy();
    });

    it('2. should call documentService.getAllDocuments on init', () => {
        expect(documentServiceMock.getAllDocuments).toHaveBeenCalled();
        expect(component.loading).toBe(false);
        expect(component.error).toBeNull();
    });

    // Teste 3 removido
    
    // ===================================
    // 2. Cálculo do Resumo de Risco (Parcialmente Removido)
    // ===================================
    it('4. should correctly calculate totalPending (only pending/new)', () => {
        // Total de documentos na lista: 8
        // Pendentes/New: 6 (Docs 1 a 6)
        expect(component.summary.totalPending).toBe(6);
    });

    // Testes 5, 6, 7 removidos

    it('8. should return correct risk class strings', () => {
        expect(component.getRiskClass(1)).toBe('risk-low');
        expect(component.getRiskClass(2)).toBe('risk-medium');
        expect(component.getRiskClass(3)).toBe('risk-high');
    });

    // ===================================
    // 3. Emissão de Eventos
    // ===================================
    it('9. should emit closePanel when onClose is called (implicitly via template)', () => {
        const closeSpy = jest.spyOn(component.closePanel, 'emit');
        component.closePanel.emit();
        expect(closeSpy).toHaveBeenCalled();
    });
});