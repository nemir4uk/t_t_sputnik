"use client";

import { Container, Card, Row, Col, Button, Badge, Alert } from "react-bootstrap";
import { FilesTable, UploadModal, useFiles } from "@/features/File";
import { AlertsTable, useAlerts } from "@/features/Alerts";
import {useState} from "react";
import {FileItem} from "@/entities/File";
import {deleteFile} from "@/entities/File/model/services/deleteFileService";
import {updateFileTitle} from "@/entities/File/model/services/updateFileTitleService";
import {useAppDispatch} from "@/app/providers/store-provider/config/hooks";
import {removeFile, updateFile} from "@/entities/File/model/slice/fileSlice";
import {removeAlert} from "@/entities/Alerts";
import {ApiError} from "@/shared/api/responseHandler";

export default function FilesPage() {
    // Файлы
    const {
        files,
        isLoading: filesLoading,
        error: filesError,
        reload: reloadFiles,
        addFile,
    } = useFiles();

    // Алерты
    const {
        alerts,
        isLoading: alertsLoading,
        error: alertsError,
        reload: reloadAlerts,
    } = useAlerts();

    const [showModal, setShowModal] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);
    const dispatch = useAppDispatch();

    const handleSave = async (title: string, file: File) => {
        setIsSubmitting(true);
        setSubmitError(null);
        try {
            await addFile(title, file);
            setShowModal(false);
        } catch (e) {
            setSubmitError(e instanceof Error ? e.message : "Неизвестная ошибка");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleRefresh = () => {
        void Promise.all([reloadFiles(), reloadAlerts()]);
    };

    const onDelete = async (file: FileItem) => {
        if (!confirm(`Удалить файл "${file.title}"?`)) {
            return;
        }
        await deleteFile(file.id);
        dispatch(removeFile(file.id));
        dispatch(removeAlert(file.id));
    };

    const onRename = async (
        file: FileItem,
        title: string
    ) => {
        try {
            const updated = await updateFileTitle(
                file.id,
                title,
            );
            dispatch(updateFile(updated));
        } catch (error) {
            if (error instanceof ApiError) {
                switch (error.status) {
                    case 404:
                        alert("Файл не найден");
                        return;
                }
            }
            alert("Не удалось изменить название");
        }
    };

    return (
        <Container fluid className="py-4 px-4 bg-light min-vh-100">
            <Row className="justify-content-center">
                <Col xxl={10} xl={11}>
                    <Card className="shadow-sm border-0 mb-4">
                        <Card.Body className="p-4">
                            <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                                <div>
                                    <h1 className="h3 mb-2">Управление файлами</h1>
                                    <p className="text-secondary mb-0">
                                        Загрузка файлов, просмотр статусов обработки и ленты алертов.
                                    </p>
                                </div>
                                <div className="d-flex gap-2">
                                    <Button variant="outline-secondary" onClick={handleRefresh}>
                                        Обновить
                                    </Button>
                                    <Button variant="primary" onClick={() => setShowModal(true)}>
                                        Добавить файл
                                    </Button>
                                </div>
                            </div>
                        </Card.Body>
                    </Card>

                    {filesError && (
                        <Alert variant="danger" className="shadow-sm">
                            {filesError}
                        </Alert>
                    )}
                    {alertsError && (
                        <Alert variant="danger" className="shadow-sm">
                            {alertsError}
                        </Alert>
                    )}

                    <Card className="shadow-sm border-0 mb-4">
                        <Card.Header className="bg-white border-0 pt-4 px-4">
                            <div className="d-flex justify-content-between align-items-center">
                                <h2 className="h5 mb-0">Файлы</h2>
                                <Badge bg="secondary">{files.length}</Badge>
                            </div>
                        </Card.Header>
                        <Card.Body className="px-4 pb-4">
                            <FilesTable
                                files={files}
                                isLoading={filesLoading}
                                onDelete={onDelete}
                                onRename={onRename}
                            />
                        </Card.Body>
                    </Card>

                    <Card className="shadow-sm border-0">
                        <Card.Header className="bg-white border-0 pt-4 px-4">
                            <div className="d-flex justify-content-between align-items-center">
                                <h2 className="h5 mb-0">Алерты</h2>
                                <Badge bg="secondary">{alerts.length}</Badge>
                            </div>
                        </Card.Header>
                        <Card.Body className="px-4 pb-4">
                            <AlertsTable alerts={alerts} isLoading={alertsLoading} />
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <UploadModal
                show={showModal}
                onClose={() => setShowModal(false)}
                onSave={handleSave}
                isSubmitting={isSubmitting}
                error={submitError}
            />
        </Container>
    );
}