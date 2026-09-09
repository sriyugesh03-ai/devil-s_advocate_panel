"use client";

import React, { createContext, useContext } from "react";
import { ClerkProvider } from "@clerk/nextjs";

interface AuthContextType {
  isClerkConfigured: boolean;
}

const AuthContext = createContext<AuthContextType>({ isClerkConfigured: false });

export const useAppAuth = () => useContext(AuthContext);

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  
  // Verify that the key is a real Clerk publishable key and not a dummy/placeholder
  const isRealClerkKey = 
    Boolean(publishableKey) && 
    !publishableKey?.includes("placeholder") && 
    publishableKey !== "pk_test_Y2xlcmsuZGV2aWxzYWR2b2NhdGUuZGV2JA" &&
    (publishableKey?.startsWith("pk_test_") || publishableKey?.startsWith("pk_live_"));

  if (isRealClerkKey) {
    return (
      <ClerkProvider
        publishableKey={publishableKey}
        appearance={{
          variables: {
            colorPrimary: "#e11d48",
            colorBackground: "#09090b",
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
        <AuthContext.Provider value={{ isClerkConfigured: true }}>
          {children}
        </AuthContext.Provider>
      </ClerkProvider>
    );
  }

  // Graceful fallback when Clerk API keys have not been configured yet (avoids DNS errors)
  return (
    <AuthContext.Provider value={{ isClerkConfigured: false }}>
      {children}
    </AuthContext.Provider>
  );
}
