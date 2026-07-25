import { FileItem } from "@/entities/File";
import { API_BASE_URL } from "@/app/config";

export async function getFiles(): Promise<FileItem[]> {
    const resp = await fetch(`${API_BASE_URL}/files`, { cache: "no-store" });
    if (!resp.ok) {
        throw new Error("Не удалось загрузить файлы");
    }
    return resp.json();
}