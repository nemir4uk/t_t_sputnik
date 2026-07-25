import { API_BASE_URL } from "@/app/config";

export async function uploadFile(
    title: string,
    file: File
): Promise<void> {
    const formData = new FormData();
    formData.append("title", title.trim());
    formData.append("file", file);

    try {
        const resp = await fetch(`${API_BASE_URL}/files`, {
            method: "POST",
            body: formData,
        });

        if (!resp.ok) {
            if (resp.status === 413) throw new Error("Файл слишком большой для загрузки");
            if (resp.status === 401) throw new Error("Сессия истекла. Авторизуйтесь заново");
            if (resp.status === 403) throw new Error("У вас нет прав для загрузки файлов");
            throw new Error(`Ошибка сервера: статус ${resp.status}`);
        }

        return await resp.json();
    } catch (err) {
        if (err instanceof TypeError) {
            throw new Error("Не удалось связаться с сервером. Проверьте интернет или настройки CORS");
        }
        throw err;
    }
}