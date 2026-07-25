import { useCallback, useEffect, useState } from "react";
import { FileItem } from "@/entities/File";
import { getFiles } from "@/entities/File/model/services/getFileService";
import { uploadFile } from "@/entities/File/model/services/uploadFileService";

export const useFiles = () => {
    const [files, setFiles] = useState<FileItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getFiles();
            setFiles(data);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Неизвестная ошибка");
        } finally {
            setIsLoading(false);
        }
    }, []);

    const addFile = useCallback(
        async (title: string, file: File) => {
            setError(null);
            try {
                await uploadFile(title, file);
                await load();
            } catch (e) {
                setError(e instanceof Error ? e.message : "Неизвестная ошибка");
                throw e;
            }
        },
        [load]
    );

    useEffect(() => {
        void load();
    }, [load]);

    return { files, isLoading, error, reload: load, addFile };
};