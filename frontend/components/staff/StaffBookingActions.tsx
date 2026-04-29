import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
import { YStack } from 'tamagui';
import type { Booking } from '@/lib/api/types';
import { staffApi } from '@/lib/api/endpoints';
import { AppButton } from '@/components/ui/AppButton';
import { AssignTableDialog } from '@/components/staff/AssignTableDialog';
import { RejectDialog } from '@/components/staff/RejectDialog';

type Props = {
  booking: Booking;
  tenant: string;
  token: string;
  onActionComplete: () => void | Promise<void>;
};

export function StaffBookingActions({ booking, tenant, token, onActionComplete }: Props) {
  const { t } = useTranslation();
  const [showReject, setShowReject] = useState(false);
  const [showAssign, setShowAssign] = useState(false);

  const approve = useMutation({
    mutationFn: () => staffApi.approveBooking(tenant, token, booking.id),
    onSuccess: onActionComplete,
  });

  const confirmWithoutDeposit = useMutation({
    mutationFn: () => staffApi.approveBooking(tenant, token, booking.id),
    onSuccess: onActionComplete,
  });

  const reject = useMutation({
    mutationFn: (reason: string) => staffApi.rejectBooking(tenant, token, booking.id, reason),
    onSuccess: () => {
      setShowReject(false);
      void onActionComplete();
    },
  });

  const assignTable = useMutation({
    mutationFn: (tableId: string) => staffApi.assignTable(tenant, token, booking.id, tableId),
    onSuccess: () => {
      setShowAssign(false);
      void onActionComplete();
    },
  });

  const canApprove = booking.status === 'pending_review' || booking.status === 'authorization_expired';
  const canConfirmWithoutDeposit = booking.status === 'authorization_expired';
  const canReject = canApprove;
  const canAssign =
    booking.status === 'pending_review' ||
    booking.status === 'authorization_expired' ||
    booking.status === 'confirmed' ||
    booking.status === 'confirmed_without_deposit';

  return (
    <YStack gap="$3">
      {canApprove ? (
        <AppButton onPress={() => approve.mutate()} loading={approve.isPending}>
          {t('staff.booking.approve')}
        </AppButton>
      ) : null}
      {canConfirmWithoutDeposit ? (
        <AppButton onPress={() => confirmWithoutDeposit.mutate()} loading={confirmWithoutDeposit.isPending}>
          {t('staff.booking.confirmWithoutDeposit')}
        </AppButton>
      ) : null}
      {canReject ? (
        <>
          <AppButton variant="secondary" onPress={() => setShowReject(true)}>
            {t('staff.booking.reject')}
          </AppButton>
          {showReject ? <RejectDialog onSubmit={reason => reject.mutate(reason)} loading={reject.isPending} /> : null}
        </>
      ) : null}
      {canAssign ? (
        <>
          <AppButton variant="secondary" onPress={() => setShowAssign(true)}>
            {t('staff.booking.assignTable')}
          </AppButton>
          {showAssign ? <AssignTableDialog onSubmit={tableId => assignTable.mutate(tableId)} loading={assignTable.isPending} /> : null}
        </>
      ) : null}
    </YStack>
  );
}
