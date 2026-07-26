import { Table, Badge, Button, Spinner, Form } from "react-bootstrap";
import { FileItem, getProcessingVariant } from "@/entities/File";
import { formatDate } from "@/shared/lib/dateFormatter";
import { formatSize } from "@/shared/lib/sizeFormatter";
import {API_BASE_URL} from "@/app/config";
import {useState} from "react";


type Props = {
    files: FileItem[];
    isLoading: boolean;
    onDelete: (file: FileItem) => void;
    onRename: (file: FileItem, title: string) => void;
};

export const FilesTable = ({ files, isLoading, onDelete, onRename }: Props) => {
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editingTitle, setEditingTitle] = useState("");
    const [isSaving, setIsSaving] = useState(false);

    const startEditing = (file: FileItem) => {
        setEditingId(file.id);
        setEditingTitle(file.title);
    };

    const cancelEditing = () => {
        setEditingId(null);
        setEditingTitle("");
    };

    const saveEditing = async (file: FileItem) => {
        if (!editingTitle.trim()) {
            return;
        }
        setIsSaving(true);
        try {
            onRename(file, editingTitle.trim());
            cancelEditing();
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="d-flex justify-content-center py-5">
                <Spinner animation="border" />
            </div>
        );
    }

    return (
        <div className="table-responsive">
            <Table hover bordered className="align-middle mb-0">
                <thead className="table-light">
                <tr>
                    <th>Название</th>
                    <th>Файл</th>
                    <th>MIME</th>
                    <th>Размер</th>
                    <th>Статус</th>
                    <th>Проверка</th>
                    <th>Создан</th>
                    <th></th>
                </tr>
                </thead>
                <tbody>
                {files.length === 0 ? (
                    <tr>
                        <td colSpan={8} className="text-center py-4 text-secondary">
                            Файлы пока не загружены
                        </td>
                    </tr>
                ) : (
                    files.map((file) => (
                        <tr key={file.id}>
                            <td>
                                {editingId === file.id ? (
                                    <div className="d-flex gap-2">
                                        <Form.Control
                                            size="sm"
                                            value={editingTitle}
                                            onChange={(e) =>
                                                setEditingTitle(e.target.value)
                                            }
                                            onKeyDown={(e) => {
                                                if (e.key === "Enter") {
                                                    void saveEditing(file);
                                                }

                                                if (e.key === "Escape") {
                                                    cancelEditing();
                                                }
                                            }}
                                            autoFocus
                                        />
                                        <Button
                                            variant="success"
                                            size="sm"
                                            disabled={isSaving}
                                            onClick={() => void saveEditing(file)}
                                        >
                                            ✓
                                        </Button>
                                        <Button
                                            variant="secondary"
                                            size="sm"
                                            disabled={isSaving}
                                            onClick={cancelEditing}
                                        >
                                            ✕
                                        </Button>
                                    </div>
                                ) : (
                                    <>
                                        <div
                                            className="fw-semibold"
                                            style={{
                                                cursor: "pointer"
                                            }}
                                            onClick={() => startEditing(file)}
                                            title="Нажмите для изменения"
                                        >
                                            {file.title}
                                        </div>
                                        <div className="small text-secondary">
                                            {file.id}
                                        </div>
                                    </>
                                )}
                            </td>
                            <td>{file.original_name}</td>
                            <td>{file.mime_type}</td>
                            <td>{formatSize(file.size)}</td>
                            <td>
                                <Badge bg={getProcessingVariant(file.processing_status)}>
                                    {file.processing_status}
                                </Badge>
                            </td>
                            <td>
                                <div className="d-flex flex-column gap-1">
                                    <Badge bg={file.requires_attention ? "warning" : "success"}>
                                        {file.scan_status ?? "pending"}
                                    </Badge>
                                    <span className="small text-secondary">
                      {file.scan_details ?? "Ожидает обработки"}
                    </span>
                                </div>
                            </td>
                            <td>{formatDate(file.created_at)}</td>
                            <td className="text-nowrap">
                                <div className="d-flex gap-2">
                                    <Button
                                        as="a"
                                        href={`${API_BASE_URL}/files/${file.id}/download`}
                                        variant="outline-primary"
                                        size="sm"
                                    >
                                        Скачать
                                    </Button>

                                    <Button
                                        variant="outline-danger"
                                        size="sm"
                                        onClick={() => onDelete(file)}
                                    >
                                        Удалить
                                    </Button>
                                </div>
                            </td>
                        </tr>
                    ))
                )}
                </tbody>
            </Table>
        </div>
    );
};