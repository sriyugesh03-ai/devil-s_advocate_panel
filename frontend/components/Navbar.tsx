"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { 
  SignInButton, 
  SignUpButton, 
  SignedIn, 
  SignedOut, 
  UserButton,
  useUser
} from "@clerk/nextjs";
import { 
  Flame, 
  History, 
  PlusCircle, 
  Activity, 
  ShieldCheck, 
  Menu, 
  X,
  User 
} from "lucide-react";
import { checkBackendHealth } from "../lib/api";
import { useAppAuth } from "./AuthProvider";

function ClerkAuthButtons() {
  const { user, isLoaded } = useUser();
  return (
    <>
      <SignedOut>
        <SignInButton mode="modal">
          <button className="px-3 py-1.5 text-sm font-medium text-slate-300 hover:text-white transition-colors">
            Sign In
          </button>
        </SignInButton>
        <SignUpButton mode="modal">
          <button className="px-3.5 py-1.5 text-sm font-semibold rounded-lg bg-rose-600 hover:bg-rose-500 text-white shadow-md shadow-rose-600/20 transition-all">
            Sign Up
          </button>
        </SignUpButton>
      </SignedOut>

      <SignedIn>
        <div className="flex items-center gap-3">
          {isLoaded && user && (
            <span className="text-xs text-slate-300 font-medium hidden lg:inline-block">
              {user.firstName || user.emailAddresses[0]?.emailAddress?.split("@")[0]}
            </span>
          )}
          <UserButton 
            afterSignOutUrl="/" 
            appearance={{
              elements: {
                userButtonAvatarBox: "w-8 h-8 ring-2 ring-rose-500/40 hover:ring-rose-500 transition-all",
              }
            }}
          />
        </div>
      </SignedIn>
    </>
  );
}

export default function Navbar() {
  const pathname = usePathname();
  const { isClerkConfigured } = useAppAuth();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    checkBackendHealth()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));

    const interval = setInterval(() => {
      checkBackendHealth()
        .then(() => setBackendOnline(true))
        .catch(() => setBackendOnline(false));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-darkbg-900/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-rose-600 to-rose-500 flex items-center justify-center shadow-lg shadow-rose-600/30 group-hover:scale-105 transition-transform duration-200">
            <Flame className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base tracking-tight text-white group-hover:text-rose-400 transition-colors">
              Devil's Advocate
            </span>
            <span className="text-[10px] text-slate-400 font-mono tracking-wider -mt-1 uppercase">
              AI Panel Gauntlet
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-6">
          <Link
            href="/pitch"
            className={`flex items-center gap-2 text-sm font-medium transition-colors px-3 py-1.5 rounded-lg ${
              pathname === "/pitch"
                ? "text-rose-400 bg-rose-950/40 border border-rose-500/30"
                : "text-slate-300 hover:text-white hover:bg-white/5"
            }`}
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Pitch</span>
          </Link>

          <Link
            href="/history"
            className={`flex items-center gap-2 text-sm font-medium transition-colors px-3 py-1.5 rounded-lg ${
              pathname === "/history"
                ? "text-rose-400 bg-rose-950/40 border border-rose-500/30"
                : "text-slate-300 hover:text-white hover:bg-white/5"
            }`}
          >
            <History className="w-4 h-4" />
            <span>Pitch History</span>
          </Link>
        </nav>

        {/* Right Section: Backend Status + Clerk Auth */}
        <div className="hidden md:flex items-center gap-4">
          {/* Live Status Indicator */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                backendOnline === true
                  ? "bg-emerald-400 animate-pulse"
                  : backendOnline === false
                  ? "bg-rose-500"
                  : "bg-amber-400"
              }`}
            />
            <span className="text-slate-400">
              {backendOnline === true ? "API Online" : backendOnline === false ? "API Offline" : "Checking..."}
            </span>
          </div>

          {/* Clerk Auth Integration */}
          <div className="flex items-center gap-3 pl-2 border-l border-white/10">
            {isClerkConfigured ? (
              <ClerkAuthButtons />
            ) : (
              <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300" title="Connect Clerk keys in .env.local to enable account login">
                <User className="w-3.5 h-3.5 text-rose-400" />
                <span>Founder Mode</span>
              </div>
            )}
          </div>
        </div>

        {/* Mobile menu button */}
        <div className="flex md:hidden items-center gap-2">
          {isClerkConfigured && <ClerkAuthButtons />}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg bg-white/5 text-slate-300 hover:text-white"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden px-4 pt-2 pb-6 space-y-3 bg-darkbg-900 border-b border-white/10">
          <Link
            href="/pitch"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-200 hover:bg-white/5"
          >
            <PlusCircle className="w-4 h-4 text-rose-400" />
            <span>New Pitch</span>
          </Link>

          <Link
            href="/history"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-200 hover:bg-white/5"
          >
            <History className="w-4 h-4 text-rose-400" />
            <span>Pitch History</span>
          </Link>

          <div className="pt-3 border-t border-white/10 flex flex-col gap-2">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="w-full py-2 text-center text-sm font-medium text-slate-200 bg-white/5 rounded-lg">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="w-full py-2 text-center text-sm font-semibold bg-rose-600 text-white rounded-lg">
                  Sign Up
                </button>
              </SignUpButton>
            </SignedOut>
          </div>
        </div>
      )}
    </header>
  );
}
