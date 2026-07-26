import { useCallback, useEffect, useState } from "react";
import {getAlerts, setAlert} from "@/entities/Alerts";
import {useAppDispatch, useAppSelector} from "@/app/providers/store-provider/config/hooks";


export const useAlerts = () => {
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const dispatch = useAppDispatch();
    const alerts = useAppSelector(
        state => state.alerts.items
    );

    const load = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getAlerts();
            dispatch(setAlert(data));
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