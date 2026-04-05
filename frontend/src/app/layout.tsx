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

export const dynamic = "force-dynamic";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Use BACKEND_URL at runtime (Cloud Run will provide this)
  const backendUrl = process.env.BACKEND_URL || "";
  
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.BACKEND_URL = "${backendUrl}";
              if (!window.BACKEND_URL) {
                console.error("SYNTRIAGE ERROR: BACKEND_URL environment variable is MISSING in Cloud Run!");
              } else {
                console.log("SYNTRIAGE SUCCESS: Connecting to backend at " + window.BACKEND_URL);
              }
            `,
          }}
        />
        {children}
      </body>
    </html>
  );
}
