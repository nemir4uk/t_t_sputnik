export class ApiError extends Error {
    constructor(
        message: string,
        public readonly status: number,
        public readonly detail?: string,
    ) {
        super(message);
        this.name = "ApiError";
    }
    get isClientError() {
        return this.status >= 400 && this.status < 500;
    }
    get isServerError() {
        return this.status >= 500;
    }
    get isNotFound() {
        return this.status === 404;
    }
    get isConflict() {
        return this.status === 409;
    }
    get isValidationError() {
        return this.status === 422;
    }
}


export async function handleResponse<T>(resp: Response): Promise<T> {
    if (!resp.ok) {
        let message = "Произошла ошибка при выполнении запроса";
        try {
            const data = await resp.json();
            if (typeof data.detail === "string") {
                message = data.detail;
            }
            else if (Array.isArray(data.detail)) {
                message = data.detail
                    .map((item: any) => item.msg)
                    .join(", ");
            }
        } catch {
            // ignore
        }
        throw new ApiError(
            message,
            resp.status,
            message
        );
    }
    if (resp.status === 204) {
        return undefined as T;
    }
    return resp.json();
}