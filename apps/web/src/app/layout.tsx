import type { Metadata } from "next";
import { Cormorant_Garamond, Sora } from "next/font/google";

import { AppProviders } from "@/providers/AppProviders";

import "./globals.css";

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
  display: "swap",
});

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-cormorant",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Sarathi AI",
  description:
    "An AI guide grounded in the Bhagavad Gita — compassionate, cited, and never claiming to be Krishna.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${sora.variable} ${cormorant.variable} antialiased`}>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
