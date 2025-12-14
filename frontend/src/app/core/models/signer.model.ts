// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\models\signer.model.ts
export interface Signer {
    id?: number;
    token?: string;
    status?: string;
    name: string;
    email: string;
    externalID?: string;
    document?: number; // ID do documento ao qual o signatário pertence
}