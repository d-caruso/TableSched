import { render, screen } from '@testing-library/react-native';
import { expect, jest, test } from '@jest/globals';
import { StatusBadge } from '@/components/ui/StatusBadge';

test('renders localized status label', () => {
  render(<StatusBadge status="pending_review" />);
  expect(screen.getByText(/Pending review/)).toBeTruthy();
});
