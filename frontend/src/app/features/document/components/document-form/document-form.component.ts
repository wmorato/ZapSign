// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\features\document\components\document-form\document-form.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray, ReactiveFormsModule, AbstractControl, ValidationErrors } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { DocumentService } from '../../services/document.service';
import { Document } from '../../../../core/models/document.model';
import { Signer } from '../../../../core/models/signer.model';
import { CommonModule } from '@angular/common';

// Validador customizado: Pelo menos um campo deve ser preenchido (url_pdf ou base64_pdf)
function urlOrFileRequiredValidator(control: AbstractControl): ValidationErrors | null {
  const url = control.get('url_pdf')?.value;
  const base64 = control.get('base64_pdf')?.value;

  // Se a URL ou Base64 estiver preenchido, é válido.
  if (url || base64) {
    return null;
  }

  // Se nenhum estiver preenchido, retorna erro
  return { urlOrFileRequired: true };
}


@Component({
  selector: 'app-document-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './document-form.component.html',
  styleUrls: ['./document-form.component.scss']
})
export class DocumentFormComponent implements OnInit {
  documentForm: FormGroup;
  isEditMode = false;
  documentId: number | null = null;
  errorMessage: string | null = null;
  successMessage: string | null = null;
  maxFileSizeMB = 10;

  // Armazenar signatários originais para identificar remoções
  private originalSigners: Signer[] = [];

  constructor(
    private fb: FormBuilder,
    private documentService: DocumentService,
    // CompanyService removido pois não precisamos mais listar empresas
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.documentForm = this.fb.group({
      name: ['', Validators.required],
      // Campo 'company' removido. O Backend infere pelo usuário logado.
      url_pdf: [''], // URL do PDF
      base64_pdf: [''], // Campo oculto para armazenar a string Base64
      local_pdf_file: [null], // NOVO: Control para o input de arquivo (sem ser Base64)
      externalID: [''],
      signers: this.fb.array([]) // Array de signatários
    }, { validators: urlOrFileRequiredValidator }); // Adicionado validador no nível do FormGroup
  }

  ngOnInit(): void {
    if (this.isEditMode) {
      this.documentForm.get('local_pdf_file')?.disable();
    }
    this.documentId = this.route.snapshot.params['id'];
    if (this.documentId) {
      this.isEditMode = true;
      // No modo de edição, apenas a URL é suportada para reanálise
      this.documentForm.get('url_pdf')?.setValidators([Validators.pattern('https?://.+')]);
      this.documentForm.get('base64_pdf')?.setValidators(null);

      this.documentService.getDocumentById(this.documentId).subscribe({
        next: (document) => {
          this.documentForm.patchValue({
            name: document.name,
            // company não é mais preenchido no formulário
            url_pdf: document.url_pdf,
            externalID: document.externalID,
            // base64_pdf e local_pdf_file ficam vazios (não é suportado editar arquivo)
          });
          // Preenche os signatários existentes
          if (document.signers_db && document.signers_db.length > 0) {
            this.originalSigners = [...document.signers_db]; // Salva uma cópia dos signatários originais
            document.signers_db.forEach(signer => {
              this.addSigner(signer); // Passa o objeto signer completo
            });
          } else {
            // Se não houver signatários, adicione um padrão para edição também
            this.addSigner();
          }
        },
        error: (err) => {
          this.errorMessage = err.message || 'Falha ao carregar dados do documento.';
          console.error('Erro ao carregar documento:', err);
        }
      });
    } else {
      // Se for novo documento, adicione um signatário padrão
      this.addSigner();

      // Validações adicionais para o modo de criação: 
      this.documentForm.get('url_pdf')?.setValidators([Validators.pattern('https?://.+')]);
      this.documentForm.get('url_pdf')?.updateValueAndValidity();
      this.documentForm.get('base64_pdf')?.updateValueAndValidity();
    }
  }

  get signers(): FormArray {
    return this.documentForm.get('signers') as FormArray;
  }

  // Modificado para aceitar um objeto Signer opcional
  addSigner(signer?: Signer): void {
    this.signers.push(this.fb.group({
      id: [signer?.id || null], // Adiciona o ID do signatário
      token: [signer?.token || null], // Adiciona o token do signatário
      status: [signer?.status || 'new'], // Adiciona o status do signatário
      name: [signer?.name || '', Validators.required],
      email: [signer?.email || '', [Validators.required, Validators.email]],
      externalID: [signer?.externalID || ''] // Usa externalID
    }));
  }

  removeSigner(index: number): void {
    // A lógica de exclusão remota será tratada no backend ao salvar
    this.signers.removeAt(index);
  }

  // Quando o usuário digita a URL do PDF
  onUrlInput(event: Event): void {
    const url = (event.target as HTMLInputElement).value;

    const fileCtrl = this.documentForm.get('local_pdf_file');
    const base64Ctrl = this.documentForm.get('base64_pdf');

    if (url) {
      // URL preenchida: desabilita upload local e limpa base64
      fileCtrl?.disable();
      fileCtrl?.setValue(null);

      base64Ctrl?.setValue('');
      base64Ctrl?.setErrors(null);
    } else if (!this.isEditMode) {
      // URL vazia: reabilita upload local (se não estiver em edição)
      fileCtrl?.enable();
    }

    this.documentForm.updateValueAndValidity();
  }


  onFileSelected(event: Event): void {
    const file: File | undefined = (event.target as HTMLInputElement).files?.[0];

    const urlCtrl = this.documentForm.get('url_pdf');
    const base64Ctrl = this.documentForm.get('base64_pdf');
    const fileCtrl = this.documentForm.get('local_pdf_file');

    // Reset inicial
    base64Ctrl?.setValue('');
    base64Ctrl?.setErrors(null);
    base64Ctrl?.markAsTouched();
    this.errorMessage = null;

    if (!file) {
      // Nenhum arquivo selecionado
      urlCtrl?.enable();
      fileCtrl?.setValue(null);
      this.documentForm.updateValueAndValidity();
      return;
    }

    // Arquivo selecionado: desabilita URL
    urlCtrl?.disable();
    urlCtrl?.setValue('');
    urlCtrl?.setErrors(null);

    // Validação de tamanho
    if (file.size > this.maxFileSizeMB * 1024 * 1024) {
      base64Ctrl?.setErrors({ maxSize: true });
      this.errorMessage = `O arquivo é muito grande. O limite é ${this.maxFileSizeMB}MB.`;
      urlCtrl?.enable();
      return;
    }

    // Validação de tipo
    if (file.type !== 'application/pdf') {
      base64Ctrl?.setErrors({ invalidType: true });
      this.errorMessage = 'Apenas arquivos PDF são suportados.';
      urlCtrl?.enable();
      return;
    }

    // Leitura do arquivo
    const reader = new FileReader();

    reader.onload = (e: ProgressEvent<FileReader>) => {
      const result = e.target?.result as string;
      const base64Content = result.split(',')[1];

      base64Ctrl?.setValue(base64Content);
      base64Ctrl?.setErrors(null);

      this.documentForm.updateValueAndValidity();
    };

    reader.onerror = () => {
      this.errorMessage = 'Erro ao ler o arquivo.';
      base64Ctrl?.setErrors({ readError: true });
      urlCtrl?.enable();
    };

    reader.readAsDataURL(file);
  }


  onSubmit(): void {
    this.errorMessage = null;
    this.successMessage = null;

    if (this.documentForm.valid) {
      // Pega o valor RAW para incluir campos disabled (que são ignorados pelo .value)
      const rawFormValue = this.documentForm.getRawValue();

      // Ajuste: Apenas url_pdf ou base64_pdf virão preenchidos (baseado no chaveamento)
      const documentData: any = {
        name: rawFormValue.name,
        externalID: rawFormValue.externalID,
        url_pdf: rawFormValue.url_pdf,
        base64_pdf: rawFormValue.base64_pdf,
        signers: rawFormValue.signers // Obtido do FormArray
      };

      // Limpeza do payload (o backend espera apenas 'url_pdf' OU 'base64_pdf')
      if (documentData.base64_pdf) {
        // Se há Base64, remove URL
        delete documentData.url_pdf;
      } else if (documentData.url_pdf) {
        // Se há URL, remove Base64 (sempre haverá um desses dois se a validação do form.valid passou)
        delete documentData.base64_pdf;
      } else {
        // A validação mútua falhou (nunca deveria chegar aqui se o form.valid é true)
        this.errorMessage = 'É obrigatório fornecer a URL do PDF OU um arquivo local.';
        return;
      }

      // Lógica para identificar signatários a serem removidos
      const currentSignerIds = this.signers.controls
        .map(control => control.get('id')?.value)
        .filter(id => id !== null);

      const signersToRemove = this.originalSigners.filter(
        originalSigner => originalSigner.id !== undefined && !currentSignerIds.includes(originalSigner.id)
      );

      // Adiciona os signatários a serem removidos ao payload, se houver
      if (signersToRemove.length > 0) {
        (documentData as any).signers_to_remove = signersToRemove.map(s => s.id);
      }

      if (this.isEditMode && this.documentId) {
        // NO MODO DE EDIÇÃO, BASE64_PDF NÃO É PERMITIDO.
        if (documentData.base64_pdf) {
          delete documentData.base64_pdf;
        }

        this.documentService.updateDocument(this.documentId, documentData).subscribe({
          next: () => {
            this.successMessage = 'Documento atualizado com sucesso!';
            this.router.navigate(['/documents']);
          },
          error: (err) => {
            this.errorMessage = err.message || 'Falha ao atualizar documento.';
            console.error('Erro ao atualizar documento:', err);
          }
        });
      } else {
        this.documentService.createDocument(documentData).subscribe({
          next: () => {
            this.successMessage = 'Documento criado com sucesso!';
            this.router.navigate(['/documents']);
          },
          error: (err) => {
            this.errorMessage = err.message || 'Falha ao criar documento.';
            console.error('Erro ao criar documento:', err);
          }
        });
      }
    } else {
      this.errorMessage = 'Por favor, preencha todos os campos obrigatórios e corrija os erros.';
      this.documentForm.markAllAsTouched(); // Marca todos os campos como tocados para exibir validações
    }
  }

  onCancel(): void {
    this.router.navigate(['/documents']);
  }
}