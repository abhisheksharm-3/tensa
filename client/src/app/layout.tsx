import type { Metadata } from "next";
import { JetBrains_Mono, Space_Grotesk } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Tensa — paste a link, get the file",
  description:
    "Self-hosted, ad-free media toolkit. Download, extract audio, convert, or transcribe from any link.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const apiBase = process.env.PUBLIC_API_URL ?? "http://localhost:8000";
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <script
          // Runtime-injected browser API base (not build-time inlined), read by getApiBase().
          // biome-ignore lint/security/noDangerouslySetInnerHtml: our own env, JSON-stringified
          dangerouslySetInnerHTML={{
            __html: `window.__TENSA_API_BASE__=${JSON.stringify(apiBase)}`,
          }}
        />
      </head>
      <body
        className={`${spaceGrotesk.variable} ${jetbrains.variable} font-sans antialiased min-h-[100dvh]`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
