const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getAvailableSlots(
  clinicId: number,
  onDate: string
): Promise<string[]> {
  const response = await fetch(
    `${API_BASE_URL}/clinics/${clinicId}/available-slots?on_date=${onDate}`
  );
  if (!response.ok) {
    throw new Error(`Failed to load available slots (status ${response.status})`);
  }
  return response.json();
}