// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\auth\auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators'; // Importe 'map'
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

@Injectable({
    providedIn: 'root'
})
@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private readonly ACCESS_TOKEN_KEY = 'access_token';
    private readonly REFRESH_TOKEN_KEY = 'refresh_token';
    private _isAuthenticated = new BehaviorSubject<boolean>(this.hasToken());

    isAuthenticated$ = this._isAuthenticated.asObservable();

    constructor(private http: HttpClient, private router: Router) { }

    private hasToken(): boolean {
        return !!localStorage.getItem(this.ACCESS_TOKEN_KEY);
    }

    getToken(): string | null {
        return localStorage.getItem(this.ACCESS_TOKEN_KEY);
    }

    private setTokens(access: string, refresh: string): void {
        localStorage.setItem(this.ACCESS_TOKEN_KEY, access);
        localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh);
        this._isAuthenticated.next(true);
    }

    private removeTokens(): void {
        localStorage.removeItem(this.ACCESS_TOKEN_KEY);
        localStorage.removeItem(this.REFRESH_TOKEN_KEY);
        this._isAuthenticated.next(false);
    }

    login(email: string, password: string): Observable<boolean> {
        return this.http.post<{ access: string; refresh: string }>(`${environment.apiUrl}/auth/login/`, {
            username: email, // SimpleJWT uses 'username' by default, or we can configure it. Let's send username=email.
            password: password
        }).pipe(
            map(response => {
                if (response.access && response.refresh) {
                    this.setTokens(response.access, response.refresh);
                    this.router.navigate(['/dashboard']);
                    return true;
                } else {
                    return false;
                }
            }),
            catchError((error: HttpErrorResponse) => {
                console.error('Login error:', error);
                this.removeTokens();
                return of(false);
            })
        );
    }

    logout(): void {
        this.removeTokens();
        this.router.navigate(['/login']);
    }

    isAuthenticated(): boolean {
        return this.hasToken();
    }
}