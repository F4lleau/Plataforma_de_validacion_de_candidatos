// Count Unicode code points, matching Python len(); never trim the password.
export function passwordLengthError(value: string): string | null {
  const length = Array.from(value).length;
  return length < 15 || length > 128
    ? "Usá entre 15 y 128 caracteres en la contraseña."
    : null;
}
