import "@typespec/http";
import "../models/user.tsp";
import "../models/schedule.tsp";
import "../models/booking.tsp";

using TypeSpec.Http;

namespace SlotBook;

model HostPublic {
  id: string;
  name: string;
  slug: string;
  timezone: string;
  scheduleCount: int32;
}

model HostsPage {
  items: HostPublic[];
  total: int32;
  page: int32;
  pageSize: int32;
}

@route("/public/hosts")
interface PublicHostsRoutes {
  @get
  list(@query search?: string, @query page?: int32, @query pageSize?: int32): HostsPage;
}

@route("/public/{slug}")
interface PublicProfileRoutes {
  @get
  get(@path slug: string): { user: User; schedules: Schedule[] };
}

@route("/public/{slug}/schedules/{scheduleId}/bookings")
interface PublicBookingRoutes {
  @post
  create(
    @path slug: string,
    @path scheduleId: string,
    @body body: BookingCreate,
  ): Booking;
}

@route("/public/{slug}/schedules/{scheduleId}")
interface PublicScheduleRoutes {
  @get
  get(
    @path slug: string,
    @path scheduleId: string,
  ): Schedule;
}
