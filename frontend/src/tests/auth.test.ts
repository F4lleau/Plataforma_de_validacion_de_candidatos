import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";

const user = {
  id: 1,
  email: "admin@example.com",
  full_name: "Admin Test",
  role: "admin",
  is_active: true,
};
const loginResult = {
  access_token: "new-access",
  refresh_token: "unused-refresh",
  user,
  token_type: "bearer",
};
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>;

beforeEach(() => {
  vi.resetModules();
  const data = new Map<string, string>();
  vi.stubGlobal("localStorage", {
    getItem: (key: string) => data.get(key) ?? null,
    setItem: (key: string, value: string) => {
      data.set(key, value);
    },
    removeItem: (key: string) => {
      data.delete(key);
    },
  });
  fetchMock = vi.fn<typeof fetch>();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

async function authenticatedStore() {
  const { useAuthStore } = await import("../stores/auth.store");
  fetchMock.mockResolvedValueOnce(Response.json(loginResult));
  await useAuthStore.getState().login("admin@example.com", "test-password");
  return useAuthStore;
}

function pendingResponse() {
  let resolve!: (response: Response) => void;
  const promise = new Promise<Response>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

describe("sesión y cliente API", () => {
  it("verifica /me antes de considerar válido el token persistido", async () => {
    localStorage.setItem("access_token", "persisted-token");
    const { useAuthStore } = await import("../stores/auth.store");
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    fetchMock.mockResolvedValueOnce(Response.json(user));
    await useAuthStore.getState().restoreSession();
    expect(useAuthStore.getState()).toMatchObject({
      isAuthenticated: true,
      isLoading: false,
      accessToken: "persisted-token",
      user,
    });
    expect(
      new Headers(fetchMock.mock.calls[0][1]?.headers).get("Authorization"),
    ).toBe("Bearer persisted-token");
  });

  it("inicia sin sesión si no hay token, sin llamar a /me", async () => {
    const { useAuthStore } = await import("../stores/auth.store");
    await useAuthStore.getState().restoreSession();
    expect(useAuthStore.getState()).toMatchObject({
      isAuthenticated: false,
      isLoading: false,
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("login guarda solo el access token y logout elimina toda la sesión", async () => {
    const store = await authenticatedStore();
    expect(localStorage.getItem("access_token")).toBe("new-access");
    expect(localStorage.getItem("refresh_token")).toBeNull();
    expect(localStorage.getItem("password")).toBeNull();
    store.getState().logout();
    expect(store.getState()).toMatchObject({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it.each(["json", "upload"])(
    "un 401 de %s invalida también Zustand",
    async (kind) => {
      const store = await authenticatedStore();
      const api = await import("../services/api");
      fetchMock.mockResolvedValueOnce(
        Response.json({ detail: "Token inválido." }, { status: 401 }),
      );
      const call =
        kind === "upload"
          ? api.apiUpload("/padron/import", new FormData())
          : api.apiFetch("/candidates");
      await expect(call).rejects.toMatchObject({ status: 401 });
      expect(store.getState()).toMatchObject({
        user: null,
        isAuthenticated: false,
        accessToken: null,
      });
      expect(localStorage.getItem("access_token")).toBeNull();
    },
  );

  it("no confunde un 403 con una sesión expirada", async () => {
    const store = await authenticatedStore();
    const { apiFetch } = await import("../services/api");
    fetchMock.mockResolvedValueOnce(
      Response.json({ detail: "Acceso restringido" }, { status: 403 }),
    );
    await expect(apiFetch("/padron/import")).rejects.toMatchObject({
      status: 403,
    });
    expect(store.getState().isAuthenticated).toBe(true);
  });

  it("una restauración pendiente no recupera la sesión después de logout", async () => {
    localStorage.setItem("access_token", "old-token");
    const { useAuthStore } = await import("../stores/auth.store");
    const pending = pendingResponse();
    fetchMock.mockReturnValueOnce(pending.promise);
    const restoring = useAuthStore.getState().restoreSession();
    useAuthStore.getState().logout();
    pending.resolve(Response.json(user));
    await restoring;
    expect(useAuthStore.getState()).toMatchObject({
      isAuthenticated: false,
      user: null,
    });
  });

  it("un 401 antiguo no elimina la nueva sesión", async () => {
    const store = await authenticatedStore();
    const { apiFetch } = await import("../services/api");
    const pending = pendingResponse();
    fetchMock.mockReturnValueOnce(pending.promise);
    const stale = apiFetch("/candidates");
    fetchMock.mockResolvedValueOnce(
      Response.json({ ...loginResult, access_token: "replacement-token" }),
    );
    await store.getState().login("admin@example.com", "test-password");
    pending.resolve(Response.json({ detail: "expired" }, { status: 401 }));
    await expect(stale).rejects.toMatchObject({ status: 401 });
    expect(store.getState().isAuthenticated).toBe(true);
    expect(localStorage.getItem("access_token")).toBe("replacement-token");
  });

  it("distingue credenciales inválidas, error servidor y desconexión sin exponer detalles técnicos", async () => {
    const { loginRequest } = await import("../services/auth.service");
    fetchMock.mockResolvedValueOnce(
      Response.json({ detail: "Credenciales inválidas." }, { status: 401 }),
    );
    await expect(
      loginRequest("admin@example.com", "wrong"),
    ).rejects.toMatchObject({ status: 401 });
    fetchMock.mockResolvedValueOnce(
      Response.json({ detail: "secret database traceback" }, { status: 500 }),
    );
    await expect(
      loginRequest("admin@example.com", "test"),
    ).rejects.toMatchObject({
      status: 500,
      message:
        "El servidor no pudo completar la operación. Intentá nuevamente.",
    });
    fetchMock.mockRejectedValueOnce(new TypeError("fetch failed"));
    await expect(
      loginRequest("admin@example.com", "test"),
    ).rejects.toMatchObject({
      status: 0,
      message: "No pudimos conectar con el servidor. Intentá nuevamente.",
    });
  });

  it("un /me rechazado limpia la sesión persistida", async () => {
    localStorage.setItem("access_token", "bad-token");
    const { useAuthStore } = await import("../stores/auth.store");
    fetchMock.mockResolvedValueOnce(
      Response.json({ detail: "Token inválido" }, { status: 401 }),
    );
    await useAuthStore.getState().restoreSession();
    expect(useAuthStore.getState()).toMatchObject({
      isAuthenticated: false,
      accessToken: null,
      isLoading: false,
    });
    expect(localStorage.getItem("access_token")).toBeNull();
  });
});

it("muestra errores por campo sin repetir los valores enviados", async () => {
  const { apiFetch } = await import("../services/api");
  fetchMock.mockResolvedValueOnce(
    Response.json(
      {
        detail: [
          {
            loc: ["body", "birth_date"],
            msg: "Fecha inválida",
            input: "private-input",
          },
        ],
      },
      { status: 422 },
    ),
  );
  await expect(
    apiFetch("/lists/1/candidates", { method: "POST", body: "{}" }),
  ).rejects.toMatchObject({
    status: 422,
    message: "birth_date: Fecha inválida",
  });
});

it("descarga con Bearer y conserva MIME/nombre", async () => {
  await authenticatedStore();
  const { apiDownload } = await import("../services/api");
  fetchMock.mockResolvedValueOnce(
    new Response("%PDF-test", {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": 'attachment; filename="reporte-electoral.pdf"',
      },
    }),
  );
  const result = await apiDownload("/admin/exports/reports?format=pdf");
  expect(result.filename).toBe("reporte-electoral.pdf");
  expect(await result.blob.text()).toBe("%PDF-test");
  expect(
    new Headers(fetchMock.mock.calls[1][1]?.headers).get("Authorization"),
  ).toBe("Bearer new-access");
});
it("401 en descarga cierra la sesión sin devolver archivo", async () => {
  const store = await authenticatedStore();
  const { apiDownload } = await import("../services/api");
  fetchMock.mockResolvedValueOnce(
    Response.json({ detail: "Sesión expirada" }, { status: 401 }),
  );
  await expect(apiDownload("/admin/exports/lists")).rejects.toMatchObject({
    status: 401,
  });
  expect(store.getState().isAuthenticated).toBe(false);
});
it("descarga no guarda HTML ni errores JSON", async () => {
  const { apiDownload } = await import("../services/api");
  fetchMock.mockResolvedValueOnce(
    new Response("<html>Error</html>", {
      headers: { "Content-Type": "text/html" },
    }),
  );
  await expect(apiDownload("/admin/exports/lists")).rejects.toMatchObject({
    status: 502,
  });
  fetchMock.mockResolvedValueOnce(
    Response.json({ detail: "Acote los filtros" }, { status: 413 }),
  );
  await expect(apiDownload("/admin/exports/lists")).rejects.toMatchObject({
    status: 413,
    message: "Acote los filtros",
  });
});
