// Route-specific capture prevents eagerly imported pages from taking another flow's token.
export function captureLinkToken(path: string): string {
  if (window.location.pathname !== path) return "";
  const token =
    new URLSearchParams(window.location.hash.slice(1)).get("token") ?? "";
  if (window.location.hash)
    window.history.replaceState(null, "", window.location.pathname);
  return token;
}
