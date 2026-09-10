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
  useUser,
} from "@clerk/nextjs";
import {
  Flame,
  History,
  PlusCircle,
  Zap,
  User,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Plug,
} from "lucide-react";
import { checkBackendHealth } from "../lib/api";
import { useAppAuth } from "./AuthProvider";
import { getMcpActiveCount } from "../lib/mcp-state";

function ClerkAuthSection() {
  const { user, isLoaded } = useUser();
  return (
    <>
      <SignedOut>
        <div className="space-y-2 px-2">
          <SignInButton mode="modal">
            <button className="w-full px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors text-left">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="w-full px-3 py-2 text-sm font-semibold rounded-lg bg-rose-600 hover:bg-rose-500 text-white shadow-md shadow-rose-600/20 transition-all text-center">
              Sign Up
            </button>
          </SignUpButton>
        </div>
      </SignedOut>

      <SignedIn>
        <div className="flex items-center gap-3 px-3 py-2">
          <UserButton
            afterSignOutUrl="/"
            appearance={{
              elements: {
                userButtonAvatarBox:
                  "w-8 h-8 ring-2 ring-rose-500/40 hover:ring-rose-500 transition-all",
              },
            }}
          />
          {isLoaded && user && (
            <div className="flex flex-col min-w-0">
              <span className="text-sm text-white font-medium truncate">
                {user.firstName ||
                  user.emailAddresses[0]?.emailAddress?.split("@")[0]}
              </span>
              <span className="text-[10px] text-slate-400 truncate">Founder</span>
            </div>
          )}
        </div>
      </SignedIn>
    </>
  );
}

interface NavItemProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  badge?: React.ReactNode;
}

function NavItem({ href, icon, label, isActive, badge }: NavItemProps) {
  return (
    <Link
      href={href}
      className={`flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group ${
        isActive
          ? "bg-rose-950/50 text-rose-400 border border-rose-500/30 shadow-sm shadow-rose-950/30"
          : "text-slate-300 hover:text-white hover:bg-white/5 border border-transparent"
      }`}
    >
      <div className="flex items-center gap-3">
        <span
          className={`${
            isActive
              ? "text-rose-400"
              : "text-slate-400 group-hover:text-slate-200"
          } transition-colors`}
        >
          {icon}
        </span>
        <span>{label}</span>
      </div>
      {badge}
    </Link>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const { isClerkConfigured } = useAppAuth();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [mcpCount, setMcpCount] = useState(3);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

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

  useEffect(() => {
    setMcpCount(getMcpActiveCount());
    const handler = () => setMcpCount(getMcpActiveCount());
    window.addEventListener("mcp-config-changed", handler);
    return () => window.removeEventListener("mcp-config-changed", handler);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const navItems = [
    {
      href: "/pitch",
      icon: <PlusCircle className="w-5 h-5" />,
      label: "New Pitch",
    },
    {
      href: "/history",
      icon: <History className="w-5 h-5" />,
      label: "Pitch History",
    },
    {
      href: "/connectors",
      icon: <Plug className="w-5 h-5" />,
      label: "MCP Connectors",
      badge: (
        <span
          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
            mcpCount > 0
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              : "bg-slate-800 text-slate-400 border border-slate-700"
          }`}
        >
          {mcpCount} ON
        </span>
      ),
    },
  ];

  return (
    <>
      {/* Mobile Toggle Button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 rounded-lg bg-darkbg-800 border border-white/10 text-slate-300 hover:text-white shadow-xl"
        aria-label="Toggle sidebar"
      >
        {mobileOpen ? (
          <ChevronLeft className="w-5 h-5" />
        ) : (
          <LayoutDashboard className="w-5 h-5" />
        )}
      </button>

      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 z-40 h-screen flex flex-col bg-darkbg-950/95 backdrop-blur-xl border-r border-white/10 transition-all duration-300 ease-in-out ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        } ${collapsed ? "w-[68px]" : "w-64"}`}
      >
        {/* Brand */}
        <div className="p-4 border-b border-white/5">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-rose-600 to-rose-500 flex items-center justify-center shadow-lg shadow-rose-600/30 group-hover:scale-105 transition-transform duration-200 shrink-0">
              <Flame className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col min-w-0">
                <span className="font-bold text-sm tracking-tight text-white group-hover:text-rose-400 transition-colors truncate">
                  Devil&apos;s Advocate
                </span>
                <span className="text-[9px] text-slate-500 font-mono tracking-wider uppercase">
                  AI Panel Gauntlet
                </span>
              </div>
            )}
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
          {!collapsed && (
            <span className="block text-[10px] font-semibold text-slate-500 uppercase tracking-widest px-3 mb-3">
              Navigation
            </span>
          )}
          {navItems.map((item) => (
            <NavItem
              key={item.href}
              href={item.href}
              icon={item.icon}
              label={collapsed ? "" : item.label}
              isActive={pathname === item.href}
              badge={collapsed ? undefined : item.badge}
            />
          ))}
        </nav>

        {/* Bottom Section */}
        <div className="mt-auto border-t border-white/5 p-3 space-y-3">
          {/* API Status */}
          <div
            className={`flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/5 text-xs font-mono ${
              collapsed ? "justify-center" : ""
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                backendOnline === true
                  ? "bg-emerald-400 animate-pulse"
                  : backendOnline === false
                  ? "bg-rose-500"
                  : "bg-amber-400"
              }`}
            />
            {!collapsed && (
              <span className="text-slate-400">
                {backendOnline === true
                  ? "API Online"
                  : backendOnline === false
                  ? "API Offline"
                  : "Checking..."}
              </span>
            )}
          </div>

          {/* Auth */}
          {isClerkConfigured ? (
            !collapsed && <ClerkAuthSection />
          ) : (
            <div
              className={`flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/5 text-xs text-slate-300 ${
                collapsed ? "justify-center" : ""
              }`}
            >
              <User className="w-3.5 h-3.5 text-rose-400 shrink-0" />
              {!collapsed && <span>Founder Mode</span>}
            </div>
          )}

          {/* Collapse Toggle (desktop only) */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden md:flex items-center justify-center w-full p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>
      </aside>
    </>
  );
}
