const API_BASE_URL = "http://localhost:8000/api/v1";

export async function importPadron(file: File) {
  const token = localStorage.getItem("access_token");

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/padron/import`, {
    method: "POST",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("No se pudo importar el padrón.");
  }

  return response.json();
}