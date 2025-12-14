import { TestBed } from '@angular/core/testing';
import { ApiService } from './api.service';
import {
    HttpClientTestingModule,
    HttpTestingController
} from '@angular/common/http/testing';

describe('ApiService', () => {
    let service: ApiService;
    let httpMock: HttpTestingController;

    const testPath = '/api/test';
    const mockResponse = { success: true };

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [ApiService]
        });

        service = TestBed.inject(ApiService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpMock.verify();
    });

    // =========================
    // Básico
    // =========================
    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    // =========================
    // GET
    // =========================
    it('should perform GET request and return data', () => {
        service.get(testPath).subscribe(response => {
            expect(response).toEqual(mockResponse);
        });

        const req = httpMock.expectOne(
            request => request.url.endsWith(testPath)
        );

        expect(req.request.method).toBe('GET');
        req.flush(mockResponse);
    });

    // =========================
    // POST
    // =========================
    it('should perform POST request and return data', () => {
        service.post(testPath, mockResponse).subscribe(response => {
            expect(response).toEqual(mockResponse);
        });

        const req = httpMock.expectOne(
            request => request.url.endsWith(testPath)
        );

        expect(req.request.method).toBe('POST');
        req.flush(mockResponse);
    });

    // =========================
    // PUT
    // =========================
    it('should perform PUT request and return data', () => {
        service.put(testPath, mockResponse).subscribe(response => {
            expect(response).toEqual(mockResponse);
        });

        const req = httpMock.expectOne(
            request => request.url.endsWith(testPath)
        );

        expect(req.request.method).toBe('PUT');
        req.flush(mockResponse);
    });

    // =========================
    // DELETE
    // =========================
    it('should perform DELETE request and return data', () => {
        service.delete(testPath).subscribe(response => {
            expect(response).toEqual(mockResponse);
        });

        const req = httpMock.expectOne(
            request => request.url.endsWith(testPath)
        );

        expect(req.request.method).toBe('DELETE');
        req.flush(mockResponse);
    });

    // =========================
    // Testes de Propagação de Erro (Console Silenciado)
    // =========================
    describe('Error Propagation', () => {
        let errorSpy: jest.SpyInstance;

        beforeAll(() => {
            // Silencia o console.error que é chamado dentro do formatErrors do ApiService
            errorSpy = jest.spyOn(console, 'error').mockImplementation(() => { });
        });

        afterAll(() => {
            // Restaura o console.error original
            errorSpy.mockRestore();
        });

        it('should propagate GET error', () => {
            service.get(testPath).subscribe({
                next: () => fail('Expected error'),
                error: err => expect(err).toBeInstanceOf(Error)
            });

            const req = httpMock.expectOne(
                request => request.url.endsWith(testPath)
            );

            req.flush(
                { message: 'GET error' },
                { status: 500, statusText: 'Server Error' }
            );
        });

        it('should propagate POST error', () => {
            service.post(testPath, mockResponse).subscribe({
                next: () => fail('Expected error'),
                error: err => expect(err).toBeInstanceOf(Error)
            });

            const req = httpMock.expectOne(
                request => request.url.endsWith(testPath)
            );

            req.flush(
                { message: 'POST error' },
                { status: 400, statusText: 'Bad Request' }
            );
        });

        it('should propagate PUT error', () => {
            service.put(testPath, mockResponse).subscribe({
                next: () => fail('Expected error'),
                error: err => expect(err).toBeInstanceOf(Error)
            });

            const req = httpMock.expectOne(
                request => request.url.endsWith(testPath)
            );

            req.flush(
                { message: 'PUT error' },
                { status: 500, statusText: 'Server Error' }
            );
        });

        it('should propagate DELETE error', () => {
            service.delete(testPath).subscribe({
                next: () => fail('Expected error'),
                error: err => expect(err).toBeInstanceOf(Error)
            });

            const req = httpMock.expectOne(
                request => request.url.endsWith(testPath)
            );

            req.flush(
                { message: 'DELETE error' },
                { status: 500, statusText: 'Server Error' }
            );
        });
    });
});