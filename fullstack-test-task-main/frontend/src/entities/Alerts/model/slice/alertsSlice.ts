import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { AlertItem } from "@/entities/Alerts";

interface AlertState {
    items: AlertItem[];
    loading: boolean;
}

const initialState: AlertState = {
    items: [],
    loading: false,
};

const alertSlice = createSlice({
    name: "alerts",
    initialState,
    reducers: {
        setAlert(
            state,
            action: PayloadAction<AlertItem[]>
        ) {
            state.items = action.payload;
        },

        removeAlert(
            state,
            action: PayloadAction<string>
        ) {
            state.items = state.items.filter(
                alert => alert.file_id !== action.payload
            );
        },

        updateAlert(
            state,
            action: PayloadAction<AlertItem>
        ) {
            const index = state.items.findIndex(
                alert => alert.id === action.payload.id
            );

            if (index !== -1) {
                state.items[index] = action.payload;
            }
        },
    },
});

export const {
    setAlert,
    removeAlert,
    updateAlert,
} = alertSlice.actions;

export default alertSlice.reducer;