// User types
export type UserRole = 'ADMIN' | 'USER';
export type UserStatus = 'ACTIVE' | 'INACTIVE';

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  status: UserStatus;
  createdAt: string;
  updatedAt?: string;
  subscriptions?: GroupSubscription[];
}

export interface AuthUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
}

// Group types
export interface Group {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt?: string;
  applications?: Application[];
  subscriptions?: GroupSubscription[];
  _count?: {
    applications: number;
    subscriptions: number;
  };
}

export interface GroupSubscription {
  id: string;
  userId: string;
  groupId: string;
  createdAt: string;
  user?: User;
  group?: Group;
}

// Application types
export type ApplicationStatus = 'ACTIVE' | 'DISCONTINUED';

export interface Application {
  id: string;
  name: string;
  description?: string;
  status: ApplicationStatus;
  groupId: string;
  gitlabProjectId?: string;
  gitlabProjectUrl?: string;
  availabilityUrl?: string;
  createdAt: string;
  updatedAt?: string;
  group?: Group;
  features?: Feature[];
  _count?: {
    features: number;
    testRequests: number;
  };
}

// Feature types
export type FeatureStatus = 'PLANNED' | 'IN_DEVELOPMENT' | 'PRODUCTIVE';

export interface Feature {
  id: string;
  name: string;
  description?: string;
  featureFilePath?: string;
  status: FeatureStatus;
  applicationId: string;
  createdAt: string;
  updatedAt?: string;
  application?: Application;
  testCases?: TestCase[];
  _count?: {
    testCases: number;
  };
}

// Test Case types
export type TestCaseType = 'MANUAL' | 'AUTOMATED';
export type TestCasePriority = 'HIGH' | 'MEDIUM' | 'LOW';
export type TestCaseStatus = 'PLANNED' | 'IN_DEVELOPMENT' | 'PRODUCTIVE' | 'OBSOLETE';

export interface TestCase {
  id: string;
  name: string;
  description?: string;
  type: TestCaseType;
  priority: TestCasePriority;
  status: TestCaseStatus;
  featureId: string;
  azureUserStoryId?: string;
  azureUserStoryUrl?: string;
  azureTestCaseId?: string;
  azureTestCaseUrl?: string;
  tags: string[];
  scenarioName?: string;
  createdAt: string;
  updatedAt?: string;
  feature?: Feature;
  steps?: GherkinStep[];
  pipelineResults?: TestCasePipelineResult[];
  _count?: {
    steps: number;
    pipelineResults: number;
  };
}

// Gherkin types
export type GherkinStepType = 'GIVEN' | 'WHEN' | 'THEN' | 'AND' | 'BUT';

export interface GherkinStep {
  id: string;
  type: GherkinStepType;
  text: string;
  order: number;
  testCaseId: string;
  subSteps?: GherkinSubStep[];
}

export interface GherkinSubStep {
  id: string;
  text: string;
  order: number;
  stepId: string;
}

// Pipeline types
export type PipelineStatus = 'PENDING' | 'RUNNING' | 'PASSED' | 'FAILED' | 'CANCELED' | 'SKIPPED';
export type TestResultStatus = 'PASSED' | 'FAILED' | 'SKIPPED' | 'NOT_EXECUTED';

export interface GitlabPipeline {
  id: string;
  gitlabProjectId: string;
  gitlabPipelineId: string;
  branch: string;
  status: PipelineStatus;
  webUrl?: string;
  executedAt: string;
  createdAt: string;
  _count?: {
    testCaseResults: number;
  };
}

export interface TestCasePipelineResult {
  id: string;
  testCaseId: string;
  pipelineId: string;
  status: TestResultStatus;
  details?: string;
  logUrl?: string;
  duration?: number;
  createdAt: string;
  testCase?: TestCase;
  pipeline?: GitlabPipeline;
}

// Test Request types
export type TestRequestStatus = 'NEW' | 'IN_ANALYSIS' | 'APPROVED' | 'REJECTED' | 'IMPLEMENTED';
export type TestRequestType = 'FRONT' | 'API';

export interface FrontTestSubAction {
  description: string;
  screenshotUrl?: string;
}

export interface FrontTestTask {
  title: string;
  expectedResult: string;
  expectedScreenshotUrl?: string;
  subActions: FrontTestSubAction[];
}

export interface FrontTestPlan {
  tasks: FrontTestTask[];
}

export interface ApiTestEndpoint {
  method: string;
  url: string;
  headers?: Record<string, string>;
  payload?: Record<string, any>;
  response?: {
    json_extractions?: Array<{
      path: string;
      name: string;
    }>;
  };
}

export interface ApiTestScenario {
  name: string;
  description?: string;
  endpoints: ApiTestEndpoint[];
}

export interface ApiTestPlan {
  baseUrl: string;
  scenarios: ApiTestScenario[];
}

export interface TestRequest {
  id: string;
  title: string;
  description: string;
  status: TestRequestStatus;
  applicationId: string;
  requesterId: string;
  assigneeId?: string;
  azureWorkItemId?: string;
  azureWorkItemUrl?: string;
  additionalNotes?: string;
  generatedTestCaseId?: string;
  type?: TestRequestType;
  environment?: string;
  hasAuth?: boolean;
  authType?: string;
  authUsers?: string[];
  frontPlan?: FrontTestPlan;
  apiPlan?: ApiTestPlan;
  createdAt: string;
  updatedAt?: string;
  application?: Application;
  requester?: User;
  assignee?: User;
  generatedTestCase?: TestCase;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Dashboard types
export interface DashboardStats {
  overview: {
    totalGroups: number;
    totalApplications: number;
    totalFeatures: number;
    totalTestCases: number;
    totalRequests: number;
    pendingRequests: number;
    recentPipelines: number;
  };
  testCasesByStatus: { status: string; count: number }[];
  requestsByStatus: { status: string; count: number }[];
}

export interface RecentActivity {
  testCases: {
    id: string;
    name: string;
    status: string;
    updatedAt: string;
    feature: { name: string; application: { name: string } };
  }[];
  requests: {
    id: string;
    title: string;
    status: string;
    updatedAt: string;
    application: { name: string };
    requester: { firstName: string; lastName: string };
  }[];
  pipelines: GitlabPipeline[];
}

