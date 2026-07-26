import type { Metadata } from "next";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container } from "react-bootstrap";
import {Providers} from "@/app/providers";

export async function generateMetadata(): Promise<Metadata> {
    return {
        title: 'Тестовое задание Fullstack',
        description: 'Тестовое задание Fullstack',
    };
}

export default async function RootLayout({
                                             children
                                         }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang='ru'>
        <head>
            <link rel="icon" href="/public/favicon.ico" sizes="any" />
        </head>
        <body>
        <Providers>
        <Container fluid className='p-0'>
            {children}
        </Container>
        </Providers>
        </body>
        </html>
    );
}