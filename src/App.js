import { Navigate, Route, Routes } from "react-router-dom";

import GroupDetailPage from "./GroupDetailPage";
import GroupsPage from "./GroupsPage";
import LoginPage from "./LoginPage";
import ProfilePage from "./ProfilePage";
import ActivityDetailPage from "./ActivityDetailPage";
import StatsPage from "./StatsPage";

function RequireAuth({ children }) {
  const token = localStorage.getItem("uisgo_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/groups"
        element={
          <RequireAuth>
            <GroupsPage />
          </RequireAuth>
        }
      />
      <Route
        path="/groups/:groupId"
        element={
          <RequireAuth>
            <GroupDetailPage />
          </RequireAuth>
        }
      />
      <Route
        path="/profile"
        element={
          <RequireAuth>
            <ProfilePage />
          </RequireAuth>
        }
      />
      <Route
        path="/activities/:activityId"
        element={
          <RequireAuth>
            <ActivityDetailPage />
          </RequireAuth>
        }
      />
      <Route
        path="/stats"
        element={
          <RequireAuth>
            <StatsPage />
          </RequireAuth>
        }
      />
      <Route path="/" element={<Navigate to="/groups" replace />} />
      <Route path="*" element={<Navigate to="/groups" replace />} />
    </Routes>
  );
}

export default App;
