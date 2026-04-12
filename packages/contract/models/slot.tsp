import "@typespec/http";

using TypeSpec.Http;

namespace SlotBook;

enum SlotStatus {
  available,
  booked,
  blocked,
}

model Slot {
  id: string;
  scheduleId: string;
  startAt: utcDateTime;
  endAt: utcDateTime;
  status: SlotStatus;
}