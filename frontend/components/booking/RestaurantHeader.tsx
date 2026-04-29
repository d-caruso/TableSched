import { Text, YStack } from 'tamagui';

type RestaurantHeaderProps = {
  name: string;
  description?: string | null;
};

export function RestaurantHeader({ name, description }: RestaurantHeaderProps) {
  return (
    <YStack gap="$2">
      <Text fontSize="$8" fontWeight="$8">
        {name}
      </Text>
      {description ? (
        <Text color="$color10" fontSize="$4">
          {description}
        </Text>
      ) : null}
    </YStack>
  );
}

