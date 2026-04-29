import { useMemo, useState } from 'react';
import { Pressable, Text, TextInput, View } from 'react-native';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n';
import { LocaleSelector } from '@/components/booking/LocaleSelector';
import type { Draft } from '@/components/booking/BookingFormFlow';

type StepContactProps = {
  tenant: string;
  draft: Draft;
  onBack: () => void;
  onNext: (draft: Draft) => void;
};

export function StepContact({ tenant, draft, onBack, onNext }: StepContactProps) {
  const { t } = useTranslation();
  const [name, setName] = useState(draft.name ?? '');
  const [phone, setPhone] = useState(draft.phone ?? '');
  const [email, setEmail] = useState(draft.email ?? '');
  const [locale, setLocale] = useState(draft.locale ?? 'en');
  const [notes, setNotes] = useState(draft.notes ?? '');

  const canSubmit = useMemo(() => name.trim().length > 0 && phone.trim().length > 0, [name, phone]);

  return (
    <View testID={`step-contact-${tenant}`}>
      <Text>{t('booking.page.booking_flow')}</Text>
      <TextInput accessibilityLabel={t('booking.contact.full_name')} value={name} onChangeText={setName} />
      <TextInput accessibilityLabel={t('booking.contact.phone_number')} value={phone} onChangeText={setPhone} />
      <TextInput accessibilityLabel={t('booking.contact.email')} value={email} onChangeText={setEmail} />
      <LocaleSelector value={locale} onChange={setLocale} />
      <TextInput accessibilityLabel={t('booking.contact.notes')} value={notes} onChangeText={setNotes} />
      <Pressable accessibilityRole="button" onPress={onBack}>
        <Text>{t('booking.page.back')}</Text>
      </Pressable>
      <Pressable
        accessibilityRole="button"
        disabled={!canSubmit}
        onPress={() => {
          if (!canSubmit) {
            return;
          }

          onNext({
            name: name.trim(),
            phone: phone.trim(),
            email: email.trim() || undefined,
            locale,
            notes: notes.trim() || undefined,
          });
        }}
      >
        <Text>{t('booking.page.request_booking')}</Text>
      </Pressable>
    </View>
  );
}
