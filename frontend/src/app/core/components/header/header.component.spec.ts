// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\components\header\header.component.spec.ts
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HeaderComponent } from './header.component';
import { AuthService } from '../../auth/auth.service';
import { DocumentService } from '../../../features/document/services/document.service';
import { RouterLink, RouterLinkActive, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { of, BehaviorSubject } from 'rxjs';
import { Document } from '../../models/document.model';

describe('HeaderComponent', () => {
    let component: HeaderComponent;
    let fixture: ComponentFixture<HeaderComponent>;
    let authServiceMock: any;
    let documentServiceMock: any;
    let dateMock: jest.SpyInstance;
    let intervalSpy: jest.SpyInstance;

    const MOCK_TOKEN_PAYLOAD = btoa(JSON.stringify({ username: 'gerente_a@corp.com' }));
    const MOCK_JWT = `header.${MOCK_TOKEN_PAYLOAD}.signature`;

    const mockDocuments: Document[] = [
        { id: 1, status: 'pending' } as Document,
        { id: 2, status: 'new' } as Document,
        { id: 3, status: 'signed' } as Document,
    ];

    beforeEach(async () => {
        const isAuthenticatedSubject = new BehaviorSubject(true);

        authServiceMock = {
            isAuthenticated$: isAuthenticatedSubject.asObservable(),
            getToken: jest.fn().mockReturnValue(MOCK_JWT),
            logout: jest.fn()
        };

        documentServiceMock = {
            getAllDocuments: jest.fn().mockReturnValue(of(mockDocuments)),
        };

        const activatedRouteMock = {
            snapshot: {
                params: {}
            }
        };

        const MOCK_DATE = new Date('2024-03-10T12:00:00Z');
        dateMock = jest.spyOn(global, 'Date').mockImplementation(() => MOCK_DATE as any);
        intervalSpy = jest.spyOn(require('rxjs'), 'interval').mockReturnValue(of(0));

        await TestBed.configureTestingModule({
            imports: [HeaderComponent, CommonModule, RouterLink, RouterLinkActive],
            providers: [
                { provide: AuthService, useValue: authServiceMock },
                { provide: DocumentService, useValue: documentServiceMock },
                { provide: ActivatedRoute, useValue: activatedRouteMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(HeaderComponent);
        component = fixture.componentInstance;
    });

    afterEach(() => {
        dateMock.mockRestore();
        intervalSpy.mockRestore();
        jest.restoreAllMocks();
    });

    describe('Inicialização e Dados do Usuário', () => {



        it('should render navbar when authenticated is true', fakeAsync(() => {
            component.isAuthenticated$ = of(true);
            fixture.detectChanges();
            const nav = fixture.nativeElement.querySelector('nav.navbar');
            expect(nav).not.toBeNull();
        }));


    });

    describe('Lógica de Notificação e Polling', () => {

        it('should calculate correct pending documents count on load (2 pending/new)', fakeAsync(() => {
            fixture.detectChanges();
            tick(0);

            component.pendingDocumentsCount$.subscribe(count => {
                expect(count).toBe(2);
            });
        }));



        it('should show badge when pending count is > 0', fakeAsync(() => {
            fixture.detectChanges();
            tick(0);
            fixture.detectChanges();
            const badge = fixture.nativeElement.querySelector('.badge');
            expect(badge).not.toBeNull();
            expect(badge.textContent).toBe('2');
        }));

        it('should NOT show badge when pending count is 0', fakeAsync(() => {
            documentServiceMock.getAllDocuments.mockReturnValue(of([]));
            fixture.detectChanges();
            tick(0);
            fixture.detectChanges();
            const badge = fixture.nativeElement.querySelector('.badge');
            expect(badge).toBeNull();
        }));
    });


});