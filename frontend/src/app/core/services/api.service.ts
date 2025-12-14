// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\services\api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  private formatErrors(error: HttpErrorResponse): Observable<never> {
    console.error('API Error:', error);
    let errorMessage = 'Ocorreu um erro desconhecido.';
    if (error.error instanceof ErrorEvent) {
      // Erro do lado do cliente
      errorMessage = `Erro: ${error.error.message}`;
    } else if (error.status) {
      // Erro do lado do servidor
      errorMessage = `Erro ${error.status}: ${error.statusText || ''} - ${error.error?.message || error.message}`;
      if (error.error && typeof error.error === 'object') {
        // Se o backend retornar um objeto de erro mais detalhado
        errorMessage = error.error.message || JSON.stringify(error.error);
      }
    }
    return throwError(() => new Error(errorMessage));
  }

  get<T>(path: string, params: any = {}): Observable<T> {
    return this.http.get<T>(`${this.apiUrl}${path}`, { params }).pipe(catchError(this.formatErrors));
  }

  post<T>(path: string, body: Object = {}): Observable<T> {
    return this.http.post<T>(`${this.apiUrl}${path}`, body).pipe(catchError(this.formatErrors));
  }

  put<T>(path: string, body: Object = {}): Observable<T> {
    return this.http.put<T>(`${this.apiUrl}${path}`, body).pipe(catchError(this.formatErrors));
  }

  patch<T>(path: string, body: Object = {}): Observable<T> {
    return this.http.patch<T>(`${this.apiUrl}${path}`, body).pipe(catchError(this.formatErrors));
  }

  delete<T>(path: string): Observable<T> {
    return this.http.delete<T>(`${this.apiUrl}${path}`).pipe(catchError(this.formatErrors));
  }
}