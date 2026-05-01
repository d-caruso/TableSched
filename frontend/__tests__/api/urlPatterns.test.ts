import { expect, jest, test, beforeEach } from '@jest/globals';

const fetchMock = jest.fn() as jest.MockedFunction<typeof fetch>;
global.fetch = fetchMock;

beforeEach(() => { fetchMock.mockClear(); });

const okResponse = { ok: true, status: 200, json: async () => ({}) } as Response;

import { publicApi, staffApi } from '@/lib/api/endpoints';

test('getRestaurantInfo uses /restaurants/{tenant}/api/v1/ prefix', async () => {
  fetchMock.mockResolvedValueOnce(okResponse);
  await publicApi.getRestaurantInfo('rome').catch(() => {});
  expect((fetchMock.mock.calls[0] as any[])[0]).toContain('/restaurants/rome/api/v1/');
});

test('getBookingByToken includes tenant in URL', async () => {
  fetchMock.mockResolvedValueOnce(okResponse);
  await publicApi.getBookingByToken('rome', 'tok123').catch(() => {});
  const url = (fetchMock.mock.calls[0] as any[])[0] as string;
  expect(url).toContain('/restaurants/rome/api/v1/');
  expect(url).toContain('tok123');
});

test('staffApi.login uses /restaurants/{tenant}/api/v1/auth/login/', async () => {
  fetchMock.mockResolvedValueOnce(okResponse);
  await staffApi.login('rome', 'a@b.com', 'pw').catch(() => {});
  expect((fetchMock.mock.calls[0] as any[])[0]).toContain('/restaurants/rome/api/v1/auth/login/');
});

test('staffApi.listBookings uses /restaurants/{tenant}/api/v1/bookings/', async () => {
  fetchMock.mockResolvedValueOnce({ ...okResponse, json: async () => [] } as any);
  await staffApi.listBookings('rome', 'tok').catch(() => {});
  expect((fetchMock.mock.calls[0] as any[])[0]).toContain('/restaurants/rome/api/v1/bookings/');
});

test('no old /api/public/ or /api/staff/ patterns reachable', async () => {
  fetchMock.mockResolvedValue(okResponse);
  await publicApi.getRestaurantInfo('rome').catch(() => {});
  const url = (fetchMock.mock.calls[0] as any[])[0] as string;
  expect(url).not.toContain('/api/public/');
  expect(url).not.toContain('/api/staff/');
});
