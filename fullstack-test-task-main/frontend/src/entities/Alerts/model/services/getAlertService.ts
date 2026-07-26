import { AlertItem } from "@/entities/Alerts";
import { API_BASE_URL } from "@/app/config";

export async function getAlerts(): Promise<AlertItem[]> {
    const resp = await fetch(`${API_BASE_URL}/alerts`, { cache: "no-store" });
    if (!resp.ok) {
        throw new Error("Не удалось загрузить алерты");
    }
    return resp.json();
}