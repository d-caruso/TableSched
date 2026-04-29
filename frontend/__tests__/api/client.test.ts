import { expect, jest, test } from '@jest/globals';
import { ApiError, apiRequest } from '@/lib/api/client';

const fetchMock = jest.fn() as jest.MockedFunction<typeof fetch>;
global.fetch = fetchMock;

test('apiRequest throws ApiError on non-ok response', async () => {
  fetchMock.mockResolvedValueOnce({
    ok: false,
    status: 404,
    json: async () => ({ code: 'BOOKING_NOT_FOUND' }),
  } as Response);

  await expect(apiRequest('/api/test/')).rejects.toBeInstanceOf(ApiError);
});

test('ApiError carries the error code', () => {
  const error = new ApiError(401, 'INVALID_CREDENTIALS');
  expect(error.code).toBe('INVALID_CREDENTIALS');
  expect(error.status).toBe(401);
});
