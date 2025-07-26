import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Layout from "@/components/Layout";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
});

export const metadata: Metadata = {
  title: {
    default: "Data Engineer Portfolio",
    template: "%s | Data Engineer Portfolio"
  },
  description: "Portfolio website of a passionate data engineer with 3.5 years of experience in building scalable data pipelines and analytics solutions.",
  keywords: ["data engineer", "data pipeline", "analytics", "ETL", "cloud computing", "big data"],
  authors: [{ name: "Data Engineer" }],
  creator: "Data Engineer",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://your-domain.com",
    title: "Data Engineer Portfolio",
    description: "Portfolio website of a passionate data engineer with 3.5 years of experience",
    siteName: "Data Engineer Portfolio",
  },
  twitter: {
    card: "summary_large_image",
    title: "Data Engineer Portfolio",
    description: "Portfolio website of a passionate data engineer with 3.5 years of experience",
    creator: "@yourusername",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className={inter.className}>
        <Layout>
          {children}
        </Layout>
      </body>
    </html>
  );
}