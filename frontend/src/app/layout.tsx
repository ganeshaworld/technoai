import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Technopie AI — World-Class AI Personal & Executive Assistant SaaS',
  description:
    'Your AI. Your Assistant. Your Productivity. An elite AI personal and executive assistant developed by Technopie Consultant Pvt. Ltd.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#070B14] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
