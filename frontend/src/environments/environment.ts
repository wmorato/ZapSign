// D:\Projetos\DesafioTecnico\ZapSign\frontend\src\environments\environment.ts
export const environment = {
    production: false,
    apiUrl: 'http://localhost:4200', // Nginx fará o proxy para o backend
    wsUrl: 'ws://localhost:8000' // Porta direta do Daphne (WebSocket)
};