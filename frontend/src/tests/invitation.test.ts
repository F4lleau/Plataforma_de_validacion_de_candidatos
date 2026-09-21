import { afterEach, describe, expect, it, vi } from "vitest";
import { captureLinkToken } from "../services/link-token";

afterEach(() => vi.unstubAllGlobals());
describe("enlaces de primer acceso", () => {
  it("cada flujo captura únicamente su token y limpia el fragmento del historial", () => {
    const replaceState = vi.fn();
    vi.stubGlobal("window", {
      location: { pathname: "/invitacion", hash: "#token=single-use-secret" },
      history: { replaceState },
    });
    expect(captureLinkToken("/restablecer-clave")).toBe("");
    expect(replaceState).not.toHaveBeenCalled();
    expect(captureLinkToken("/invitacion")).toBe("single-use-secret");
    expect(replaceState).toHaveBeenCalledWith(null, "", "/invitacion");
  });
  it("un enlace vacío no inventa credenciales ni escribe storage", () => {
    const replaceState = vi.fn();
    vi.stubGlobal("window", {
      location: { pathname: "/invitacion", hash: "" },
      history: { replaceState },
    });
    expect(captureLinkToken("/invitacion")).toBe("");
    expect(replaceState).not.toHaveBeenCalled();
  });
});
