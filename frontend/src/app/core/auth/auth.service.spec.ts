import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

describe('AuthService', () => {
    let service: AuthService;
    let routerMock: jest.Mocked<Router>;

    const mockAccessToken = 'fake-access-token';
    const mockLoginPayload = {
        username: 'test@test.com',
        password: '123456'
    };

    beforeEach(() => {
        routerMock = {
            navigate: jest.fn()
        } as any;

        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [
                AuthService,
                { provide: Router, useValue: routerMock }
            ]
        });

        service = TestBed.inject(AuthService);
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    // =========================
    // Básico
    // =========================
    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    // =========================
    // getToken
    // =========================
    describe('getToken', () => {
        it('should return token when available', () => {
            jest.spyOn(service, 'getToken').mockReturnValue(mockAccessToken);

            const token = service.getToken();

            expect(token).toBe(mockAccessToken);
        });

        it('should return null when no token exists', () => {
            jest.spyOn(service, 'getToken').mockReturnValue(null);

            const token = service.getToken();

            expect(token).toBeNull();
        });
    });

    // =========================
    // login
    // =========================
    describe('login', () => {
        // CORREÇÃO: Passando username e password separadamente
        it('should return true when login succeeds', (done) => {
            jest.spyOn(service, 'login').mockReturnValue(of(true));

            service.login(mockLoginPayload.username, mockLoginPayload.password).subscribe(result => {
                expect(result).toBe(true);
                done();
            });
        });

        // CORREÇÃO: Passando username e password separadamente
        it('should return false when login fails', (done) => {
            jest.spyOn(service, 'login').mockReturnValue(of(false));

            service.login(mockLoginPayload.username, mockLoginPayload.password).subscribe(result => {
                expect(result).toBe(false);
                done();
            });
        });
    });

    // =========================
    // logout
    // =========================
    describe('logout', () => {
        it('should navigate to login page', () => {
            service.logout();

            expect(routerMock.navigate).toHaveBeenCalledWith(['/login']);
        });
    });

    // =========================
    // isAuthenticated
    // =========================
    describe('isAuthenticated', () => {
        it('should return false when token does not exist', () => {
            jest.spyOn(service, 'getToken').mockReturnValue(null);

            const result = service.isAuthenticated();

            expect(result).toBe(false);
        });
    });
});