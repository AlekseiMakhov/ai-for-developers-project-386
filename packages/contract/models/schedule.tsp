import "@typespec/http";

using TypeSpec.Http;

namespace SlotBook;

model TimeRange {
  start: string;
  end: string;
}

model WeeklyAvailability {
  monday?: TimeRange[];
  tuesday?: TimeRange[];
  wednesday?: TimeRange[];
  thursday?: TimeRange[];
  friday?: TimeRange[];
  saturday?: TimeRange[];
  sunday?: TimeRange[];
}

model Schedule {
  id: string;
  userId: string;
  name: string;
  description?: string;
  duration: int32;
  bufferBefore: int32;
  bufferAfter: int32;
  availability: WeeklyAvailability;
  timezone: string;
  isActive: boolean;
  color?: string;
  slug: string;
}

model ScheduleCreate {
  name: string;
  description?: string;
  duration: int32;
  bufferBefore: int32;
  bufferAfter: int32;
  availability: WeeklyAvailability;
  timezone: string;
  isActive: boolean;
  color?: string;
  slug: string;
}

model ScheduleUpdate {
  name?: string;
  description?: string;
  duration?: int32;
  bufferBefore?: int32;
  bufferAfter?: int32;
  availability?: WeeklyAvailability;
  timezone?: string;
  isActive?: boolean;
  color?: string;
  slug?: string;
}
