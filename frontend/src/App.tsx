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

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/403" element={<Forbidden />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
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
