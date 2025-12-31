import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Kroaddy",
    description: "새로운 방식으로 연결하고, 공유하고, 성장하세요.",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ko">
            <body className="antialiased">
                {children}
            </body>
        </html>
    );
}