// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\environments\environment.prod.ts
export const environment = {
    production: true,
    apiUrl: 'http://localhost:4200', // Nginx fará o proxy para o backend
    wsUrl: 'wss://localhost:4200' // Em produção, usa o proxy Nginx (wss)    
};