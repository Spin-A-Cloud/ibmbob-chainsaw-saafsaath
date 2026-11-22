export type UserRole = "customer" | "company";

export interface AuthUser {
  name: string;
  email: string;
  role: UserRole;
  token: string;
}
