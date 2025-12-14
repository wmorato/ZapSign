import { HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { of, throwError } from 'rxjs';

import { AuthInterceptor } from './auth-interceptor';
import { AuthService } from '../auth/auth.service';

describe('AuthInterceptor', () => {
  let interceptor: AuthInterceptor;
  let authServiceMock: any;
  let handlerMock: HttpHandler;

  // CORREÇÃO: Adicionando tipo genérico para HttpRequest<any> para métodos sem body
  const createRequest = (url = '/api/test') =>
    new HttpRequest<any>('GET', url);

  beforeEach(() => {
    authServiceMock = {
      getToken: jest.fn()
    };

    handlerMock = {
      handle: jest.fn().mockReturnValue(of({} as HttpEvent<any>))
    };

    interceptor = new AuthInterceptor(authServiceMock as AuthService);
  });

  it('should be created', () => {
    expect(interceptor).toBeTruthy();
  });

  it('should not add Authorization header when token is null', () => {
    authServiceMock.getToken.mockReturnValue(null);

    const req = createRequest();
    interceptor.intercept(req, handlerMock).subscribe();

    const handledReq = (handlerMock.handle as any).mock.calls[0][0];
    expect(handledReq.headers.has('Authorization')).toBe(false);
  });

  it('should not add Authorization header when token is undefined', () => {
    authServiceMock.getToken.mockReturnValue(undefined);

    const req = createRequest();
    interceptor.intercept(req, handlerMock).subscribe();

    const handledReq = (handlerMock.handle as any).mock.calls[0][0];
    expect(handledReq.headers.has('Authorization')).toBe(false);
  });

  it('should pass request unchanged when no token', () => {
    authServiceMock.getToken.mockReturnValue(null);

    const req = createRequest('/api/unchanged');
    interceptor.intercept(req, handlerMock).subscribe();

    const handledReq = (handlerMock.handle as any).mock.calls[0][0];
    expect(handledReq.url).toBe('/api/unchanged');
  });

  it('should call handler.handle exactly once', () => {
    authServiceMock.getToken.mockReturnValue(null);

    const req = createRequest();
    interceptor.intercept(req, handlerMock).subscribe();

    expect((handlerMock.handle as any).mock.calls.length).toBe(1);
  });

  // CORREÇÃO: Adiciona `null` ou `{}` como corpo para o método POST
  it('should preserve request method', () => {
    authServiceMock.getToken.mockReturnValue(null);

    // Necessário definir o corpo (3º parâmetro) para o método POST/PUT/PATCH
    const req = new HttpRequest<any>('POST', '/api/post', {}); 
    interceptor.intercept(req, handlerMock).subscribe();

    const handledReq = (handlerMock.handle as any).mock.calls[0][0];
    expect(handledReq.method).toBe('POST');
  });

  it('should preserve request body', () => {
    authServiceMock.getToken.mockReturnValue(null);

    const body = { test: true };
    // Necessário definir o tipo genérico e o corpo
    const req = new HttpRequest<typeof body>('POST', '/api/post', body);
    interceptor.intercept(req, handlerMock).subscribe();

    const handledReq = (handlerMock.handle as any).mock.calls[0][0];
    expect(handledReq.body).toEqual(body);
  });

  it('should work with different URLs', () => {
    authServiceMock.getToken.mockReturnValue(null);

    const req = createRequest('/auth/login');
    interceptor.intercept(req, handlerMock).subscribe();

    const handledReq = (handlerMock.handle as any).mock.calls[0][0];
    expect(handledReq.url).toBe('/auth/login');
  });

  it('should return observable from handler', () => {
    authServiceMock.getToken.mockReturnValue(null);

    const req = createRequest();
    const result$ = interceptor.intercept(req, handlerMock);

    expect(result$).toBeDefined();
  });

  it('should support multiple consecutive calls', () => {
    authServiceMock.getToken.mockReturnValue(null);

    interceptor.intercept(createRequest('/1'), handlerMock).subscribe();
    interceptor.intercept(createRequest('/2'), handlerMock).subscribe();

    expect((handlerMock.handle as any).mock.calls.length).toBe(2);
  });

  it('should not mutate original request headers', () => {
    authServiceMock.getToken.mockReturnValue(null);

    const req = createRequest();
    interceptor.intercept(req, handlerMock).subscribe();

    expect(req.headers.has('Authorization')).toBe(false);
  });

  it('should handle empty string token as no token', () => {
    authServiceMock.getToken.mockReturnValue('');

    const req = createRequest();
    interceptor.intercept(req, handlerMock).subscribe();

    const handledReq = (handlerMock.handle as any).mock.calls[0][0];
    expect(handledReq.headers.has('Authorization')).toBe(false);
  });

  it('should not block request if handler throws error', () => {
    handlerMock.handle = jest.fn().mockReturnValue(
      throwError(() => new Error('Handler error'))
    );

    const req = createRequest();

    expect(() =>
      interceptor.intercept(req, handlerMock).subscribe({
        error: () => { }
      })
    ).not.toThrow();
  });
});