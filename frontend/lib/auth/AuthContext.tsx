import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { staffApi } from '@/lib/api/endpoints';

const ACCESS_TOKEN_KEY = 'tablesched.accessToken';
const REFRESH_TOKEN_KEY = 'tablesched.refreshToken';
const TENANT_KEY = 'tablesched.tenant';

type AuthState = {
  accessToken: string | null;
  tenant: string | null;
  isLoading: boolean;
};

type AuthContextValue = AuthState & {
  login: (email: string, password: string, tenant: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

async function writeItem(key: string, value: string) {
  if (typeof window !== 'undefined') {
    window.sessionStorage.setItem(key, value);
    return;
  }
  await SecureStore.setItemAsync(key, value);
}

async function readItem(key: string) {
  if (typeof window !== 'undefined') {
    return window.sessionStorage.getItem(key);
  }
  return SecureStore.getItemAsync(key);
}

async function removeItem(key: string) {
  if (typeof window !== 'undefined') {
    window.sessionStorage.removeItem(key);
    return;
  }
  await SecureStore.deleteItemAsync(key);
}

async function clearAuthStorage() {
  await Promise.all([
    removeItem(ACCESS_TOKEN_KEY),
    removeItem(REFRESH_TOKEN_KEY),
    removeItem(TENANT_KEY),
  ]);
}

async function loadAuthState(): Promise<Pick<AuthState, 'accessToken' | 'tenant'>> {
  const [accessToken, tenant] = await Promise.all([
    readItem(ACCESS_TOKEN_KEY),
    readItem(TENANT_KEY),
  ]);

  return {
    accessToken,
    tenant,
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [tenant, setTenant] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      const stored = await loadAuthState();
      setAccessToken(stored.accessToken);
      setTenant(stored.tenant);
      setIsLoading(false);
    })();
  }, []);

  const login = async (email: string, password: string, nextTenant: string) => {
    const { access_token, refresh_token } = await staffApi.login(nextTenant, email, password);
    await Promise.all([
      writeItem(ACCESS_TOKEN_KEY, access_token),
      writeItem(REFRESH_TOKEN_KEY, refresh_token),
      writeItem(TENANT_KEY, nextTenant),
    ]);
    setAccessToken(access_token);
    setTenant(nextTenant);
  };

  const logout = async () => {
    await clearAuthStorage();
    setAccessToken(null);
    setTenant(null);
  };

  const value = useMemo(
    () => ({ accessToken, tenant, isLoading, login, logout }),
    [accessToken, tenant, isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
