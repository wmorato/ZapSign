// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\components\feedback-modal\feedback-modal.component.ts
import { Component, OnInit, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-feedback-modal',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './feedback-modal.component.html',
  styleUrls: ['./feedback-modal.component.scss']
})
export class FeedbackModalComponent implements OnInit {
  @Input() userName: string = '';
  @Input() userEmail: string = '';
  @Output() closeModal = new EventEmitter<void>();

  feedbackForm!: FormGroup; // <--- CORREÇÃO: Adicionado operador de asserção de atribuição definitiva (!)
  isSubmitted = false;
  
  private fb = inject(FormBuilder);

  ngOnInit(): void {
    this.feedbackForm = this.fb.group({
      // O estado 'disabled' é um booleano, não uma string.
      // O Angular Reactive Forms gerencia o disabled via objeto de valor.
      name: [{ value: this.userName, disabled: true }, Validators.required],
      email: [{ value: this.userEmail, disabled: true }, [Validators.required, Validators.email]],
      contactType: ['Elogio', Validators.required],
      message: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  onSubmit(): void {
    if (this.feedbackForm.valid) {
      // Simulação de envio de feedback
      const feedbackData = {
        name: this.userName,
        email: this.userEmail,
        type: this.feedbackForm.get('contactType')?.value,
        message: this.feedbackForm.get('message')?.value
      };

      console.log('Feedback Enviado (Simulado):', feedbackData);
      
      // Define o estado de submissão para exibir a mensagem de sucesso
      this.isSubmitted = true;
      
      // Opcional: Fechar o modal após alguns segundos
      // setTimeout(() => this.closeModal.emit(), 5000);
    } else {
      this.feedbackForm.markAllAsTouched();
    }
  }

  onClose(): void {
    this.closeModal.emit();
  }
}