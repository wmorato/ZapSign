// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\dashboard\dashboard.component.ts
import { Component, OnInit, inject } from '@angular/core';
import { AuthService } from '../../core/auth/auth.service';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FeedbackModalComponent } from '../../core/components/feedback-modal/feedback-modal.component'; // <--- ADICIONADO

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, RouterLink, FeedbackModalComponent], // <--- ADICIONADO FeedbackModalComponent
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
    private authService = inject(AuthService);
    userName: string = 'Usuário';
    userEmail: string = ''; // <--- NOVO
    showFeedbackModal: boolean = false; // <--- NOVO

    ngOnInit(): void {
        const token = this.authService.getToken();
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                this.userName = payload.username.split('@')[0];
                this.userEmail = payload.username; // O username é o email
            } catch (e) {
                this.userName = 'Usuário';
                this.userEmail = 'email@naoencontrado.com';
            }
        }
    }

    openFeedbackModal(): void { // <--- NOVO
        this.showFeedbackModal = true;
    }

    closeFeedbackModal(): void { // <--- NOVO
        this.showFeedbackModal = false;
    }

    logout(): void {
        this.authService.logout();
    }
}