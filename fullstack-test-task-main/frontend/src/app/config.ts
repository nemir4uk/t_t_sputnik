function parseEnv() {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    const maxFileSize = process.env.NEXT_PUBLIC_MAX_FILE_SIZE;
    const allowedExtensions = process.env.NEXT_PUBLIC_ALLOWED_EXTENSIONS;

    if (!apiBaseUrl) {
        throw new Error("Переменная NEXT_PUBLIC_API_BASE_URL обязательна");
    }
    try {
        new URL(apiBaseUrl);
    } catch {
        throw new Error("Переменная NEXT_PUBLIC_API_BASE_URL должна быть корректным URL");
    }

    if (!maxFileSize) {
        throw new Error("Переменная MAX_FILE_SIZE обязательна");
    }
    const fileSizeNum = Number(maxFileSize);
    if (isNaN(fileSizeNum) || !Number.isInteger(fileSizeNum) || fileSizeNum <= 0) {
        throw new Error("Переменная MAX_FILE_SIZE должна быть положительным целым числом");
    }

    if (!allowedExtensions) {
        throw new Error("Переменная ALLOWED_EXTENSIONS обязательна");
    }
    const extensionsArray = allowedExtensions.split(',').map((s) => s.trim());

    return {
        API_BASE_URL: apiBaseUrl,
        MAX_FILE_SIZE: fileSizeNum,
        ALLOWED_EXTENSIONS: extensionsArray as readonly string[],
    };
}

const env = parseEnv();

export const API_BASE_URL = env.API_BASE_URL;
export const MAX_FILE_SIZE = env.MAX_FILE_SIZE;
export const ALLOWED_EXTENSIONS = env.ALLOWED_EXTENSIONS;