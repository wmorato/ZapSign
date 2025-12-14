// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\company\services\company.service.spec.ts
import { of, throwError, firstValueFrom } from 'rxjs';
import { CompanyService } from './company.service';
import { ApiService } from '../../../core/services/api.service';
import { Company } from '../../../core/models/company.model';

describe('CompanyService', () => {
    let service: CompanyService;
    let apiServiceMock: any;

    const companyPath = '/api/company/';
    const mockCompany: Company = {
        id: 1,
        name: 'Test Company',
        apiToken: 'test-api-token-123',
        created_at: '2024-01-01',
        last_updated_at: '2024-01-01'
    };

    beforeEach(() => {
        // Mock do ApiService
        apiServiceMock = {
            get: jest.fn(),
            post: jest.fn(),
            put: jest.fn(),
            delete: jest.fn()
        };

        // Criar instância do serviço com mock
        service = new CompanyService(apiServiceMock as ApiService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('getAllCompanies', () => {
        it('should get all companies', async () => {
            const mockCompanies: Company[] = [mockCompany];
            apiServiceMock.get.mockReturnValue(of(mockCompanies));

            const result = await firstValueFrom(service.getAllCompanies());

            expect(result).toEqual(mockCompanies);
            expect(apiServiceMock.get).toHaveBeenCalledWith(companyPath);
        });

        it('should handle errors when getting all companies', async () => {
            const error = new Error('Failed to fetch companies');
            apiServiceMock.get.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.getAllCompanies()))
                .rejects.toThrow('Failed to fetch companies');
        });
    });

    describe('getCompanyById', () => {
        it('should get company by id', async () => {
            const companyId = 1;
            apiServiceMock.get.mockReturnValue(of(mockCompany));

            const result = await firstValueFrom(service.getCompanyById(companyId));

            expect(result).toEqual(mockCompany);
            expect(apiServiceMock.get).toHaveBeenCalledWith(`${companyPath}${companyId}/`);
        });

        it('should handle errors when getting company by id', async () => {
            const companyId = 999;
            const error = new Error('Company not found');
            apiServiceMock.get.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.getCompanyById(companyId)))
                .rejects.toThrow('Company not found');
        });
    });

    describe('createCompany', () => {
        it('should create a new company', async () => {
            const newCompany: Company = {
                name: 'New Company',
                apiToken: 'new-api-token-456'
            } as Company;

            const createdCompany: Company = { ...newCompany, id: 2 } as Company;
            apiServiceMock.post.mockReturnValue(of(createdCompany));

            const result = await firstValueFrom(service.createCompany(newCompany));

            expect(result).toEqual(createdCompany);
            expect(apiServiceMock.post).toHaveBeenCalledWith(companyPath, newCompany);
        });

        it('should handle validation errors when creating company', async () => {
            const invalidCompany = {} as Company;
            const error = new Error('Validation failed');
            apiServiceMock.post.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.createCompany(invalidCompany)))
                .rejects.toThrow('Validation failed');
        });

        it('should handle duplicate name error', async () => {
            const duplicateCompany: Company = {
                name: 'Duplicate Company'
            } as Company;
            const error = new Error('Company name already exists');
            apiServiceMock.post.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.createCompany(duplicateCompany)))
                .rejects.toThrow('Company name already exists');
        });
    });

    describe('updateCompany', () => {
        it('should update an existing company', async () => {
            const companyId = 1;
            const updatedData: Partial<Company> = {
                name: 'Updated Company Name',
                apiToken: 'updated-api-token'
            };
            const updatedCompany: Company = { ...mockCompany, ...updatedData };
            apiServiceMock.put.mockReturnValue(of(updatedCompany));

            const result = await firstValueFrom(
                service.updateCompany(companyId, updatedData as Company)
            );

            expect(result).toEqual(updatedCompany);
            expect(apiServiceMock.put).toHaveBeenCalledWith(
                `${companyPath}${companyId}/`,
                updatedData
            );
        });

        it('should handle errors when updating company', async () => {
            const companyId = 999;
            const error = new Error('Company not found');
            apiServiceMock.put.mockReturnValue(throwError(() => error));

            await expect(
                firstValueFrom(service.updateCompany(companyId, mockCompany))
            ).rejects.toThrow('Company not found');
        });
    });

    describe('deleteCompany', () => {
        it('should delete a company', async () => {
            const companyId = 1;
            const mockResponse = { success: true };
            apiServiceMock.delete.mockReturnValue(of(mockResponse));

            const result = await firstValueFrom(service.deleteCompany(companyId));

            expect(result).toEqual(mockResponse);
            expect(apiServiceMock.delete).toHaveBeenCalledWith(`${companyPath}${companyId}/`);
        });

        it('should handle errors when deleting company', async () => {
            const companyId = 999;
            const error = new Error('Company not found');
            apiServiceMock.delete.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.deleteCompany(companyId)))
                .rejects.toThrow('Company not found');
        });

        it('should handle constraint errors when deleting company with documents', async () => {
            const companyId = 1;
            const error = new Error('Cannot delete company with associated documents');
            apiServiceMock.delete.mockReturnValue(throwError(() => error));

            await expect(firstValueFrom(service.deleteCompany(companyId)))
                .rejects.toThrow('Cannot delete company with associated documents');
        });
    });

    describe('Type safety', () => {
        it('should return typed Company for getCompanyById', async () => {
            apiServiceMock.get.mockReturnValue(of(mockCompany));

            const result = await firstValueFrom(service.getCompanyById(1));

            expect(result).toHaveProperty('id');
            expect(result).toHaveProperty('name');
            expect(result).toHaveProperty('apiToken');
            expect(typeof result.id).toBe('number');
            expect(typeof result.name).toBe('string');
        });

        it('should return typed Company array for getAllCompanies', async () => {
            const mockCompanies = [mockCompany];
            apiServiceMock.get.mockReturnValue(of(mockCompanies));

            const result = await firstValueFrom(service.getAllCompanies());

            expect(Array.isArray(result)).toBe(true);
            expect(result[0]).toHaveProperty('id');
            expect(result[0]).toHaveProperty('name');
            expect(result[0]).toHaveProperty('apiToken');
        });
    });
});