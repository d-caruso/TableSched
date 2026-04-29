import { apiRequest } from '@/lib/api/client';
import type {
  Booking,
  BookingCreatePayload,
  BookingModifyPayload,
  RestaurantSettings,
  RestaurantPublicInfo,
  TimeSlot,
} from '@/lib/api/types';

export const publicApi = {
  getRestaurantInfo(tenant: string) {
    return apiRequest<RestaurantPublicInfo>(`/api/public/${tenant}/restaurant/`);
  },
  getAvailableSlots(tenant: string, date: string) {
    return apiRequest<TimeSlot[]>(`/api/public/${tenant}/slots/?date=${encodeURIComponent(date)}`);
  },
  createBooking(tenant: string, payload: BookingCreatePayload) {
    return apiRequest<Booking>(`/api/public/${tenant}/bookings/`, {
      method: 'POST',
      body: payload,
    });
  },
  getBookingByToken(token: string) {
    return apiRequest<Booking>(`/api/public/bookings/${token}/`);
  },
  cancelBooking(token: string) {
    return apiRequest<void>(`/api/public/bookings/${token}/cancel/`, {
      method: 'POST',
    });
  },
  modifyBooking(token: string, payload: BookingModifyPayload) {
    return apiRequest<Booking>(`/api/public/bookings/${token}/`, {
      method: 'PATCH',
      body: payload,
    });
  },
  getPaymentIntent(token: string) {
    return apiRequest<{ client_secret: string }>(`/api/public/bookings/${token}/payment-intent/`);
  },
};

export const staffApi = {
  login(tenant: string, email: string, password: string) {
    return apiRequest<{ access: string; refresh: string }>(`/api/staff/${tenant}/login/`, {
      method: 'POST',
      body: { email, password },
    });
  },
  triggerExpirationSweep(tenant: string, token: string) {
    return apiRequest<void>(`/api/staff/${tenant}/bookings/sweep/`, {
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
    return apiRequest<Booking[]>(`/api/staff/${tenant}/bookings/${suffix}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  getBooking(tenant: string, token: string, id: string) {
    return apiRequest<Booking>(`/api/staff/${tenant}/bookings/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  approveBooking(tenant: string, token: string, id: string) {
    return apiRequest<Booking>(`/api/staff/${tenant}/bookings/${id}/approve/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  rejectBooking(tenant: string, token: string, id: string, reason: string) {
    return apiRequest<Booking>(`/api/staff/${tenant}/bookings/${id}/reject/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: { reason },
    });
  },
  assignTable(tenant: string, token: string, id: string, table_id: string) {
    return apiRequest<Booking>(`/api/staff/${tenant}/bookings/${id}/assign-table/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: { table_id },
    });
  },
  createWalkin(tenant: string, token: string, payload: { party_size: number }) {
    return apiRequest<Booking>(`/api/staff/${tenant}/walkins/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: payload,
    });
  },
  getRestaurantSettings(tenant: string, token: string) {
    return apiRequest<RestaurantSettings>(`/api/staff/${tenant}/settings/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
  updateRestaurantSettings(tenant: string, token: string, payload: Partial<RestaurantSettings>) {
    return apiRequest<RestaurantSettings>(`/api/staff/${tenant}/settings/`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` },
      body: payload,
    });
  },
};
