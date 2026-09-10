import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 
                    process.env.NEXT_PUBLIC_API_URL || 
                    "https://devils-advocate-backend.onrender.com";

function getTargetUrl(request: NextRequest, pathParams: string[]): string {
  const path = pathParams.join("/");
  const search = request.nextUrl.search;
  const baseUrl = BACKEND_URL.replace(/\/+$/, "");
  return `${baseUrl}/${path}${search}`;
}

async function handleProxy(request: NextRequest, { params }: { params: { path: string[] } }) {
  try {
    const targetUrl = getTargetUrl(request, params.path || []);
    
    // Forward headers (excluding host to prevent routing mismatch)
    const headers = new Headers();
    request.headers.forEach((value, key) => {
      if (key.toLowerCase() !== "host" && key.toLowerCase() !== "connection") {
        headers.set(key, value);
      }
    });

    const options: RequestInit = {
      method: request.method,
      headers,
      cache: "no-store",
    };

    if (request.method !== "GET" && request.method !== "HEAD") {
      const body = await request.text();
      if (body) {
        options.body = body;
      }
    }

    const backendResponse = await fetch(targetUrl, options);
    const data = await backendResponse.text();

    const responseHeaders = new Headers();
    backendResponse.headers.forEach((value, key) => {
      responseHeaders.set(key, value);
    });

    return new NextResponse(data, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });
  } catch (err: any) {
    return NextResponse.json(
      { detail: `Proxy error reaching backend: ${err.message}` },
      { status: 502 }
    );
  }
}

export const GET = handleProxy;
export const POST = handleProxy;
export const PUT = handleProxy;
export const DELETE = handleProxy;
export const OPTIONS = handleProxy;
