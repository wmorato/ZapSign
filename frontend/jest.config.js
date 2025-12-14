// D:\Projetos\DesafioTecnico\ZapSign\frontend\jest.config.js
/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/src/test/jest-setup.ts'],
  // REMOVIDO: globalSetup: 'jest-preset-angular/global-setup',
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    // Mapeamento para garantir que o Zone.js seja carregado corretamente
    '^zone.js/testing$': 'zone.js/testing',
  },
  transform: {
    '^.+\\.(ts|js|html)$': [
      'jest-preset-angular',
      {
        tsconfig: '<rootDir>/tsconfig.spec.json',
        stringifyContentPathRegex: '\\.(html|svg)$',
      },
    ],
  },
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/app/**/*.ts',
    '!src/app/**/*.spec.ts',
    '!src/app/**/*.module.ts',
    '!src/app/**/*.config.ts',
    '!src/app/**/*.routes.ts',
    '!src/environments/**',
    '!src/main.ts',
  ],
};