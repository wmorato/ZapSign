// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\dashboard\dashboard.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DashboardComponent } from './dashboard.component';
import { AuthService } from '../../core/auth/auth.service';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FeedbackModalComponent } from '../../core/components/feedback-modal/feedback-modal.component';

describe('DashboardComponent', () => {
    let component: DashboardComponent;
    let fixture: ComponentFixture<DashboardComponent>;
    let authServiceMock: any;

    const MOCK_TOKEN_PAYLOAD = btoa(JSON.stringify({ username: 'gerente_a@corp.com' }));
    const MOCK_JWT = `header.${MOCK_TOKEN_PAYLOAD}.signature`;

    beforeEach(async () => {
        authServiceMock = {
            getToken: jest.fn().mockReturnValue(MOCK_JWT),
            logout: jest.fn()
        };

        const activatedRouteMock = {
            snapshot: {
                params: {}
            }
        };

        await TestBed.configureTestingModule({
            imports: [DashboardComponent, CommonModule, RouterLink, FeedbackModalComponent],
            providers: [
                { provide: AuthService, useValue: authServiceMock },
                { provide: ActivatedRoute, useValue: activatedRouteMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(DashboardComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    describe('Inicialização e Dados do Usuário', () => {

        it('should create DashboardComponent', () => {
            expect(component).toBeTruthy();
        });

        it('should correctly extract userName from JWT on init', () => {
            expect(component.userName).toBe('gerente_a');
        });

        it('should correctly extract userEmail from JWT on init', () => {
            expect(component.userEmail).toBe('gerente_a@corp.com');
        });

        it('should set default userName/Email if token is malformed', () => {
            authServiceMock.getToken.mockReturnValue('malformed.token');
            component.ngOnInit();
            expect(component.userName).toBe('Usuário');
            expect(component.userEmail).toBe('email@naoencontrado.com');
        });
    });

    describe('Lógica do Modal de Feedback', () => {

        it('should initialize showFeedbackModal to false', () => {
            expect(component.showFeedbackModal).toBe(false);
        });

        it('should set showFeedbackModal to true on openFeedbackModal()', () => {
            component.openFeedbackModal();
            expect(component.showFeedbackModal).toBe(true);
        });

        it('should set showFeedbackModal to false on closeFeedbackModal()', () => {
            component.showFeedbackModal = true;
            component.closeFeedbackModal();
            expect(component.showFeedbackModal).toBe(false);
        });

        it('should render FeedbackModalComponent when showFeedbackModal is true', () => {
            component.openFeedbackModal();
            fixture.detectChanges();
            const modal = fixture.nativeElement.querySelector('app-feedback-modal');
            expect(modal).not.toBeNull();
        });

        it('should pass correct inputs (userName/userEmail) to FeedbackModalComponent', () => {
            component.openFeedbackModal();
            fixture.detectChanges();
            const modalComponent = fixture.debugElement.children.find(el => el.name === 'app-feedback-modal')?.componentInstance;

            expect(modalComponent.userName).toBe('gerente_a');
            expect(modalComponent.userEmail).toBe('gerente_a@corp.com');
        });
    });
});