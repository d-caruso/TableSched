export type BookingStatus =
  | 'pending_review'
  | 'pending_payment'
  | 'confirmed'
  | 'confirmed_without_deposit'
  | 'declined'
  | 'cancelled_by_customer'
  | 'cancelled_by_staff'
  | 'authorization_expired';

export type PaymentStatus =
  | 'pending'
  | 'authorized'
  | 'captured'
  | 'failed'
  | 'requires_action'
  | 'refund_pending'
  | 'refunded'
  | 'refund_failed';

export type Payment = {
  id: string;
  status: PaymentStatus;
};

export type TimeSlot = {
  date: string;
  time: string;
  available: boolean;
};

export type OpeningHour = {
  day: number;
  open: string;
  close: string;
};

export type DepositPolicy = {
  mode: 'never' | 'always' | 'by_party_size';
  min_party_size?: number | null;
};

export type RestaurantPublicInfo = {
  name: string;
  description?: string | null;
  timezone: string;
  currency: string;
  booking_window_days: number;
};

export type RestaurantSettings = {
  slug: string;
  name: string;
  opening_hours: OpeningHour[];
  deposit_policy: DepositPolicy;
  cancellation_cutoff_hours: number;
};

export type Room = {
  id: string;
  name: string;
  tables?: Table[] | null;
};

export type Table = {
  id: string;
  name: string;
  room?: Room | null;
  capacity: number;
  x?: number | null;
  y?: number | null;
};

export type BookingPayment = {
  id: string;
  status: PaymentStatus;
  amount: number;
  currency: string;
  client_secret?: string | null;
};

export type BookingCustomer = {
  name: string;
  phone: string;
  locale?: string | null;
  email?: string | null;
};

export type Booking = {
  id: string;
  status: BookingStatus;
  date: string;
  time: string;
  party_size: number;
  customer: BookingCustomer;
  created_at: string;
  notes?: string | null;
  table?: Table | null;
  payment?: BookingPayment | null;
};

export type BookingCreatePayload = {
  date: string;
  time: string;
  party_size: number;
  name: string;
  phone: string;
  email?: string;
  notes?: string;
};

export type BookingModifyPayload = {
  date: string;
  time: string;
  party_size: number;
};
