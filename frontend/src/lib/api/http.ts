export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export type QueryValue = string | number | boolean | null | undefined;

const DEFAULT_PROXY_BASE = "/api/hive";

function getProxyBase(): string {
  const configured = process.env.NEXT_PUBLIC_HIVE_PROXY_PREFIX ?? DEFAULT_PROXY_BASE;
  const withLeadingSlash = configured.startsWith("/") ? configured : `/${configured}`;
  return withLeadingSlash.replace(/\/+$/, "");
}

function normalizePath(path: string): string {
  if (!path) {
    return "";
  }
  return path.startsWith("/") ? path : `/${path}`;
}

export function withQuery(path: string, query?: Record<string, QueryValue>): string {
  if (!query) {
    return path;
  }

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === null || value === undefined || value === "") {
      continue;
    }
    params.set(key, String(value));
  }

  const queryString = params.toString();
  if (!queryString) {
    return path;
  }

  return `${path}${path.includes("?") ? "&" : "?"}${queryString}`;
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    cache: "no-store",
  });

  if (!response.ok) {
    const details = await parseResponseBody(response);
    throw new ApiError(`Request failed with status ${response.status}`, response.status, details);
  }

  return (await parseResponseBody(response)) as T;
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${getProxyBase()}${normalizePath(path)}`;
  return requestJson<T>(url, {
    method: "GET",
    ...init,
  });
}

export async function apiPost<TBody, TResponse>(path: string, body: TBody, init?: RequestInit): Promise<TResponse> {
  const url = `${getProxyBase()}${normalizePath(path)}`;
  return requestJson<TResponse>(url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {}),
    },
    body: JSON.stringify(body),
    ...init,
  });
}
