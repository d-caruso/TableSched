import type { ComponentProps } from 'react';
import { Button } from 'tamagui';

type AppButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

type AppButtonProps = Omit<ComponentProps<typeof Button>, 'variant'> & {
  variant?: AppButtonVariant;
  loading?: boolean;
};

const variantStyles: Record<AppButtonVariant, Record<string, unknown>> = {
  primary: {
    backgroundColor: '$brand',
    color: '$background',
  },
  secondary: {
    backgroundColor: '$background',
    borderColor: '$brand',
    borderWidth: 1,
    color: '$brand',
  },
  danger: {
    backgroundColor: '$danger',
    color: '$background',
  },
  ghost: {
    backgroundColor: 'transparent',
    color: '$brand',
  },
};

export function AppButton({ variant = 'primary', loading, children, ...props }: AppButtonProps) {
  const disabled = loading ?? props.disabled;

  return (
    <Button
      {...variantStyles[variant]}
      {...props}
      disabled={disabled}
      opacity={loading ? 0.7 : 1}
      borderRadius="$4"
      fontWeight="$6"
    >
      {children}
    </Button>
  );
}
