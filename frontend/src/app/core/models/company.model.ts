// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\app\core\models\company.model.ts
export interface Company {
    id?: number; // Opcional, pois não existe na criação
    name: string;
    apiToken?: string; // Opcional, pode ser nulo/vazio
    created_at?: string;
    last_updated_at?: string;
}