import { useCallback, useEffect, useState } from "react";
import { FileItem } from "@/entities/File";
import { getFiles } from "@/entities/File/model/services/getFileService";
import { uploadFile } from "@/entities/File/model/services/uploadFileService";
import {useAppDispatch, useAppSelector} from "@/app/providers/store-provider/config/hooks";
import {setFiles} from "@/entities/File/model/slice/fileSlice";

export const useFiles = () => {
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const dispatch = useAppDispatch();
    const files = useAppSelector(
        state => state.files.items
    );

    const load = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getFiles();
            dispatch(setFiles(data));
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