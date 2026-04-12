import "@typespec/http";
import "../models/schedule.tsp";

using TypeSpec.Http;

namespace SlotBook;

@route("/schedules")
interface ScheduleRoutes {
  @get
  list(): Schedule[];

  @post
  create(@body body: ScheduleCreate): Schedule;

  @get
  @route("/{id}")
  get(@path id: string): Schedule;

  @put
  @route("/{id}")
  update(@path id: string, @body body: ScheduleUpdate): Schedule;

  @delete
  @route("/{id}")
  delete(@path id: string): void;
}
