import { ENV } from '@/lib/env';

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message = code) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

type ApiRequestInit = Omit<RequestInit, 'body'> & {
  body?: unknown;
};

function buildUrl(path: string) {
  const base = ENV.API_BASE_URL.replace(/\/$/, '');
  const suffix = path.startsWith('/') ? path : `/${path}`;
  return `${base}${suffix}`;
}

export async function apiRequest<T>(path: string, init: ApiRequestInit = {}) {
  const headers: HeadersInit = {
    Accept: 'application/json',
    ...(init.body !== undefined ? { 'Content-Type': 'application/json' } : {}),
    ...(init.headers ?? {}),
  };

  const response = await fetch(buildUrl(path), {
    ...init,
    headers,
    body: init.body === undefined ? undefined : JSON.stringify(init.body),
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new ApiError(response.status, payload.code ?? 'UNKNOWN_ERROR');
  }

  return payload as T;
}
