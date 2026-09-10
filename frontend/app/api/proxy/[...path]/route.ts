import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE = (process.env.BACKEND_INTERNAL_URL || 
                      process.env.NEXT_PUBLIC_API_URL || 
                      "https://devils-advocate-backend.onrender.com").replace(/\/+$/, "");

async function handleProxy(request: NextRequest, { params }: { params: { path?: string[] } }) {
  try {
    const pathSegments = params?.path || [];
    const path = pathSegments.join("/");
    const search = request.nextUrl.search || "";
    const targetUrl = `${BACKEND_BASE}/${path}${search}`;

    const headers: Record<string, string> = {};
    
    // Selectively forward only necessary headers
    const auth = request.headers.get("authorization");
    if (auth) headers["authorization"] = auth;
    
    const cookie = request.headers.get("cookie");
    if (cookie) headers["cookie"] = cookie;
    
    const contentType = request.headers.get("content-type");
    if (contentType) headers["content-type"] = contentType;

    headers["accept"] = "application/json, text/plain, */*";

    const fetchOptions: RequestInit = {
      method: request.method,
      headers,
      cache: "no-store",
    };

    if (request.method !== "GET" && request.method !== "HEAD") {
      const body = await request.text();
      if (body) {
        fetchOptions.body = body;
      }
    }

    const res = await fetch(targetUrl, fetchOptions);
    const responseBody = await res.text();

    return new NextResponse(responseBody, {
      status: res.status,
      headers: {
        "content-type": res.headers.get("content-type") || "application/json",
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Proxy failure: ${error.message}` },
      { status: 502 }
    );
  }
}

export const GET = handleProxy;
export const POST = handleProxy;
export const PUT = handleProxy;
export const DELETE = handleProxy;
export const OPTIONS = handleProxy;
