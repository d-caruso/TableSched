import { render, type RenderOptions } from '@testing-library/react-native/pure';
import type { ReactElement } from 'react';
import { TamaguiProvider } from 'tamagui';
import { tamaguiConfig } from '@/tamagui.config';

function Wrapper({ children }: { children: ReactElement }) {
  return <TamaguiProvider config={tamaguiConfig} defaultTheme="light">{children}</TamaguiProvider>;
}

function renderWithTamagui(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, { wrapper: Wrapper, ...options });
}

export * from '@testing-library/react-native/pure';
export { renderWithTamagui as render };
