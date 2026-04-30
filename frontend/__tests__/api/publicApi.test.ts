import { expect, jest, test, beforeEach } from '@jest/globals';
import { publicApi } from '@/lib/api/endpoints';

const fetchMock = jest.fn() as jest.MockedFunction<typeof fetch>;
global.fetch = fetchMock;

beforeEach(() => { fetchMock.mockClear(); });

test('cancelBooking calls DELETE on /api/public/bookings/{token}/', async () => {
  fetchMock.mockResolvedValueOnce({ ok: true, status: 204, json: async () => null } as Response);
  await publicApi.cancelBooking('tok123');
  expect(fetchMock).toHaveBeenCalledWith(
    expect.stringContaining('/api/public/bookings/tok123/'),
    expect.objectContaining({ method: 'DELETE' }),
  );
});

test('cancelBooking URL does not contain /cancel/', async () => {
  fetchMock.mockResolvedValueOnce({ ok: true, status: 204, json: async () => null } as Response);
  await publicApi.cancelBooking('tok123');
  const calledUrl = (fetchMock.mock.calls[0] as any[])[0] as string;
  expect(calledUrl).not.toContain('/cancel/');
});
