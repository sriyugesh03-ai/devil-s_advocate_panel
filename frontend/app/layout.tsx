import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import Navbar from "../components/Navbar";
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
    <ClerkProvider
      appearance={{
        variables: {
          colorPrimary: "#e11d48", // rose-600
          colorBackground: "#09090b", // darkbg-900
          colorText: "#f1f5f9",
          colorInputBackground: "#18181b",
          colorInputText: "#f8fafc",
          borderRadius: "0.75rem",
        },
        elements: {
          card: "bg-darkbg-900/95 border border-white/10 shadow-2xl backdrop-blur-xl",
          headerTitle: "text-white font-bold",
          headerSubtitle: "text-slate-400",
          socialButtonsBlockButton: "bg-white/5 border border-white/10 text-white hover:bg-white/10",
          formButtonPrimary: "bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/30",
          footerActionLink: "text-rose-400 hover:text-rose-300",
        },
      }}
    >
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
            <Navbar />
            <div className="flex-1 flex flex-col">
              {children}
            </div>
          </div>
        </body>
      </html>
    </ClerkProvider>
  );
}

