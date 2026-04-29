export const resources = {
  en: {
    translation: {
      common: {
        error: 'Something went wrong',
      },
      booking: {
        status: {
          pending_review: 'Pending review',
          pending_payment: 'Pending payment',
          confirmed: 'Confirmed',
          confirmed_without_deposit: 'Confirmed without deposit',
          declined: 'Declined',
          cancelled_by_customer: 'Cancelled by customer',
          authorization_expired: 'Authorization expired',
        },
      },
      error: {
        booking_not_found: 'Booking not found',
      },
    },
  },
} as const;

