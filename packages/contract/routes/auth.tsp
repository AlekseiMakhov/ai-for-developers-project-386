import "@typespec/http";
import "../models/user.tsp";

using TypeSpec.Http;

namespace SlotBook;

@route("/auth")
interface AuthRoutes {
  @post
  @route("/register")
  register(@body body: UserCreate): TokenResponse;

  @post
  @route("/login")
  login(@body body: UserLogin): TokenResponse;

  @post
  @route("/logout")
  logout(): void;

  @get
  @route("/me")
  me(): User;
}
