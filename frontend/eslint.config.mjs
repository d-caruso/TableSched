import tsParser from '@typescript-eslint/parser';
import reactNative from 'eslint-plugin-react-native';

export default [
  {
    ignores: ['**/node_modules/**', '**/dist/**', '**/.expo/**'],
  },
  {
    files: ['**/*.{js,mjs,cjs,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      'react-native': reactNative,
    },
    rules: {
      'no-undef': 'off',
      'no-unused-vars': 'off',
      'react-native/no-inline-styles': 'error',
    },
  },
];
