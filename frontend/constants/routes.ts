export const ROUTES = {
  publicBooking: (tenant: string) => `/${tenant}` as const,
  bookingDetail: (token: string) => `/booking/${token}` as const,
  bookingPay: (token: string) => `/booking/${token}/pay` as const,
  staffLogin: '/login',
  dashboard: '/dashboard',
  bookingAdmin: (id: string) => `/dashboard/bookings/${id}` as const,
  walkins: '/dashboard/walkins',
  settings: '/dashboard/settings',
  floor: '/dashboard/settings/floor',
} as const;
