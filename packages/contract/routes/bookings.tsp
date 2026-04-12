import "@typespec/http";
import "../models/booking.tsp";

using TypeSpec.Http;

namespace SlotBook;

@route("/bookings")
interface BookingRoutes {
  @get
  list(): Booking[];

  @get
  @route("/{id}")
  get(@path id: string): Booking;

  @patch
  @route("/{id}/confirm")
  confirm(@path id: string): Booking;

  @patch
  @route("/{id}/cancel")
  cancel(@path id: string): Booking;

  @get
  @route("/confirm/{token}")
  confirmByToken(@path token: string): Booking;

  @get
  @route("/cancel/{cancelToken}")
  cancelByToken(@path cancelToken: string): Booking;
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
