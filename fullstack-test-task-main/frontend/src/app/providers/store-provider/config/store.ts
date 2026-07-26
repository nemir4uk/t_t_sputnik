import { configureStore } from "@reduxjs/toolkit"
import { combineReducers } from "redux"

import fileReducer from "@/entities/File/model/slice/fileSlice";
import alertReducer from "@/entities/Alerts/model/slice/alertsSlice";

export const rootReducer = combineReducers({
  // auth: authReducer,
})

const store = configureStore({
  reducer: {
      files: fileReducer,
      alerts: alertReducer,
  },
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
  devTools: true,
})

export default store

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
