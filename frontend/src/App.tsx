import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import Layout from '@/components/Layout';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import GroupsPage from '@/pages/GroupsPage';
import ApplicationsPage from '@/pages/ApplicationsPage';
import ApplicationDetailPage from '@/pages/ApplicationDetailPage';
import FeaturesPage from '@/pages/FeaturesPage';
import FeatureDetailPage from '@/pages/FeatureDetailPage';
import TestCasesPage from '@/pages/TestCasesPage';
import TestCaseDetailPage from '@/pages/TestCaseDetailPage';
import TestRequestsPage from '@/pages/TestRequestsPage';
import TestRequestDetailPage from '@/pages/TestRequestDetailPage';
import UsersPage from '@/pages/UsersPage';
import PipelinesPage from '@/pages/PipelinesPage';
import ProfilePage from '@/pages/ProfilePage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== 'ADMIN') {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="groups" element={<GroupsPage />} />
        <Route path="applications" element={<ApplicationsPage />} />
        <Route path="applications/:id" element={<ApplicationDetailPage />} />
        <Route path="features" element={<FeaturesPage />} />
        <Route path="features/:id" element={<FeatureDetailPage />} />
        <Route path="test-cases" element={<TestCasesPage />} />
        <Route path="test-cases/:id" element={<TestCaseDetailPage />} />
        <Route path="requests" element={<TestRequestsPage />} />
        <Route path="requests/:id" element={<TestRequestDetailPage />} />
        <Route path="pipelines" element={<PipelinesPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route
          path="users"
          element={
            <AdminRoute>
              <UsersPage />
            </AdminRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;

