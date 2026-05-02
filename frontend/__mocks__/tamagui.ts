/**
 * Tamagui mock for Jest + @testing-library/react-native.
 *
 * RNTL queries the React Native component tree, so Tamagui stubs must back
 * onto RN host components (View, Text, TextInput, Switch, Pressable).
 * This is not a workaround — it is the only approach that works with RNTL,
 * as documented by the community (no official Tamagui Jest preset exists).
 */
const React = require('react');
const { View, Text, TextInput, Switch, Pressable, ScrollView } = require('react-native');

const stack = ({ children, onPress, accessibilityRole, accessibilityLabel, accessibilityState, testID }: any) =>
  React.createElement(Pressable, { onPress, accessibilityRole, accessibilityLabel, accessibilityState, testID }, children ?? null);

const view = ({ children, testID, accessibilityLabel }: any) =>
  React.createElement(View, { testID, accessibilityLabel }, children ?? null);

const text = ({ children, testID, accessibilityLabel }: any) =>
  React.createElement(Text, { testID, accessibilityLabel }, children ?? null);

module.exports = {
  Stack: stack,
  XStack: stack,
  YStack: view,
  Text: text,
  Button: stack,
  Spinner: () => null,
  ScrollView: ({ children }: any) => React.createElement(ScrollView, null, children ?? null),
  Input: ({ accessibilityLabel, value, onChangeText, placeholder, testID }: any) =>
    React.createElement(TextInput, { accessibilityLabel, value, onChangeText, placeholder, testID }),
  Switch: ({ checked, onCheckedChange, accessibilityRole, testID }: any) =>
    React.createElement(Switch, { value: checked ?? false, onValueChange: onCheckedChange, accessibilityRole: accessibilityRole ?? 'switch', testID }),
  Select: view,
  Sheet: view,
  Adapt: view,
  TamaguiProvider: ({ children }: any) => children,
  useMedia: jest.fn(() => ({})),
  createTamagui: (config: any) => config,
};
