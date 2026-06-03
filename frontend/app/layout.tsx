import type { Metadata } from "next";
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
  title: "Clinical Extraction Observatory",
  description:
    "Interactive lens for hybrid clinical-extraction pipelines. Inspect, compare, and understand stage-by-stage extraction.",
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
    >
      <body className="h-screen flex flex-col overflow-hidden bg-background text-foreground">
        <Providers>
          <Navbar />
          <main className="flex-1 min-h-0">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
