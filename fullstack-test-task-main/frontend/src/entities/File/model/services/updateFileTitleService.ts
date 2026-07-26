import {FileItem} from "@/entities/File";
import {API_BASE_URL} from "@/app/config";
import {handleResponse} from "@/shared/api/responseHandler";

export async function updateFileTitle(
    fileId: string,
    title: string
): Promise<FileItem> {
    const resp = await fetch(`${API_BASE_URL}/files/${fileId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            title,
        }),
    });
    return handleResponse<FileItem>(resp);
}