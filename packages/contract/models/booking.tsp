import "@typespec/http";

using TypeSpec.Http;

namespace SlotBook;

enum BookingStatus {
  pending,
  confirmed,
  cancelled,
}

model Booking {
  id: string;
  scheduleId: string;
  slotId: string;
  guestName: string;
  guestEmail: string;
  guestNote?: string;
  status: BookingStatus;
  confirmationToken: string;
  cancelToken: string;
  createdAt: utcDateTime;
}

model BookingCreate {
  slotId: string;
  guestName: string;
  guestEmail: string;
  guestNote?: string;
}
