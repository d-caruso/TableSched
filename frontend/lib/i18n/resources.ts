export const resources = {
  en: {
    translation: {
      common: {
        loading: 'Loading',
        error: 'Something went wrong',
      },
      booking: {
        page: {
          opening_hours: 'Opening hours',
          booking_flow: 'Booking form',
        },
        hours: {
          closed: 'Closed',
        },
        weekdays: {
          monday: 'Monday',
          tuesday: 'Tuesday',
          wednesday: 'Wednesday',
          thursday: 'Thursday',
          friday: 'Friday',
          saturday: 'Saturday',
          sunday: 'Sunday',
        },
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
