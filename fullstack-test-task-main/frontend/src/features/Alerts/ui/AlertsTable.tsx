import { Table, Badge, Spinner } from "react-bootstrap";
import { AlertItem } from "@/entities/Alerts";
import { formatDate } from "@/shared/lib/dateFormatter";
import { getLevelVariant } from "@/entities/File";

type Props = {
    alerts: AlertItem[];
    isLoading: boolean;
};

export const AlertsTable = ({ alerts, isLoading }: Props) => {
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
                    <th>ID</th>
                    <th>File ID</th>
                    <th>Уровень</th>
                    <th>Сообщение</th>
                    <th>Создан</th>
                </tr>
                </thead>
                <tbody>
                {alerts.length === 0 ? (
                    <tr>
                        <td colSpan={5} className="text-center py-4 text-secondary">
                            Алертов пока нет
                        </td>
                    </tr>
                ) : (
                    alerts.map((a) => (
                        <tr key={a.id}>
                            <td>{a.id}</td>
                            <td className="small">{a.file_id}</td>
                            <td>
                                <Badge bg={getLevelVariant(a.level)}>{a.level}</Badge>
                            </td>
                            <td>{a.message}</td>
                            <td>{formatDate(a.created_at)}</td>
                        </tr>
                    ))
                )}
                </tbody>
            </Table>
        </div>
    );
};