const { createRequire } = require('node:module');
const requireJson = createRequire(__filename);

const en = requireJson('../lib/i18n/locales/en.json') as Record<string, unknown>;
const it = requireJson('../lib/i18n/locales/it.json') as Record<string, unknown>;
const de = requireJson('../lib/i18n/locales/de.json') as Record<string, unknown>;

function flatKeys(obj: Record<string, unknown>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return flatKeys(value as Record<string, unknown>, fullKey);
    }

    return [fullKey];
  });
}

const enKeys = flatKeys(en);
const itKeys = flatKeys(it);
const deKeys = flatKeys(de);

const missing = {
  it: enKeys.filter(key => !itKeys.includes(key)),
  de: enKeys.filter(key => !deKeys.includes(key)),
};

if (missing.it.length || missing.de.length) {
  console.error('Missing i18n keys:', missing);
  process.exit(1);
}

console.log('OK - all keys present in it and de.');
