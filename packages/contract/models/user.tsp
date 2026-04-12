import "@typespec/http";

using TypeSpec.Http;

namespace SlotBook;

model User {
  id: string;
  email: string;
  name: string;
  timezone: string;
  slug: string;
  createdAt: utcDateTime;
}

model UserCreate {
  email: string;
  name: string;
  password: string;
  timezone: string;
  slug: string;
}

model UserLogin {
  email: string;
  password: string;
}

model TokenResponse {
  accessToken: string;
  tokenType: string;
}