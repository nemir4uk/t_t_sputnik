import { API_BASE_URL } from "@/app/config";
import {handleResponse} from "@/shared/api/responseHandler";

export async function deleteFile(fileId: string): Promise<void> {
    const resp = await fetch(`${API_BASE_URL}/files/${fileId}`, {
        method: "DELETE",
    });

    return handleResponse<void>(resp);
}