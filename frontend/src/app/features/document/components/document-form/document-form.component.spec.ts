// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-form\document-form.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DocumentFormComponent } from './document-form.component';
import { FormBuilder, ReactiveFormsModule, Validators, FormArray } from '@angular/forms';
import { DocumentService } from '../../services/document.service';
import { ActivatedRoute, Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { Document } from '../../../../core/models/document.model';
import { CommonModule } from '@angular/common';

describe('DocumentFormComponent', () => {
    let component: DocumentFormComponent;
    let fixture: ComponentFixture<DocumentFormComponent>;
    let documentServiceMock: any;
    let routerMock: any;
    let activatedRouteMock: any;
    let consoleErrorSpy: jest.SpyInstance;

    const mockSigner = { name: 'Signatário Teste', email: 'signer@test.com', status: 'new', externalID: 'ext123' };
    const mockDocument: Document = {
        id: 1,
        name: 'Contrato A',
        url_pdf: 'https://test.com/doc.pdf',
        company: 1,
        externalID: 'doc-ext-1',
        signers_db: [{ id: 101, ...mockSigner, token: 's-token-1' }]
    } as Document;

    beforeEach(async () => {
        documentServiceMock = {
            getDocumentById: jest.fn().mockReturnValue(of(mockDocument)),
            createDocument: jest.fn().mockReturnValue(of(mockDocument)),
            updateDocument: jest.fn().mockReturnValue(of(mockDocument))
        };

        routerMock = {
            navigate: jest.fn()
        };

        activatedRouteMock = {
            snapshot: {
                params: {} // Padrão para modo de criação
            }
        };

        await TestBed.configureTestingModule({
            imports: [DocumentFormComponent, ReactiveFormsModule, CommonModule],
            providers: [
                FormBuilder,
                { provide: DocumentService, useValue: documentServiceMock },
                { provide: Router, useValue: routerMock },
                { provide: ActivatedRoute, useValue: activatedRouteMock }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(DocumentFormComponent);
        component = fixture.componentInstance;
        consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => { });
    });

    afterEach(() => {
        consoleErrorSpy.mockRestore();
    });

    it('should create the component', () => {
        fixture.detectChanges();
        expect(component).toBeTruthy();
    });

    it('should initialize with an empty signer in create mode', () => {
        component.ngOnInit();
        const signersArray = component.documentForm.get('signers') as FormArray;

        expect(component.isEditMode).toBeFalsy();
        expect(signersArray.length).toBe(1);
        expect(signersArray.controls[0].get('name')?.value).toBe('');
    });

    // ===================================
    // Gerenciamento de Signatários (FormArray)
    // ===================================
    it('should add a new signer to the form array', () => {
        component.ngOnInit(); // 1 signatário inicial
        component.addSigner();

        const signersArray = component.documentForm.get('signers') as FormArray;
        expect(signersArray.length).toBe(2);
        expect(signersArray.controls[1].get('status')?.value).toBe('new');
    });

    it('should remove a signer from the form array', () => {
        component.ngOnInit(); // 1 signatário inicial
        component.addSigner(); // 2 signatários
        component.removeSigner(0);

        const signersArray = component.documentForm.get('signers') as FormArray;
        expect(signersArray.length).toBe(1);
        expect(signersArray.controls[0].get('name')?.value).toBe(''); // O segundo signatário é agora o primeiro
    });

    it('should require name, url_pdf, and signer fields to be valid', () => {
        component.ngOnInit();

        // Documento inválido (name e url_pdf vazios)
        expect(component.documentForm.valid).toBeFalsy();

        component.documentForm.controls['name'].setValue('Doc Name');
        component.documentForm.controls['url_pdf'].setValue('http://validurl.pdf');

        const signerGroup = (component.documentForm.get('signers') as FormArray).controls[0];
        signerGroup.get('name')?.setValue('Nome Signatário');
        signerGroup.get('email')?.setValue('signer@valido.com');

        expect(component.documentForm.valid).toBeTruthy();
    });

    // ===================================
    // Submissão (Create)
    // ===================================
    it('should call createDocument and navigate on valid create submission', () => {
        component.ngOnInit();
        component.documentForm.controls['name'].setValue('Novo Contrato');
        component.documentForm.controls['url_pdf'].setValue('https://new.com/new.pdf');

        const signerGroup = (component.documentForm.get('signers') as FormArray).controls[0];
        signerGroup.get('name')?.setValue('Signer A');
        signerGroup.get('email')?.setValue('a@signer.com');

        component.onSubmit();

        expect(documentServiceMock.createDocument).toHaveBeenCalled();
        expect(routerMock.navigate).toHaveBeenCalledWith(['/documents']);
        expect(component.successMessage).toBeTruthy();
    });

    it('should display error message on createDocument failure', () => {
        documentServiceMock.createDocument.mockReturnValue(throwError(() => new Error('API Error')));
        component.ngOnInit();

        component.documentForm.controls['name'].setValue('Novo Contrato');
        component.documentForm.controls['url_pdf'].setValue('https://new.com/new.pdf');
        const signerGroup = (component.documentForm.get('signers') as FormArray).controls[0];
        signerGroup.get('name')?.setValue('Signer A');
        signerGroup.get('email')?.setValue('a@signer.com');

        component.onSubmit();

        expect(component.errorMessage).toBe('API Error');
        expect(routerMock.navigate).not.toHaveBeenCalled();
    });

    // ===================================
    // Submissão (Update)
    // ===================================
    describe('Update Mode', () => {
        beforeEach(() => {
            activatedRouteMock.snapshot.params['id'] = 1;
            component.ngOnInit();
            // Simula o carregamento dos dados mockDocument
        });

        it('should initialize in edit mode and load document/signers data', () => {
            expect(component.isEditMode).toBeTruthy();
            expect(documentServiceMock.getDocumentById).toHaveBeenCalledWith(1);
            expect(component.documentForm.controls['name'].value).toBe(mockDocument.name);
            expect(component.signers.length).toBe(1);
            expect(component.signers.controls[0].get('id')?.value).toBe(101);
        });

        it('should call updateDocument on edit submission', () => {
            component.documentForm.controls['name'].setValue('Contrato B');
            component.onSubmit();

            expect(documentServiceMock.updateDocument).toHaveBeenCalledWith(1, expect.objectContaining({
                name: 'Contrato B',
                signers: expect.any(Array)
            }));
        });

        it('should include signers_to_remove when a signer is removed in edit mode', () => {
            // Documento carrega 1 signatário: id: 101
            component.removeSigner(0); // Remove o único signatário

            component.onSubmit();

            const payloadSent = documentServiceMock.updateDocument.mock.calls[0][1];
            expect(payloadSent.signers_to_remove).toEqual([101]); // O ID 101 deve ser removido
            expect(payloadSent.signers.length).toBe(0); // Nenhum signatário na lista atual
        });

        it('should not include signers_to_remove when no signers were removed', () => {
            // Documento carrega 1 signatário: id: 101
            // Apenas atualiza o nome
            component.documentForm.controls['name'].setValue('Contrato C');
            component.signers.controls[0].get('name')?.setValue('Signer Z');

            component.onSubmit();

            const payloadSent = documentServiceMock.updateDocument.mock.calls[0][1];
            expect(payloadSent.signers_to_remove).toBeUndefined();
            expect(payloadSent.signers.length).toBe(1);
        });
    });

    // ===================================
    // Outras Ações
    // ===================================
    it('should navigate to documents list on cancel', () => {
        component.onCancel();
        expect(routerMock.navigate).toHaveBeenCalledWith(['/documents']);
    });
});