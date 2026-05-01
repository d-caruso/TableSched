import { apiRequest } from '@/lib/api/client';
import type {
  Booking,
  BookingCreatePayload,
  BookingModifyPayload,
  Payment,
  RestaurantSettings,
  RestaurantPublicInfo,
  Room,
  TenantEntry,
  TimeSlot,
} from '@/lib/api/types';

const tp = (tenant: string, path: string) => `/restaurants/${tenant}/api/v1/${path}`;

export const publicApi = {
  tenantDirectory() {
    return apiRequest<TenantEntry[]>('/api/tenants/');
  },
  getRestaurantInfo(tenant: string) {
    return apiRequest<RestaurantPublicInfo>(tp(tenant, 'public/restaurant/'));
  },
  getAvailableSlots(tenant: string, date: string) {
    return apiRequest<TimeSlot[]>(tp(tenant, `public/slots/?date=${encodeURIComponent(date)}`));
  },
  createBooking(tenant: string, payload: BookingCreatePayload) {
    return apiRequest<Booking>(tp(tenant, 'public/bookings/'), {
      method: 'POST',
      body: payload,
    });
  },
  getBookingByToken(tenant: string, token: string) {
    return apiRequest<Booking>(tp(tenant, `public/bookings/${token}/`));
  },
  cancelBooking(tenant: string, token: string) {
    return apiRequest<void>(tp(tenant, `public/bookings/${token}/`), {
      method: 'DELETE',
    });
  },
  modifyBooking(tenant: string, token: string, payload: BookingModifyPayload) {
    return apiRequest<Booking>(tp(tenant, `public/bookings/${token}/`), {
      method: 'PATCH',
      body: payload,
    });
  },
  getPaymentIntent(tenant: string, token: string) {
    return apiRequest<{ client_secret: string }>(tp(tenant, `public/bookings/${token}/payment-intent/`));
  },
};

export const staffApi = {
  login(tenant: string, email: string, password: string) {
    return apiRequest<{ access: string; refresh: string }>(tp(tenant, 'auth/login/'), {
      method: 'POST',
      body: { email, password },
    });
  },
  triggerExpirationSweep(tenant: string, token: string) {
    return apiRequest<void>(tp(tenant, 'bookings/sweep/'), {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  listBookings(tenant: string, token: string, params?: Record<string, string | number | undefined>) {
    const query = new URLSearchParams();
    Object.entries(params ?? {}).forEach(([key, value]) => {
      if (value !== undefined && value !== '') query.set(key, String(value));
    });
    const suffix = query.toString() ? `?${query.toString()}` : '';
    return apiRequest<Booking[]>(tp(tenant, `bookings/${suffix}`), {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  getBooking(tenant: string, token: string, id: string) {
    return apiRequest<Booking>(tp(tenant, `bookings/${id}/`), {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  postDecision(
    tenant: string,
    token: string,
    id: string,
    payload: { outcome: 'approved' | 'declined' | 'confirmed_without_deposit'; reason_code?: string; staff_message?: string },
  ) {
    return apiRequest<Booking>(tp(tenant, `bookings/${id}/decisions/`), {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: payload,
    });
  },
  assignTables(tenant: string, token: string, id: string, tableIds: string[]) {
    return apiRequest<{ tables: string[] }>(tp(tenant, `bookings/${id}/tables/`), {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` },
      body: { tables: tableIds },
    });
  },
  patchBooking(
    tenant: string,
    token: string,
    id: string,
    payload: { starts_at?: string; party_size?: number; notes?: string; status?: 'no_show' },
  ) {
    return apiRequest<Booking>(tp(tenant, `bookings/${id}/`), {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` },
      body: payload,
    });
  },
  refundPayment(tenant: string, token: string, paymentId: string) {
    return apiRequest<Payment>(tp(tenant, `payments/${paymentId}/refunds/`), {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  createWalkin(tenant: string, token: string, payload: { party_size: number }) {
    return apiRequest<Booking>(tp(tenant, 'walkins/'), {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: payload,
    });
  },
  listRooms(tenant: string, token: string) {
    return apiRequest<Room[]>(tp(tenant, 'rooms/'), {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  updateTablePosition(tenant: string, token: string, tableId: string, x: number, y: number) {
    return apiRequest<void>(tp(tenant, `tables/${tableId}/position/`), {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` },
      body: { x, y },
    });
  },
  getRestaurantSettings(tenant: string, token: string) {
    return apiRequest<RestaurantSettings>(tp(tenant, 'settings/'), {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  updateRestaurantSettings(tenant: string, token: string, payload: Partial<RestaurantSettings>) {
    return apiRequest<RestaurantSettings>(tp(tenant, 'settings/'), {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` },
      body: payload,
    });
  },
};
