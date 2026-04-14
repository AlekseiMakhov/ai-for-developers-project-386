// Generated from TypeSpec — do not edit manually

export interface User {
  id: string;
  email: string;
  name: string;
  timezone: string;
  slug: string;
  createdAt: string;
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
  timezone: string;
  slug: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  accessToken: string;
  tokenType: string;
}

export interface TimeRange {
  start: string;
  end: string;
}

export interface WeeklyAvailability {
  monday?: TimeRange[];
  tuesday?: TimeRange[];
  wednesday?: TimeRange[];
  thursday?: TimeRange[];
  friday?: TimeRange[];
  saturday?: TimeRange[];
  sunday?: TimeRange[];
}

export interface Schedule {
  id: string;
  userId: string;
  name: string;
  description?: string;
  duration: number;
  bufferBefore: number;
  bufferAfter: number;
  availability: WeeklyAvailability;
  timezone: string;
  isActive: boolean;
  color?: string;
  slug: string;
}

export interface ScheduleCreate {
  name: string;
  description?: string;
  duration: number;
  bufferBefore: number;
  bufferAfter: number;
  availability: WeeklyAvailability;
  timezone: string;
  isActive: boolean;
  color?: string;
  slug: string;
}

export interface ScheduleUpdate {
  name?: string;
  description?: string;
  duration?: number;
  bufferBefore?: number;
  bufferAfter?: number;
  availability?: WeeklyAvailability;
  timezone?: string;
  isActive?: boolean;
  color?: string;
  slug?: string;
}

export type SlotStatus = "available" | "booked" | "blocked";

export interface Slot {
  id: string;
  scheduleId: string;
  startAt: string;
  endAt: string;
  status: SlotStatus;
}

export type BookingStatus = "pending" | "confirmed" | "cancelled" | "past";

export interface Booking {
  id: string;
  scheduleId: string;
  slotId: string;
  guestName: string;
  guestEmail: string;
  guestNote?: string;
  status: BookingStatus;
  confirmationToken: string;
  cancelToken: string;
  createdAt: string;
  slotStartAt?: string;
  slotEndAt?: string;
  scheduleName?: string;
}

export interface BookingCreate {
  slotId: string;
  guestName: string;
  guestEmail: string;
  guestNote?: string;
}

export interface PublicProfile {
  user: User;
  schedules: Schedule[];
}

export interface HostPublic {
  id: string;
  name: string;
  slug: string;
  timezone: string;
  scheduleCount: number;
}

export interface HostsPage {
  items: HostPublic[];
  total: number;
  page: number;
  pageSize: number;
}
