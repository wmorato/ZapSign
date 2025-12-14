// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\app.ts
import { Component, inject } from '@angular/core'; // Importe 'inject'
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router'; // Importe RouterLink e RouterLinkActive
import { CommonModule } from '@angular/common';
import { AuthService } from './core/auth/auth.service'; // Importe AuthService
import { HeaderComponent } from './core/components/header/header.component'; // <--- ADICIONADO

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, HeaderComponent], // <--- ADICIONADO HeaderComponent
  templateUrl: './app.component.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = 'frontend-app';

}