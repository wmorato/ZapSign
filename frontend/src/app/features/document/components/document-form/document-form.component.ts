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

  // NOVO MÉTODO DE CHAVEAMENTO: Quando o usuário digita na URL
  onUrlInput(event: any): void {
    const url = event.target.value;
    if (url) {
      // Se a URL tem valor, desabilita o upload de arquivo local e limpa o base64
      this.documentForm.get('local_pdf_file')?.disable();
      this.documentForm.get('base64_pdf')?.setValue('');
    } else {
      // Se a URL está vazia, reabilita o upload de arquivo
      this.documentForm.get('local_pdf_file')?.enable();
    }
    this.documentForm.updateValueAndValidity(); // Força a revalidação
  }

  // MÉTODO MODIFICADO: Lidar com seleção de arquivo local e conversão para Base64
  onFileSelected(event: any): void {
    const file: File = event.target.files?.[0]; // Pega o primeiro arquivo
    
    // Reseta o estado do Base64
    this.documentForm.get('base64_pdf')?.setValue('');
    this.documentForm.get('base64_pdf')?.markAsTouched();
    
    // Habilita/Desabilita o campo de URL com base na existência do arquivo
    if (file) {
      this.documentForm.get('url_pdf')?.disable();
    } else {
      this.documentForm.get('url_pdf')?.enable();
      this.documentForm.get('local_pdf_file')?.setValue(null); // Limpa o controle de arquivo
      this.documentForm.updateValueAndValidity(); // Força a revalidação
      return;
    }

    if (file.size > this.maxFileSizeMB * 1024 * 1024) {
      this.documentForm.get('base64_pdf')?.setErrors({ maxSize: true });
      this.errorMessage = `O arquivo é muito grande. O limite é ${this.maxFileSizeMB}MB.`;
      this.documentForm.get('url_pdf')?.enable(); // Reabilita a URL
      return;
    }

    if (file.type !== 'application/pdf') {
      this.documentForm.get('base64_pdf')?.setErrors({ invalidType: true });
      this.errorMessage = 'Apenas arquivos PDF são suportados.';
      this.documentForm.get('url_pdf')?.enable(); // Reabilita a URL
      return;
    }

    // Limpa erros customizados se o arquivo for válido (os validators built-in são null)
    this.documentForm.get('base64_pdf')?.setErrors(null);
    this.errorMessage = null;

    const reader = new FileReader();
    reader.onload = (e: any) => {
      const base64StringWithPrefix: string = e.target.result;
      
      // Remove o prefixo (e.g., data:application/pdf;base64,) conforme ZapSign docs
      const base64Content = base64StringWithPrefix.split(',')[1]; 
      
      this.documentForm.get('base64_pdf')?.setValue(base64Content);
      this.documentForm.get('base64_pdf')?.setErrors(null);
      
      // Garante que o campo de URL está desabilitado
      this.documentForm.get('url_pdf')?.disable();
      this.documentForm.get('url_pdf')?.setValue(''); // Limpa o valor de URL se estava preenchido
      this.documentForm.get('url_pdf')?.setErrors(null);
      this.documentForm.updateValueAndValidity(); // Força revalidação do grupo
    };
    reader.onerror = () => {
      this.errorMessage = 'Erro ao ler o arquivo.';
      this.documentForm.get('base64_pdf')?.setErrors({ readError: true });
      this.documentForm.get('url_pdf')?.enable(); // Reabilita a URL em caso de erro de leitura
    };

    reader.readAsDataURL(file); // Lê como Data URL para obter a string Base64
  }
  // FIM MÉTODO MODIFICADO

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