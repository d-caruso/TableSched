import { expect, test } from '@jest/globals';
import en from '@/lib/i18n/locales/en.json';
import it from '@/lib/i18n/locales/it.json';
import de from '@/lib/i18n/locales/de.json';

function flatKeys(obj: Record<string, unknown>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return flatKeys(value as Record<string, unknown>, fullKey);
    }

    return [fullKey];
  });
}

function valueAtPath(obj: Record<string, unknown>, path: string) {
  return path.split('.').reduce<unknown>((acc, part) => {
    if (!acc || typeof acc !== 'object') return undefined;
    return (acc as Record<string, unknown>)[part];
  }, obj);
}

test('it.json has all en.json keys', () => {
  const enKeys = flatKeys(en as Record<string, unknown>);
  const itKeys = flatKeys(it as Record<string, unknown>);
  enKeys.forEach(key => expect(itKeys).toContain(key));
});

test('de.json has all en.json keys', () => {
  const enKeys = flatKeys(en as Record<string, unknown>);
  const deKeys = flatKeys(de as Record<string, unknown>);
  enKeys.forEach(key => expect(deKeys).toContain(key));
});

test('no locale contains empty string values', () => {
  [it, de].forEach(locale => {
    flatKeys(locale as Record<string, unknown>).forEach(key => {
      const value = valueAtPath(locale as Record<string, unknown>, key);
      expect(typeof value === 'string' && value.trim().length > 0).toBe(true);
    });
  });
});
