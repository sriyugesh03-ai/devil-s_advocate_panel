import { NextResponse } from "next/server";
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/pitch(.*)",
  "/session(.*)",
  "/history(.*)",
  "/api(.*)",
  "/sign-in(.*)",
  "/sign-up(.*)",
]);

const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
const isRealClerkKey = 
  Boolean(publishableKey) && 
  !publishableKey?.includes("placeholder") && 
  publishableKey !== "pk_test_Y2xlcmsuZGV2aWxzYWR2b2NhdGUuZGV2JA";

export default function middleware(req: any, evt: any) {
  if (!isRealClerkKey) {
    return NextResponse.next();
  }
  return clerkMiddleware((auth, request) => {
    if (!isPublicRoute(request)) {
      auth().protect();
    }
  })(req, evt);
}

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};

