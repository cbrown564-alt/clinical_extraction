import type { Metadata } from "next";
import { Suspense } from "react";
import { Inter, Source_Serif_4, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Providers from "./providers";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const sourceSerif = Source_Serif_4({
  variable: "--font-source-serif",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "600"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Clinical Extraction Explorer",
    template: "%s | Clinical Extraction Explorer",
  },
  description:
    "Evidence-first workspace for inspecting, evaluating, and assuring clinical extraction systems.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${sourceSerif.variable} ${jetbrainsMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="h-screen flex flex-col overflow-hidden bg-background text-foreground">
        <Providers>
          <Suspense
            fallback={
              <header
                aria-label="Application"
                className="h-[89px] shrink-0 border-b border-border bg-surface shadow-sm"
              />
            }
          >
            <Navbar />
          </Suspense>
          <main className="flex-1 min-h-0">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
