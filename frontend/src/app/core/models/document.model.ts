// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\models\document.model.ts
import { Company } from './company.model';
import { Signer } from './signer.model'; // Importe Signer

export interface DocumentAnalysis {
    status: string;
    summary: string | null;
    missing_topics: string[] | null;
    insights: string[] | null;
    model_used: string | null;
    created_at: string;
    last_updated_at: string;
}

export interface Document {
    id?: number;
    openID?: number;
    token?: string;
    name: string;
    status?: string;
    created_at?: string;
    last_updated_at?: string;
    created_by?: string;
    company: number; // ID da empresa
    externalID?: string;
    signers_db?: Signer[]; // Lista de signatários associados (do DB local)
    ai_analysis?: DocumentAnalysis; // Análise de IA
    url_pdf?: string; // Adicionado para a criação de documentos
    signed_file_url?: string; // <--- ADICIONADO: URL do PDF assinado (S3)
}