import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
const user = {
  id: 1,
  email: "admin@example.com",
  full_name: "Admin Test",
  role: "admin",
  is_active: true,
};
const result = { access_token: "new-access", user, token_type: "bearer" };
let network: ReturnType<typeof vi.fn<typeof fetch>>;
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>;

beforeEach(() => {
  vi.resetModules();
  const data = new Map<string, string>();
  vi.stubGlobal("localStorage", {
    getItem: (k: string) => data.get(k) ?? null,
    setItem: (k: string, v: string) => data.set(k, v),
    removeItem: (k: string) => data.delete(k),
  });
  network = vi.fn<typeof fetch>();
  fetchMock = vi.fn<typeof fetch>((url, options) =>
    String(url).endsWith("/auth/csrf")
      ? Promise.resolve(Response.json({ csrf_token: "csrf-test" }))
      : network(url, options),
  );
  vi.stubGlobal("fetch", fetchMock);
});
afterEach(() => vi.unstubAllGlobals());

async function authenticated() {
  const { useAuthStore } = await import("../stores/auth.store");
  network.mockResolvedValueOnce(Response.json(result));
  await useAuthStore.getState().login(user.email, "private password");
  return useAuthStore;
}
function pendingResponse() {
  let resolve!: (r: Response) => void;
  const promise = new Promise<Response>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

describe("sesiones revocables", () => {
  it("elimina tokens legacy y restaura desde cookie HttpOnly", async () => {
    localStorage.setItem("access_token", "legacy");
    const { useAuthStore } = await import("../stores/auth.store");
    expect(localStorage.getItem("access_token")).toBeNull();
    network.mockResolvedValueOnce(Response.json(result));
    await useAuthStore.getState().restoreSession();
    expect(useAuthStore.getState()).toMatchObject({
      isAuthenticated: true,
      user,
    });
    expect(String(network.mock.calls[0][0])).toContain("/auth/refresh");
    expect(network.mock.calls[0][1]?.credentials).toBe("include");
    expect(
      new Headers(network.mock.calls[0][1]?.headers).get("X-CSRF-Token"),
    ).toBe("csrf-test");
  });
  it("login deja credenciales solo en memoria y logout llama al servidor", async () => {
    const store = await authenticated();
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
    network.mockResolvedValueOnce(Response.json({ message: "ok" }));
    await store.getState().logout();
    expect(store.getState().isAuthenticated).toBe(false);
    expect(String(network.mock.calls[1][0])).toContain("/auth/logout");
  });
  it("restauración sin cookie termina sin sesión", async () => {
    const { useAuthStore } = await import("../stores/auth.store");
    network.mockResolvedValueOnce(
      Response.json({ detail: "invalid" }, { status: 401 }),
    );
    await useAuthStore.getState().restoreSession();
    expect(useAuthStore.getState()).toMatchObject({
      isAuthenticated: false,
      isLoading: false,
    });
  });
  it.each(["json", "upload", "download"])(
    "renueva un 401 de %s y reintenta una sola vez",
    async (kind) => {
      await authenticated();
      const api = await import("../services/api");
      network.mockResolvedValueOnce(Response.json({}, { status: 401 }));
      network.mockResolvedValueOnce(
        Response.json({ ...result, access_token: "rotated" }),
      );
      network.mockResolvedValueOnce(
        kind === "download"
          ? new Response("%PDF", {
              headers: { "Content-Type": "application/pdf" },
            })
          : Response.json({ ok: true }),
      );
      if (kind === "upload")
        await api.apiUpload("/padron/import", new FormData());
      else if (kind === "download")
        await api.apiDownload("/admin/exports/lists");
      else await api.apiFetch("/lists/", { method: "POST", body: "{}" });
      expect(
        new Headers(network.mock.calls[3][1]?.headers).get("Authorization"),
      ).toBe("Bearer rotated");
      expect(network).toHaveBeenCalledTimes(4);
    },
  );
  it("una renovación inválida cierra sesión sin repetir la escritura", async () => {
    const store = await authenticated();
    const { apiFetch } = await import("../services/api");
    network.mockResolvedValueOnce(Response.json({}, { status: 401 }));
    network.mockResolvedValueOnce(Response.json({}, { status: 401 }));
    await expect(
      apiFetch("/lists/", { method: "POST", body: "{}" }),
    ).rejects.toMatchObject({ status: 401 });
    expect(store.getState().isAuthenticated).toBe(false);
    expect(
      network.mock.calls.filter(([url]) => String(url).endsWith("/lists/")),
    ).toHaveLength(1);
  });
  it("no reintenta 403, errores de red ni escrituras exitosas", async () => {
    const store = await authenticated();
    const { apiFetch } = await import("../services/api");
    network.mockResolvedValueOnce(
      Response.json({ detail: "Sin permiso" }, { status: 403 }),
    );
    await expect(apiFetch("/admin/test")).rejects.toMatchObject({
      status: 403,
    });
    expect(store.getState().isAuthenticated).toBe(true);
    network.mockRejectedValueOnce(new TypeError("network"));
    await expect(apiFetch("/lists/", { method: "POST" })).rejects.toMatchObject(
      { status: 0 },
    );
    network.mockResolvedValueOnce(Response.json({ ok: true }));
    await apiFetch("/lists/", { method: "POST" });
    expect(
      network.mock.calls.filter(([url]) =>
        String(url).endsWith("/auth/refresh"),
      ),
    ).toHaveLength(0);
  });
  it("coordina solicitudes paralelas con una sola renovación", async () => {
    await authenticated();
    const { apiFetch } = await import("../services/api");
    const pending = pendingResponse();
    network.mockResolvedValueOnce(Response.json({}, { status: 401 }));
    network.mockResolvedValueOnce(Response.json({}, { status: 401 }));
    network.mockReturnValueOnce(pending.promise);
    network.mockImplementation(async () => Response.json({ ok: true }));
    const a = apiFetch("/a");
    const b = apiFetch("/b");
    await vi.waitFor(() =>
      expect(
        network.mock.calls.some(([url]) =>
          String(url).endsWith("/auth/refresh"),
        ),
      ).toBe(true),
    );
    pending.resolve(Response.json({ ...result, access_token: "rotated" }));
    await Promise.all([a, b]);
    expect(
      network.mock.calls.filter(([url]) =>
        String(url).endsWith("/auth/refresh"),
      ),
    ).toHaveLength(1);
  });
  it("una respuesta vieja no borra ni reemplaza una sesión nueva", async () => {
    const store = await authenticated();
    const { apiFetch } = await import("../services/api");
    const pending = pendingResponse();
    network.mockReturnValueOnce(pending.promise);
    const stale = apiFetch("/lists/");
    network.mockResolvedValueOnce(
      Response.json({ ...result, access_token: "replacement" }),
    );
    await store.getState().login(user.email, "private password");
    pending.resolve(Response.json({}, { status: 401 }));
    await expect(stale).rejects.toMatchObject({ status: 401 });
    expect(store.getState().accessToken).toBe("replacement");
  });
  it("logout durante refresh evita restaurar la sesión", async () => {
    const store = await authenticated();
    const { refreshSession } = await import("../services/api");
    const pending = pendingResponse();
    network.mockReturnValueOnce(pending.promise);
    const restoring = refreshSession();
    await vi.waitFor(() => expect(network).toHaveBeenCalledTimes(2));
    network.mockResolvedValueOnce(Response.json({ message: "ok" }));
    const closing = store.getState().logout();
    pending.resolve(Response.json(result));
    await expect(restoring).rejects.toMatchObject({ status: 401 });
    await closing;
    expect(store.getState().isAuthenticated).toBe(false);
  });
  it("no persiste cookies ni imprime entradas en errores de validación", async () => {
    await authenticated();
    const { apiFetch } = await import("../services/api");
    network.mockResolvedValueOnce(
      Response.json(
        {
          detail: [
            { loc: ["body", "password"], msg: "Inválida", input: "secret" },
          ],
        },
        { status: 422 },
      ),
    );
    await expect(apiFetch("/test", { method: "POST" })).rejects.toMatchObject({
      message: "password: Inválida",
    });
  });
  it("la descarga conserva nombre y MIME y rechaza HTML", async () => {
    await authenticated();
    const { apiDownload } = await import("../services/api");
    network.mockResolvedValueOnce(
      new Response("%PDF", {
        headers: {
          "Content-Type": "application/pdf",
          "Content-Disposition": 'attachment; filename="reporte.pdf"',
        },
      }),
    );
    const file = await apiDownload("/admin/exports/reports");
    expect(file.filename).toBe("reporte.pdf");
    network.mockResolvedValueOnce(
      new Response("html", { headers: { "Content-Type": "text/html" } }),
    );
    await expect(apiDownload("/test")).rejects.toMatchObject({ status: 502 });
  });
});

it("cuenta Unicode igual que backend y conserva espacios", async () => {
  const { passwordLengthError } = await import("../services/password-policy");
  expect(passwordLengthError("🦋".repeat(14))).not.toBeNull();
  expect(passwordLengthError("🦋".repeat(100))).toBeNull();
  expect(passwordLengthError("á".repeat(129))).not.toBeNull();
  expect(passwordLengthError("  frase larga  ")).toBeNull();
});

it("una restauración obsoleta no cierra un login posterior", async () => {
  // Exercise the fallback without Web Locks, where responses can cross.
  vi.stubGlobal("navigator", {});
  const { useAuthStore } = await import("../stores/auth.store");
  const pending = pendingResponse();
  network.mockReturnValueOnce(pending.promise);
  const restoring = useAuthStore.getState().restoreSession();
  await vi.waitFor(() => expect(network).toHaveBeenCalledTimes(1));
  network.mockResolvedValueOnce(
    Response.json({ ...result, access_token: "later-login" }),
  );
  await useAuthStore.getState().login(user.email, "private password");
  pending.resolve(Response.json({}, { status: 401 }));
  await restoring;
  expect(useAuthStore.getState()).toMatchObject({
    isAuthenticated: true,
    accessToken: "later-login",
  });
});
