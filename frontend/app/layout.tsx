import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Devil's Advocate Panel | Pitch Your Idea. Get Grilled by AI Investors",
  description: "Stateful multi-agent startup stress-testing platform powered by LangGraph, LangChain, Multi-Agent RAG, and Gemini/Groq.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased bg-darkbg-900 text-slate-100 min-h-screen selection:bg-rose-500/30 selection:text-rose-200">
        <div className="fixed inset-0 pointer-events-none z-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-rose-950/20 via-darkbg-900 to-darkbg-900" />
        <div className="relative z-10 flex flex-col min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
