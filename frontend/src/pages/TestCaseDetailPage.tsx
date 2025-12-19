"use client"

import { motion } from 'framer-motion';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  ArrowLeftIcon,
  BeakerIcon,
  LinkIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { testCasesApi } from '@/services/api';
import { StatusBadge, PriorityBadge, TypeBadge } from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { GherkinStep, GherkinStepType } from '@/types';

const stepKeywords: Record<GherkinStepType, string> = {
  GIVEN: 'Given',
  WHEN: 'When',
  THEN: 'Then',
  AND: 'And',
  BUT: 'But',
};

export default function TestCaseDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: testCase, isLoading } = useQuery({
    queryKey: ['test-case', id],
    queryFn: async () => {
      const response = await testCasesApi.getById(id!);
      return response.data.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-surface-700 rounded w-1/4" />
        <div className="card">
          <div className="h-6 bg-surface-700 rounded w-1/2 mb-4" />
          <div className="h-4 bg-surface-700 rounded w-3/4" />
        </div>
      </div>
    );
  }

  if (!testCase) {
    return (
      <div className="card text-center py-12">
        <div className="text-4xl mb-3">🔬</div>
        <p className="text-surface-400">Caso de prueba no encontrado</p>
        <Link to="/test-cases">
          <Button variant="secondary" className="mt-4">
            Volver a casos de prueba
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Back button */}
      <Link to="/test-cases" className="inline-flex items-center gap-2 text-surface-400 hover:text-surface-100 transition-colors">
        <ArrowLeftIcon className="w-4 h-4" />
        Volver a casos de prueba
      </Link>

      {/* Header */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-orange-500/20 to-amber-500/20 flex items-center justify-center">
            <BeakerIcon className="w-8 h-8 text-orange-400" />
          </div>
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-display font-bold text-surface-100">
                {testCase.name}
              </h1>
              <TypeBadge type={testCase.type} />
              <PriorityBadge priority={testCase.priority} />
              <StatusBadge status={testCase.status} />
            </div>
            <p className="text-surface-400 mt-2">{testCase.description || 'Sin descripción'}</p>
            
            <div className="flex flex-wrap items-center gap-4 mt-4">
              <Link to={`/features/${testCase.featureId}`}>
                <span className="px-3 py-1 bg-surface-800 rounded-lg text-sm text-surface-300 hover:bg-surface-700 transition-colors">
                  {testCase.feature?.name}
                </span>
              </Link>
              <span className="text-sm text-surface-500">
                {testCase.feature?.application?.name}
              </span>
            </div>

            {/* Azure links */}
            <div className="flex flex-wrap gap-4 mt-4">
              {testCase.azureUserStoryId && (
                <a
                  href={testCase.azureUserStoryUrl || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300"
                >
                  <LinkIcon className="w-4 h-4" />
                  User Story: {testCase.azureUserStoryId}
                </a>
              )}
              {testCase.azureTestCaseId && (
                <a
                  href={testCase.azureTestCaseUrl || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300"
                >
                  <LinkIcon className="w-4 h-4" />
                  Test Case: {testCase.azureTestCaseId}
                </a>
              )}
            </div>

            {/* Tags */}
            {testCase.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {testCase.tags.map((tag: string) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-accent-500/20 text-accent-300 rounded text-xs"
                  >
                    @{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Gherkin Steps */}
      <div className="card">
        <h2 className="text-lg font-display font-semibold text-surface-100 mb-6">
          Steps Gherkin
        </h2>
        
        {testCase.steps?.length === 0 ? (
          <div className="text-center py-8 text-surface-500">
            <p>No hay steps definidos</p>
          </div>
        ) : (
          <div className="space-y-4 font-mono text-sm">
            {testCase.steps?.map((step: GherkinStep) => (
              <div key={step.id} className="gherkin-step">
                <div className="flex">
                  <span className="gherkin-keyword w-16 flex-shrink-0">
                    {stepKeywords[step.type]}
                  </span>
                  <span className="gherkin-text">{step.text}</span>
                </div>
                {step.subSteps && step.subSteps.length > 0 && (
                  <div className="ml-16 mt-2 space-y-1 text-surface-500 text-xs">
                    {step.subSteps.map((sub) => (
                      <div key={sub.id} className="flex items-start gap-2">
                        <span className="text-surface-600">•</span>
                        <span>{sub.text}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pipeline Results */}
      <div className="card">
        <h2 className="text-lg font-display font-semibold text-surface-100 mb-6">
          Resultados de Ejecución
        </h2>
        
        {testCase.pipelineResults?.length === 0 ? (
          <div className="text-center py-8 text-surface-500">
            <ClockIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No hay ejecuciones registradas</p>
          </div>
        ) : (
          <div className="space-y-3">
            {testCase.pipelineResults?.map((result: any) => (
              <div
                key={result.id}
                className="flex items-center gap-4 p-4 rounded-lg bg-surface-800/50 border border-surface-700/50"
              >
                <div className="flex items-center gap-2">
                  {result.status === 'PASSED' ? (
                    <CheckCircleIcon className="w-6 h-6 text-emerald-400" />
                  ) : result.status === 'FAILED' ? (
                    <XCircleIcon className="w-6 h-6 text-red-400" />
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-surface-600" />
                  )}
                  <StatusBadge status={result.status} />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-surface-300">
                    Pipeline #{result.pipeline?.gitlabPipelineId}
                  </p>
                  <p className="text-xs text-surface-500">
                    Branch: {result.pipeline?.branch}
                  </p>
                </div>
                {result.duration && (
                  <span className="text-sm text-surface-500">
                    {result.duration}s
                  </span>
                )}
                <span className="text-xs text-surface-500">
                  {formatDistanceToNow(new Date(result.createdAt), {
                    addSuffix: true,
                    locale: es,
                  })}
                </span>
                {result.logUrl && (
                  <a
                    href={result.logUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-400 hover:text-primary-300"
                  >
                    Ver logs
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

