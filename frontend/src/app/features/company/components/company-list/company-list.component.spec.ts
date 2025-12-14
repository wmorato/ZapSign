// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\company\components\company-list\company-list.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CompanyListComponent } from './company-list.component';
import { CompanyService } from '../../services/company.service';
import { of, throwError, EMPTY } from 'rxjs'; // Importe EMPTY
import { Company } from '../../../../core/models/company.model';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';

describe('CompanyListComponent', () => {
    let component: CompanyListComponent;
    let fixture: ComponentFixture<CompanyListComponent>;
    let companyServiceMock: any;
    let consoleErrorSpy: jest.SpyInstance;

    const mockCompanies: Company[] = [
        { id: 1, name: 'Empresa A', apiToken: 'token1' },
        { id: 2, name: 'Empresa B', apiToken: 'token2' }
    ];

    // Mock mínimo para ActivatedRoute para satisfazer RouterLink no template
    const activatedRouteMock = {
        snapshot: {
            params: {}
        }
    };

    beforeEach(async () => {
        companyServiceMock = {
            getAllCompanies: jest.fn().mockReturnValue(of(mockCompanies)),
            deleteCompany: jest.fn().mockReturnValue(of({}))
        };

        // Silencia console.error para testes de erro
        consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

        await TestBed.configureTestingModule({
            imports: [CompanyListComponent, CommonModule, RouterLink],
            providers: [
                { provide: CompanyService, useValue: companyServiceMock },
                { provide: ActivatedRoute, useValue: activatedRouteMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(CompanyListComponent);
        component = fixture.componentInstance;
    });

    afterEach(() => {
        consoleErrorSpy.mockRestore(); // Restaura o console.error
    });

    it('should create the component', () => {
        fixture.detectChanges();
        expect(component).toBeTruthy();
    });

    // ===================================
    // Carregamento de Dados
    // ===================================
    it('should load companies on init and display them', () => {
        component.ngOnInit();

        expect(companyServiceMock.getAllCompanies).toHaveBeenCalled();
        expect(component.companies).toEqual(mockCompanies);
        expect(component.loading).toBeFalsy();
        expect(component.error).toBeNull();
    });

    it('should display error message on load failure', () => {
        companyServiceMock.getAllCompanies.mockReturnValue(throwError(() => new Error('API Error')));

        component.ngOnInit();

        expect(component.companies.length).toBe(0);
        expect(component.loading).toBeFalsy();
        expect(component.error).toBe('API Error');
    });

    it('should set loading to true before the async call completes', () => {
        // Usa um observable que não completa imediatamente (EMPTY) para que o `loading` fique true.
        companyServiceMock.getAllCompanies.mockReturnValue(EMPTY);
        component.loading = false; // Garante que o estado está 'false' antes de iniciar a carga

        component.loadCompanies();

        // Neste ponto, `loadCompanies` já setou para true, mas a subscrição ainda não terminou
        expect(component.loading).toBeTruthy();
    });

    // ===================================
    // Exclusão de Empresa
    // ===================================
    it('should call deleteCompany and remove company from list on success', () => {
        jest.spyOn(window, 'confirm').mockReturnValue(true);
        component.companies = [...mockCompanies]; // Inicializa a lista

        component.deleteCompany(1);

        expect(companyServiceMock.deleteCompany).toHaveBeenCalledWith(1);
        expect(component.companies.length).toBe(1);
        expect(component.companies.find(c => c.id === 1)).toBeUndefined();
    });

    it('should not call deleteCompany if confirmation is cancelled', () => {
        jest.spyOn(window, 'confirm').mockReturnValue(false);
        component.companies = [...mockCompanies];

        component.deleteCompany(1);

        expect(companyServiceMock.deleteCompany).not.toHaveBeenCalled();
        expect(component.companies.length).toBe(2);
    });

    it('should not call deleteCompany if id is undefined', () => {
        jest.spyOn(window, 'confirm').mockReturnValue(true);
        component.companies = [...mockCompanies];

        component.deleteCompany(undefined);

        expect(companyServiceMock.deleteCompany).not.toHaveBeenCalled();
        expect(component.companies.length).toBe(2);
    });

    it('should display error message on deleteCompany failure', () => {
        jest.spyOn(window, 'confirm').mockReturnValue(true);
        companyServiceMock.deleteCompany.mockReturnValue(throwError(() => new Error('Delete Error')));
        component.companies = [...mockCompanies];

        component.deleteCompany(1);

        expect(component.error).toBe('Delete Error');
        expect(component.companies.length).toBe(2); // Não deve remover da lista
    });
});