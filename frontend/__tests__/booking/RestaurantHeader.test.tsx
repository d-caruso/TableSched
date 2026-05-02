import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { RestaurantHeader } from '@/components/booking/RestaurantHeader';

test('displays restaurant name', () => {
  render(<RestaurantHeader name="Da Mario" />);
  expect(screen.getByText('Da Mario')).toBeTruthy();
});
