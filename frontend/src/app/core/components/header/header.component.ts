// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\components\header\header.component.ts
import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';
import { DocumentService } from '../../../features/document/services/document.service';
import { Subscription, interval, Observable, of } from 'rxjs';
import { switchMap, startWith, map } from 'rxjs/operators';
import { Document } from '../../models/document.model';
import { NotificationPanelComponent } from '../notification-panel/notification-panel.component'; // <--- ADICIONADO

@Component({
    selector: 'app-header',
    standalone: true,
    imports: [CommonModule, RouterLink, RouterLinkActive, NotificationPanelComponent], // <--- ADICIONADO NotificationPanelComponent
    templateUrl: './header.component.html',
    styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit, OnDestroy {
    private authService = inject(AuthService);
    private documentService = inject(DocumentService);

    isAuthenticated$ = this.authService.isAuthenticated$;
    userName: string = 'Usuário';
    currentDateTime: Date = new Date();
    pendingDocumentsCount$: Observable<number> = of(0);
    private intervalSubscription: Subscription | null = null;

    showNotificationPanel: boolean = false; // <--- NOVO: Estado do painel

    ngOnInit(): void {
        // Simula a obtenção do nome do usuário (o email é usado como username)
        // Em um sistema real, isso viria de um endpoint de perfil.
        const token = this.authService.getToken();
        if (token) {
            // Lógica simplificada para extrair o username do token (se for JWT)
            // Em um sistema real, o backend enviaria o nome completo.
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                this.userName = payload.username.split('@')[0]; // Ex: 'gerente_a'
            } catch (e) {
                this.userName = 'Usuário';
            }
        }

        // Atualiza a data e hora a cada segundo
        this.intervalSubscription = interval(1000).subscribe(() => {
            this.currentDateTime = new Date();
        });

        // Polling para o contador de documentos pendentes (a cada 30 segundos)
        this.pendingDocumentsCount$ = interval(30000).pipe(
            startWith(0), // Inicia imediatamente
            switchMap(() => this.documentService.getAllDocuments().pipe(
                map((documents: Document[]) => {
                    // Conta documentos com status 'pending' ou 'new'
                    return documents.filter(doc => doc.status === 'pending' || doc.status === 'new').length;
                })
            ))
        );
    }

    ngOnDestroy(): void {
        this.intervalSubscription?.unsubscribe();
    }

    logout(): void {
        this.authService.logout();
    }

    toggleNotificationPanel(): void { // <--- NOVO MÉTODO
        this.showNotificationPanel = !this.showNotificationPanel;
    }
}