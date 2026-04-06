/**
 * Timezone utility functions
 * Xử lý timezone (UTC+07:00) Bangkok, Hanoi, Jakarta
 */

const TIMEZONE_OFFSET = 7 * 60 // UTC+07:00 in minutes

/**
 * Lấy ngày hiện tại theo timezone UTC+07:00
 * Format: YYYY-MM-DD
 */
export function getCurrentDateInTimezone(): string {
  const now = new Date()
  const utc = now.getTime() + now.getTimezoneOffset() * 60000
  const localTime = new Date(utc + TIMEZONE_OFFSET * 60000)
  return formatDateToYMD(localTime)
}

/**
 * Lấy thời gian hiện tại theo timezone UTC+07:00
 * Format: HH:MM:SS
 */
export function getCurrentTimeInTimezone(): string {
  const now = new Date()
  const utc = now.getTime() + now.getTimezoneOffset() * 60000
  const localTime = new Date(utc + TIMEZONE_OFFSET * 60000)
  return formatTimeToHMS(localTime)
}

/**
 * Lấy datetime hiện tại theo timezone UTC+07:00
 */
export function getNowInTimezone(): Date {
  const now = new Date()
  const utc = now.getTime() + now.getTimezoneOffset() * 60000
  return new Date(utc + TIMEZONE_OFFSET * 60000)
}

/**
 * Format Date object sang YYYY-MM-DD
 */
export function formatDateToYMD(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Format Date object sang HH:MM:SS
 */
export function formatTimeToHMS(date: Date): string {
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

/**
 * Format Date object sang HH:MM
 */
export function formatTimeToHM(date: Date): string {
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

/**
 * Parse date string YYYY-MM-DD sang Date object trong timezone UTC+07:00
 */
export function parseDateInTimezone(dateStr: string): Date {
  const parts = dateStr.split('-').map(Number)
  const year = parts[0] ?? 2000
  const month = parts[1] ?? 1
  const day = parts[2] ?? 1
  return new Date(year, month - 1, day)
}

/**
 * Thêm hoặc trừ ngày từ một date string
 */
export function addDays(dateStr: string, days: number): string {
  const date = parseDateInTimezone(dateStr)
  date.setDate(date.getDate() + days)
  return formatDateToYMD(date)
}

/**
 * Thêm hoặc trừ tháng từ một date string
 */
export function addMonths(dateStr: string, months: number): string {
  const date = parseDateInTimezone(dateStr)
  date.setMonth(date.getMonth() + months)
  return formatDateToYMD(date)
}

/**
 * So sánh hai date strings
 * Trả về: -1 nếu date1 < date2, 0 nếu bằng nhau, 1 nếu date1 > date2
 */
export function compareDates(date1: string, date2: string): number {
  const d1 = parseDateInTimezone(date1)
  const d2 = parseDateInTimezone(date2)
  if (d1 < d2) return -1
  if (d1 > d2) return 1
  return 0
}

/**
 * Kiểm tra xem dateStr có phải là ngày hôm nay không (theo UTC+07:00)
 */
export function isToday(dateStr: string): boolean {
  return dateStr === getCurrentDateInTimezone()
}

/**
 * Lấy ngày đầu tuần (Monday) của một date string
 */
export function getWeekStart(dateStr: string): string {
  const date = parseDateInTimezone(dateStr)
  const day = date.getDay()
  const diff = day === 0 ? -6 : 1 - day // Nếu Sunday (0), quay lại Monday trước đó
  date.setDate(date.getDate() + diff)
  return formatDateToYMD(date)
}

/**
 * Lấy ngày cuối tuần (Sunday) của một date string
 */
export function getWeekEnd(dateStr: string): string {
  const weekStart = getWeekStart(dateStr)
  return addDays(weekStart, 6)
}

/**
 * Lấy ngày đầu tháng
 */
export function getMonthStart(year: number, month: number): string {
  return formatDateToYMD(new Date(year, month - 1, 1))
}

/**
 * Lấy ngày cuối tháng
 */
export function getMonthEnd(year: number, month: number): string {
  return formatDateToYMD(new Date(year, month, 0))
}

/**
 * Format date string thành dạng hiển thị: DD/MM/YYYY
 */
export function formatDateDisplay(dateStr: string): string {
  const date = parseDateInTimezone(dateStr)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

/**
 * Format datetime ISO string thành dạng hiển thị: DD/MM/YYYY HH:MM
 */
export function formatDateTimeDisplay(isoString: string): string {
  const date = new Date(isoString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day}/${month}/${year} ${hours}:${minutes}`
}
