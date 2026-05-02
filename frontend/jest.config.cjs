module.exports = {
  preset: 'jest-expo',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^tamagui$': '<rootDir>/__mocks__/tamagui.ts',
    '^@tamagui/core$': '<rootDir>/__mocks__/tamagui.ts',
  },
};
