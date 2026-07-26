import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { FileItem } from "@/entities/File";

interface FilesState {
    items: FileItem[];
    loading: boolean;
}

const initialState: FilesState = {
    items: [],
    loading: false,
};

const filesSlice = createSlice({
    name: "files",
    initialState,
    reducers: {
        setFiles(
            state,
            action: PayloadAction<FileItem[]>
        ) {
            state.items = action.payload;
        },

        removeFile(
            state,
            action: PayloadAction<string>
        ) {
            state.items = state.items.filter(
                file => file.id !== action.payload
            );
        },

        updateFile(
            state,
            action: PayloadAction<FileItem>
        ) {
            const index = state.items.findIndex(
                file => file.id === action.payload.id
            );

            if (index !== -1) {
                state.items[index] = action.payload;
            }
        },
    },
});

export const {
    setFiles,
    removeFile,
    updateFile,
} = filesSlice.actions;

export default filesSlice.reducer;