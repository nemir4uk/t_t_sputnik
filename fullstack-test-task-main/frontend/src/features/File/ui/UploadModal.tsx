import {
    Modal,
    Form,
    Button,
    Alert,
    Spinner,
} from "react-bootstrap";
import { useState, SyntheticEvent } from "react";
import { formatSize } from "@/shared/lib/sizeFormatter";
import {ALLOWED_EXTENSIONS, MAX_FILE_SIZE} from "@/app/config";


type Props = {
    show: boolean;
    onClose: () => void;
    onSave: (title: string, file: File) => Promise<void>;
    isSubmitting: boolean;
    error?: string | null;
};

export const UploadModal = ({
                                show,
                                onClose,
                                onSave,
                                isSubmitting,
                                error,
                            }: Props) => {
    const [title, setTitle] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [localError, setLocalError] = useState<string | null>(null);

    const handleSubmit = async (e: SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!title.trim() || !file) {
            setLocalError("Укажите название и выберите файл");
            return;
        }

        const fileName = file.name.toLowerCase();
        const hasValidExtension = ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext));

        if (!hasValidExtension) {
            setLocalError(`Неверный формат файла. Разрешены только: ${ALLOWED_EXTENSIONS.join(", ")}`);
            return;
        }

        if (file.size > MAX_FILE_SIZE) {
            setLocalError(`Файл слишком большой. Максимальный размер: ${formatSize(MAX_FILE_SIZE)} (ваш файл: ${formatSize(file.size)})`);
            return;
        }

        setLocalError(null);
        await onSave(title, file);
    };

    const handleHide = () => {
        setTitle("");
        setFile(null);
        setLocalError(null);
        onClose();
    };

    return (
        <Modal show={show} onHide={handleHide} centered>
            <Form onSubmit={handleSubmit}>
                <Modal.Header closeButton>
                    <Modal.Title>Добавить файл</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {(error || localError) && (
                        <Alert variant="danger">{error ?? localError}</Alert>
                    )}
                    <Form.Group className="mb-3">
                        <Form.Label>Название</Form.Label>
                        <Form.Control
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Например, Договор с подрядчиком"
                        />
                    </Form.Group>
                    <Form.Group>
                        <Form.Label>Файл</Form.Label>
                        <Form.Control
                            type="file"
                            accept={ALLOWED_EXTENSIONS.join(",")}
                            onChange={(e) => {
                                setFile((e.target as HTMLInputElement).files?.[0] ?? null);
                                setLocalError(null);
                            }}
                        />
                        <Form.Text className="text-muted">
                            Максимальный размер: {formatSize(MAX_FILE_SIZE)}.
                            Форматы: {ALLOWED_EXTENSIONS.join(", ")}
                        </Form.Text>
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="outline-secondary" onClick={handleHide}>
                        Отмена
                    </Button>
                    <Button type="submit" variant="primary" disabled={isSubmitting}>
                        {isSubmitting ? (
                            <div className="d-flex align-items-center gap-2">
                                <Spinner
                                    as="span"
                                    animation="border"
                                    size="sm"
                                    role="status"
                                    aria-hidden="true"
                                />
                                <span>Сохранение...</span>
                            </div>
                        ) : (
                            "Сохранить"
                        )}
                    </Button>
                </Modal.Footer>
            </Form>
        </Modal>
    );
};