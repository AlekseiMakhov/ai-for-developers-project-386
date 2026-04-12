import "@typespec/http";
import "./models/user.tsp";
import "./models/schedule.tsp";
import "./models/slot.tsp";
import "./models/booking.tsp";
import "./routes/auth.tsp";
import "./routes/schedules.tsp";
import "./routes/slots.tsp";
import "./routes/bookings.tsp";

using TypeSpec.Http;

@service({
  title: "SlotBook API",
  version: "1.0.0",
})
@server("http://localhost:8000", "Local development server")
namespace SlotBook;