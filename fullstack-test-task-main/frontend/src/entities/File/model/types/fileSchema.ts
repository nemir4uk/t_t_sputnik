export type FileItem = {
    id: string;
    title: string;
    original_name: string;
    mime_type: string;
    size: number;
    processing_status: string;
    scan_status: string | null;
    scan_details: string | null;
    metadata_json: Record<string, unknown> | null;
    requires_attention: boolean;
    created_at: string;
    updated_at: string;
};

export const getProcessingVariant = (status: string) => {
    switch (status) {
        case "failed":      return "danger";
        case "processing":  return "warning";
        case "processed":   return "success";
        default:            return "secondary";
    }
};

export const getLevelVariant = (level: string) => {
    switch (level) {
        case "critical": return "danger";
        case "warning":  return "warning";
        default:         return "success";
    }
};