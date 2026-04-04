import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Syntriage",
  description: "Advanced AI Clinical Coordinator",
  icons: {
    icon: [
      { url: "/logo.png", href: "/logo.png" },
    ],
    apple: [
      { url: "/logo.png", href: "/logo.png" },
    ],
    shortcut: ["/logo.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Use BACKEND_URL at runtime (Cloud Run will provide this)
  const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
  
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <script
          dangerouslySetInnerHTML={{
            __html: `window.BACKEND_URL = "${backendUrl}";`,
          }}
        />
        {children}
      </body>
    </html>
  );
}
