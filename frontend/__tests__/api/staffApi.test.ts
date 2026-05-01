import { expect, test } from '@jest/globals';
import { staffApi } from '@/lib/api/endpoints';

test('staffApi exposes postDecision', () => {
  expect(typeof staffApi.postDecision).toBe('function');
});

test('staffApi exposes assignTables', () => {
  expect(typeof staffApi.assignTables).toBe('function');
});

test('staffApi exposes patchBooking', () => {
  expect(typeof staffApi.patchBooking).toBe('function');
});

test('staffApi exposes refundPayment', () => {
  expect(typeof staffApi.refundPayment).toBe('function');
});

test('staffApi does not expose deleted methods', () => {
  expect((staffApi as any).approveBooking).toBeUndefined();
  expect((staffApi as any).rejectBooking).toBeUndefined();
  expect((staffApi as any).assignTable).toBeUndefined();
  expect((staffApi as any).markNoShow).toBeUndefined();
  expect((staffApi as any).modifyBooking).toBeUndefined();
  expect((staffApi as any).requestPayment).toBeUndefined();
});
