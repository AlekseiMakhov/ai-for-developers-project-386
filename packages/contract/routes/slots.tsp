import "@typespec/http";
import "../models/slot.tsp";

using TypeSpec.Http;

namespace SlotBook;

@route("/public/{slug}/schedules/{scheduleId}/slots")
interface SlotRoutes {
  @get
  list(
    @path slug: string,
    @path scheduleId: string,
    @query date: string,
  ): Slot[];
}