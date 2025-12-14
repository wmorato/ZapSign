// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\components\feedback-modal\feedback-modal.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FeedbackModalComponent } from './feedback-modal.component';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { CommonModule } from '@angular/common';

describe('FeedbackModalComponent', () => {
    let component: FeedbackModalComponent;
    let fixture: ComponentFixture<FeedbackModalComponent>;
    let consoleLogSpy: jest.SpyInstance;

    const MOCK_USER_NAME = 'Gerente Teste';
    const MOCK_USER_EMAIL = 'gerente.teste@corp.com';

    beforeEach(async () => {
        consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => { });

        await TestBed.configureTestingModule({
            imports: [FeedbackModalComponent, CommonModule, ReactiveFormsModule],
            providers: [FormBuilder]
        }).compileComponents();

        fixture = TestBed.createComponent(FeedbackModalComponent);
        component = fixture.componentInstance;

        // Simula os Inputs do Dashboard
        component.userName = MOCK_USER_NAME;
        component.userEmail = MOCK_USER_EMAIL;

        fixture.detectChanges(); // Chama ngOnInit
    });

    afterEach(() => {
        consoleLogSpy.mockRestore();
        jest.restoreAllMocks();
    });

    // --- GRUPO 1: Inicialização e Props (4 testes) ---

    it('1. should create the component and initialize the form', () => {
        expect(component).toBeTruthy();
        expect(component.feedbackForm).toBeDefined();
        expect(component.isSubmitted).toBe(false);
    });

    it('2. should initialize form with userName and userEmail (disabled)', () => {
        expect(component.feedbackForm.get('name')?.value).toBe(MOCK_USER_NAME);
        expect(component.feedbackForm.get('name')?.disabled).toBe(true);
        expect(component.feedbackForm.get('email')?.value).toBe(MOCK_USER_EMAIL);
        expect(component.feedbackForm.get('email')?.disabled).toBe(true);
    });

    it('3. should initialize contactType to "Elogio"', () => {
        expect(component.feedbackForm.get('contactType')?.value).toBe('Elogio');
    });

    it('4. should be invalid if message is missing or too short', () => {
        const messageControl = component.feedbackForm.get('message');
        messageControl?.setValue('');
        expect(messageControl?.valid).toBeFalsy();

        messageControl?.setValue('short');
        expect(messageControl?.valid).toBeFalsy();
        expect(messageControl?.hasError('minlength')).toBe(true);
    });

    // --- GRUPO 2: Ações do Modal (5 testes) ---

    it('5. should emit closeModal on onClose button click', () => {
        const closeSpy = jest.spyOn(component.closeModal, 'emit');
        component.onClose();
        expect(closeSpy).toHaveBeenCalled();
    });

    it('6. should NOT submit if form is invalid and mark all as touched', () => {
        const messageControl = component.feedbackForm.get('message');
        messageControl?.setValue('short'); // Inválido (minlength 10)

        component.onSubmit();

        expect(component.isSubmitted).toBe(false);
        expect(messageControl?.touched).toBe(true);
        expect(consoleLogSpy).not.toHaveBeenCalled();
    });

    it('7. should process submit, set isSubmitted to true and log feedback data on success', () => {
        const messageControl = component.feedbackForm.get('message');
        messageControl?.setValue('Esta é uma mensagem de feedback válida e completa.');

        component.onSubmit();

        expect(component.isSubmitted).toBe(true);
        expect(consoleLogSpy).toHaveBeenCalledWith('Feedback Enviado (Simulado):', {
            name: MOCK_USER_NAME,
            email: MOCK_USER_EMAIL,
            type: 'Elogio',
            message: 'Esta é uma mensagem de feedback válida e completa.'
        });
    });

    it('8. should display success message and close button after successful submission', () => {
        component.isSubmitted = true;
        fixture.detectChanges(); // Renderiza o estado de submissão

        const successMessage = fixture.nativeElement.querySelector('.success-message');
        expect(successMessage).not.toBeNull();
        expect(successMessage.textContent).toContain('Agradecemos o seu contato!');

        const closeButton = successMessage.querySelector('.btn-primary');
        expect(closeButton).not.toBeNull();
    });

    it('9. should enable submit button when form is valid', () => {
        const messageControl = component.feedbackForm.get('message');
        messageControl?.setValue('Mensagem longa o suficiente para ser válida.');

        fixture.detectChanges();

        const submitButton = fixture.nativeElement.querySelector('button[type="submit"]');
        expect(submitButton.disabled).toBe(false);
    });
});