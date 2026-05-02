import { PRESS_STYLE } from '@/constants/styles';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Stack, Switch, Text, XStack, YStack } from 'tamagui';
import '@/lib/i18n';
import type { OpeningHour } from '@/lib/api/types';

/*
 * OpeningHoursEditor
 *
 * Each day can have 0, 1 or 2 OpeningHour slots (e.g. lunch + dinner).
 * The API model is: multiple OpeningHour records with the same `weekday`.
 * No type change required — this is already valid per the backend schema.
 *
 * Internal state is a plain OpeningHour[] (same as the prop type).
 * Helpers below convert between the flat array and a per-day slot structure.
 *
 * Time values are chosen from a <select> at 30-min intervals —
 * no free-text input, no HH:MM validation needed.
 */

// ─── constants ──────────────────────────────────────────────────────────────

const DAYS = [0, 1, 2, 3, 4, 5, 6] as const;
const MAX_SLOTS_PER_DAY = 2;

const DEFAULT_OPENS_AT = '09:00';
const DEFAULT_CLOSES_AT = '22:00';

/** Every 30-minute interval across 24 h, as "HH:MM" strings. */
const TIME_OPTIONS: string[] = (() => {
  const opts: string[] = [];
  for (let m = 0; m < 24 * 60; m += 30) {
    const h = String(Math.floor(m / 60)).padStart(2, '0');
    const min = String(m % 60).padStart(2, '0');
    opts.push(`${h}:${min}`);
  }
  return opts;
})();

// ─── helpers ────────────────────────────────────────────────────────────────

/** All slots for a given weekday, in insertion order. */
function slotsForDay(hours: OpeningHour[], weekday: number): OpeningHour[] {
  return hours.filter(h => h.weekday === weekday);
}

/** Replace all slots for `weekday` with `nextSlots`, preserving other days. */
function setDaySlots(
  hours: OpeningHour[],
  weekday: number,
  nextSlots: OpeningHour[],
): OpeningHour[] {
  const other = hours.filter(h => h.weekday !== weekday);
  return [...other, ...nextSlots].sort((a, b) => a.weekday - b.weekday);
}

// ─── sub-components ─────────────────────────────────────────────────────────

type TimeSelectProps = {
  value: string;
  label: string;
  onChange: (value: string) => void;
};

const selectStyle: React.CSSProperties = {
  padding: '6px 8px',
  borderRadius: 6,
  border: '1.5px solid var(--border, #E2DDD8)',
  fontSize: 13,
  fontFamily: 'inherit',
  background: 'var(--background, #FDFCFB)',
  color: 'var(--color, #1A1714)',
  minWidth: 80,
};

function TimeSelect({ value, label, onChange }: TimeSelectProps) {
  return (
    <Stack accessibilityLabel={label}>
      {/* React Native Web renders this as a native <select> */}
      {/* @ts-ignore: 'select' is valid on web only */}
      <select
        value={value}
        aria-label={label}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => onChange(e.target.value)}
        style={selectStyle}
      >
        {TIME_OPTIONS.map(t => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>
    </Stack>
  );
}

// ─── main component ──────────────────────────────────────────────────────────

type Props = {
  hours: OpeningHour[];
  onChange: (hours: OpeningHour[]) => void;
};

export function OpeningHoursEditor({ hours = [], onChange }: Props) {
  const { t } = useTranslation();

  return (
    <YStack gap="$2">
      <Text fontSize="$4" fontWeight="$6">
        {t('staff.settings.openingHours')}
      </Text>

      {DAYS.map(day => {
        const slots = slotsForDay(hours, day);
        const isOpen = slots.length > 0;
        const dayLabel = t(`booking.weekdays.${day}`);

        const handleToggle = (next: boolean) => {
          if (!next) {
            onChange(setDaySlots(hours, day, []));
            return;
          }
          onChange(
            setDaySlots(hours, day, [
              { weekday: day, opens_at: DEFAULT_OPENS_AT, closes_at: DEFAULT_CLOSES_AT },
            ]),
          );
        };

        const handleAddSlot = () => {
          if (slots.length >= MAX_SLOTS_PER_DAY) return;
          const next = [
            ...slots,
            { weekday: day, opens_at: '19:00', closes_at: '22:00' },
          ];
          onChange(setDaySlots(hours, day, next));
        };

        const handleRemoveSlot = (slotIndex: number) => {
          const next = slots.filter((_, i) => i !== slotIndex);
          onChange(setDaySlots(hours, day, next));
        };

        const handlePatchSlot = (
          slotIndex: number,
          field: 'opens_at' | 'closes_at',
          value: string,
        ) => {
          const next = slots.map((s, i) => (i === slotIndex ? { ...s, [field]: value } : s));
          onChange(setDaySlots(hours, day, next));
        };

        return (
          <XStack
            key={day}
            accessibilityLabel={dayLabel}
            alignItems="flex-start"
            borderBottomWidth={1}
            borderColor="$borderColor"
            paddingVertical="$2"
            gap="$3"
          >
            {/* Day label — fixed width so all toggles align */}
            <Text
              width={72}
              paddingTop="$2"
              fontSize="$3"
              fontWeight={isOpen ? '$6' : '$4'}
              color={isOpen ? '$color' : '$placeholderColor'}
            >
              {dayLabel}
            </Text>

            {/* Toggle */}
            <Stack paddingTop="$2">
              <Switch
                accessibilityRole="switch"
                checked={isOpen}
                onCheckedChange={handleToggle}
              />
            </Stack>

            {/* Slots column */}
            <YStack flex={1} gap="$1">
              {!isOpen && (
                <Text paddingTop="$2" fontSize="$3" color="$placeholderColor" fontStyle="italic">
                  {t('staff.settings.closed')}
                </Text>
              )}

              {slots.map((slot, idx) => (
                <XStack key={idx} alignItems="center" gap="$2" flexWrap="wrap">
                  <TimeSelect
                    value={slot.opens_at}
                    label={t('staff.settings.open')}
                    onChange={v => handlePatchSlot(idx, 'opens_at', v)}
                  />
                  <Text fontSize="$2" color="$placeholderColor">–</Text>
                  <TimeSelect
                    value={slot.closes_at}
                    label={t('staff.settings.close')}
                    onChange={v => handlePatchSlot(idx, 'closes_at', v)}
                  />
                  {slots.length > 1 && (
                    <Stack
                      accessibilityRole="button"
                      accessibilityLabel={t('staff.settings.removeSlot')}
                      onPress={() => handleRemoveSlot(idx)}
                      pressStyle={PRESS_STYLE}
                    >
                      <Text fontSize="$3" color="$placeholderColor" paddingHorizontal="$1">×</Text>
                    </Stack>
                  )}
                </XStack>
              ))}

              {isOpen && slots.length < MAX_SLOTS_PER_DAY && (
                <Stack
                  accessibilityRole="button"
                  accessibilityLabel={t('staff.settings.addSlot')}
                  onPress={handleAddSlot}
                  pressStyle={PRESS_STYLE}
                >
                  <Text fontSize="$2" color="$blue10" paddingTop="$1">
                    + {t('staff.settings.addSlot')}
                  </Text>
                </Stack>
              )}
            </YStack>
          </XStack>
        );
      })}
    </YStack>
  );
}
