// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\auth\login\login.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoginComponent } from './login.component';
import { ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../core/auth/auth.service';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { CommonModule } from '@angular/common';

describe('LoginComponent', () => {
    let component: LoginComponent;
    let fixture: ComponentFixture<LoginComponent>;
    let authServiceMock: any;
    let routerMock: any;

    beforeEach(async () => {
        authServiceMock = {
            isAuthenticated: jest.fn().mockReturnValue(false),
            login: jest.fn()
        };

        routerMock = {
            navigate: jest.fn()
        };

        await TestBed.configureTestingModule({
            imports: [LoginComponent, ReactiveFormsModule, CommonModule],
            providers: [
                { provide: AuthService, useValue: authServiceMock },
                { provide: Router, useValue: routerMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(LoginComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create the component', () => {
        expect(component).toBeTruthy();
    });

    it('should initialize with an invalid form', () => {
        expect(component.loginForm.valid).toBeFalsy();
    });

    it('should validate email format', () => {
        const email = component.loginForm.controls['email'];
        email.setValue('invalid-email');
        expect(email.hasError('email')).toBeTruthy();

        email.setValue('test@test.com');
        expect(email.hasError('email')).toBeFalsy();
    });

    it('should show error message if form is submitted with empty fields', () => {
        component.onSubmit();
        expect(component.errorMessage).toBe('Por favor, preencha todos os campos corretamente.');
    });

    it('should call authService.login and navigate on success', () => {
        authServiceMock.login.mockReturnValue(of(true));

        component.loginForm.controls['email'].setValue('gerente@empresa.com');
        component.loginForm.controls['password'].setValue('123456');

        component.onSubmit();

        expect(authServiceMock.login).toHaveBeenCalledWith('gerente@empresa.com', '123456');
        // Nota: O redirecionamento real ocorre dentro do AuthService.login (map), 
        // mas o componente gerencia o estado de sucesso.
    });

    it('should display error message on invalid credentials', () => {
        authServiceMock.login.mockReturnValue(of(false));

        component.loginForm.controls['email'].setValue('wrong@test.com');
        component.loginForm.controls['password'].setValue('wrongpass');

        component.onSubmit();

        expect(component.errorMessage).toBe('Credenciais inválidas. Por favor, tente novamente.');
    });

    it('should handle HTTP error during login', () => {
        // Silencia o console.error para o teste ficar limpo
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

        authServiceMock.login.mockReturnValue(throwError(() => new Error('Server Error')));

        component.loginForm.controls['email'].setValue('test@test.com');
        component.loginForm.controls['password'].setValue('password');

        component.onSubmit();

        expect(component.errorMessage).toContain('Ocorreu um erro ao tentar fazer login');

        consoleSpy.mockRestore();
    });

    it('should redirect to dashboard if already authenticated', () => {
        authServiceMock.isAuthenticated.mockReturnValue(true);

        // Simula nova inicialização para testar o ngOnInit
        component.ngOnInit();

        expect(routerMock.navigate).toHaveBeenCalledWith(['/dashboard']);
    });
});