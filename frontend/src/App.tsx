import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";
import Candidatos from "./pages/Candidatos";
import CandidatosRevision from "./pages/CandidatosRevision";
import Dashboard from "./pages/Dashboard";
import Forbidden from "./pages/Forbidden";
import Listas from "./pages/Listas";
import Login from "./pages/Login";
import Padron from "./pages/Padron";

import Configuracion from "./pages/Configuracion";
import Usuarios from "./pages/Usuarios";
import ListaDetalle from "./pages/ListaDetalle";

import Validaciones from "./pages/Validaciones";
import Reportes from "./pages/Reportes";
import Auditoria from "./pages/Auditoria";
import Ayuda from "./pages/Ayuda";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/403" element={<Forbidden />} />
          <Route path="/ayuda" element={<Ayuda />} />
          <Route element={<ProtectedRoute roles={["admin"]} />}>
            <Route path="/validaciones" element={<Validaciones />} />
            <Route path="/reportes" element={<Reportes />} />
            <Route path="/auditoria" element={<Auditoria />} />
          </Route>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/listas/:id" element={<ListaDetalle />} />
          <Route element={<ProtectedRoute roles={["admin"]} />}>
            <Route path="/configuracion" element={<Configuracion />} />
            <Route path="/usuarios" element={<Usuarios />} />
          </Route>
          <Route path="/listas" element={<Listas />} />
          <Route path="/candidatos" element={<Candidatos />} />
          <Route
            path="/candidatos/revision"
            element={<ProtectedRoute roles={["admin"]} />}
          >
            <Route index element={<CandidatosRevision />} />
          </Route>
          <Route path="/padron" element={<ProtectedRoute roles={["admin"]} />}>
            <Route index element={<Padron />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
