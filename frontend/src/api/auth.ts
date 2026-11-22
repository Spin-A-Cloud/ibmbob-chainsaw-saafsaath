import type { AuthUser, UserRole } from "../types/auth";

const BASE = "/api";

export async function loginApi(
  email: string,
  password: string
): Promise<AuthUser> {
  const res = await fetch(`${BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Login failed");
  }

  const data = await res.json();
  return {
    name: data.name,
    email,
    role: data.role as UserRole,
    token: data.access_token,
  };
}

export async function registerApi(
  name: string,
  email: string,
  password: string,
  role: UserRole
): Promise<void> {
  const res = await fetch(`${BASE}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password, role }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Registration failed");
  }
}
