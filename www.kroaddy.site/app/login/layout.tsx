import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "로그인 | My App",
    description: "카카오 로그인을 통해 서비스를 이용하세요",
};

export default function LoginLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <>
            {children}
        </>
    );
}

