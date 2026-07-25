import { useCallback, useEffect, useState } from "react";
import { AlertItem, getAlerts } from "@/entities/Alerts";


export const useAlerts = () => {
    const [alerts, setAlerts] = useState<AlertItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getAlerts();
            setAlerts(data);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Не удалось загрузить алерты");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        void load();
    }, [load]);

    return { alerts, isLoading, error, reload: load };
};