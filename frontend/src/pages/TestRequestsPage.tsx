"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { Link } from "react-router-dom"
import { formatDistanceToNow } from "date-fns"
import { es } from "date-fns/locale"
import { 
  Plus, 
  Search, 
  ChevronRight, 
  X, 
  Trash2, 
  Pencil, 
  ChevronDown,
  Layers,
  Zap
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"

// Mock API functions - replace with your actual API
const testRequestsApi = {
  getAll: async (params: Record<string, string>) => ({ data: { data: [] } }),
  create: async (data: any) => ({ data: {} }),
}
const applicationsApi = {
  getAll: async (params: Record<string, string>) => ({ data: { data: [] } }),
}

interface RequestForm {
  title: string
  applicationId: string
  type: "FRONT" | "API"
  environment: string
  azureWorkItemId?: string
  azureWorkItemUrl?: string
  additionalNotes?: string
  hasAuth?: boolean
  authType?: string
  authUsers?: string
}

interface FrontTask {
  title: string
  description: string
  expectedResult: string
  subTasks: { description: string }[]
}

interface ApiScenario {
  name: string
  endpoints: { method: string; url: string }[]
}

interface TestRequest {
  id: string
  title: string
  description?: string
  status: string
  application?: { name: string }
  requester?: { firstName: string; lastName: string }
  createdAt: string
}

interface Application {
  id: string
  name: string
}

const statusColors: Record<string, string> = {
  NEW: "bg-primary/20 text-primary",
  IN_ANALYSIS: "bg-amber-500/20 text-amber-400",
  APPROVED: "bg-emerald-500/20 text-emerald-400",
  REJECTED: "bg-destructive/20 text-destructive",
  IMPLEMENTED: "bg-blue-500/20 text-blue-400",
}

const statusLabels: Record<string, string> = {
  NEW: "Nueva",
  IN_ANALYSIS: "En Análisis",
  APPROVED: "Aprobada",
  REJECTED: "Rechazada",
  IMPLEMENTED: "Implementada",
}

export default function TestRequestsPage() {
  const [search, setSearch] = useState("")
  const [appFilter, setAppFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedType, setSelectedType] = useState<"FRONT" | "API">("FRONT")
  const [frontTasks, setFrontTasks] = useState<FrontTask[]>([])
  const [apiScenarios, setApiScenarios] = useState<ApiScenario[]>([])
  const [selectedTaskIndex, setSelectedTaskIndex] = useState<number | null>(null)
  const [selectedScenarioIndex, setSelectedScenarioIndex] = useState<number | null>(null)
  const [newItemName, setNewItemName] = useState("")
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [showAdvanced, setShowAdvanced] = useState(false)
  
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { register, handleSubmit, reset, formState: { errors } } = useForm<RequestForm>({
    defaultValues: { type: "FRONT", environment: "" },
  })

  const { data: requestsData, isLoading } = useQuery({
    queryKey: ["test-requests", search, appFilter, statusFilter],
    queryFn: async () => {
      const params: Record<string, string> = { limit: "100" }
      if (search) params.search = search
      if (appFilter && appFilter !== "all") params.applicationId = appFilter
      if (statusFilter && statusFilter !== "all") params.status = statusFilter
      return (await testRequestsApi.getAll(params)).data
    },
  })

  const { data: appsData } = useQuery({
    queryKey: ["applications-list"],
    queryFn: async () => (await applicationsApi.getAll({ limit: "100" })).data.data,
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => testRequestsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["test-requests"] })
      toast({ title: "Solicitud creada exitosamente" })
      handleCloseModal()
    },
    onError: () => {
      toast({ title: "Error al crear solicitud", variant: "destructive" })
    },
  })

  const handleCloseModal = () => {
    setIsModalOpen(false)
    reset({ type: "FRONT", environment: "" })
    setFrontTasks([])
    setApiScenarios([])
    setSelectedType("FRONT")
    setSelectedTaskIndex(null)
    setSelectedScenarioIndex(null)
    setNewItemName("")
    setShowAdvanced(false)
  }

  const handleAddItem = () => {
    if (!newItemName.trim()) return

    if (selectedType === "FRONT") {
      if (selectedTaskIndex !== null) {
        const updated = [...frontTasks]
        updated[selectedTaskIndex].subTasks.push({ description: newItemName.trim() })
        setFrontTasks(updated)
        toast({ title: "Subtarea agregada" })
      } else {
        const newTasks = [...frontTasks, { 
          title: newItemName.trim(), 
          description: "", 
          expectedResult: "", 
          subTasks: [] 
        }]
        setFrontTasks(newTasks)
        setSelectedTaskIndex(newTasks.length - 1)
        toast({ title: "Tarea creada" })
      }
    } else {
      if (selectedScenarioIndex !== null) {
        const updated = [...apiScenarios]
        updated[selectedScenarioIndex].endpoints.push({ method: "GET", url: "" })
        setApiScenarios(updated)
        toast({ title: "Endpoint agregado" })
      } else {
        const newScenarios = [...apiScenarios, { name: newItemName.trim(), endpoints: [] }]
        setApiScenarios(newScenarios)
        setSelectedScenarioIndex(newScenarios.length - 1)
        toast({ title: "Escenario creado" })
      }
    }
    setNewItemName("")
  }

  const onSubmit = (data: RequestForm) => {
    const payload: any = {
      title: data.title,
      applicationId: data.applicationId,
      type: data.type,
      environment: data.environment,
    }

    if (data.type === "FRONT") {
      payload.frontPlan = { tasks: frontTasks.filter(t => t.title.trim()) }
    } else {
      payload.apiPlan = { scenarios: apiScenarios.filter(s => s.name.trim()) }
    }

    if (showAdvanced) {
      if (data.azureWorkItemId) payload.azureWorkItemId = data.azureWorkItemId
      if (data.additionalNotes) payload.additionalNotes = data.additionalNotes
      if (data.hasAuth) {
        payload.hasAuth = true
        payload.authType = data.authType
      }
    }

    createMutation.mutate(payload)
  }

  const requests = requestsData?.data || []
  const applications = appsData || []

  return (
    <div className="dark min-h-screen bg-background">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-10"
        >
          <div>
            <h1 className="text-2xl font-semibold text-foreground tracking-tight">
              Test Requests
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Solicita nuevos casos de prueba automatizados
            </p>
          </div>
          <Button 
            onClick={() => setIsModalOpen(true)}
            className="gap-2"
          >
            <Plus className="w-4 h-4" />
            Nueva Solicitud
          </Button>
        </motion.div>

        {/* Filters */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap gap-3 mb-8"
        >
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 bg-card border-border"
            />
          </div>
          <Select value={appFilter} onValueChange={setAppFilter}>
            <SelectTrigger className="w-44 bg-card border-border">
              <SelectValue placeholder="Aplicación" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              {applications.map((app: Application) => (
                <SelectItem key={app.id} value={app.id}>{app.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-36 bg-card border-border">
              <SelectValue placeholder="Estado" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="NEW">Nueva</SelectItem>
              <SelectItem value="IN_ANALYSIS">En Análisis</SelectItem>
              <SelectItem value="APPROVED">Aprobada</SelectItem>
              <SelectItem value="REJECTED">Rechazada</SelectItem>
              <SelectItem value="IMPLEMENTED">Implementada</SelectItem>
            </SelectContent>
          </Select>
        </motion.div>

        {/* Request List */}
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 rounded-lg bg-card animate-pulse" />
            ))}
          </div>
        ) : requests.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
              <Layers className="w-6 h-6 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground">
              {search ? "Sin resultados" : "No hay solicitudes"}
            </p>
          </motion.div>
        ) : (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="space-y-2"
          >
            {requests.map((req: TestRequest, index: number) => (
              <motion.div
                key={req.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <Link 
                  to={`/requests/${req.id}`}
                  className="group flex items-center gap-4 p-4 rounded-lg bg-card/50 hover:bg-card border border-transparent hover:border-border transition-all duration-200"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-medium text-foreground truncate group-hover:text-primary transition-colors">
                        {req.title}
                      </h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[req.status] || "bg-muted text-muted-foreground"}`}>
                        {statusLabels[req.status] || req.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      {req.application?.name && (
                        <span className="px-2 py-0.5 rounded bg-muted/50">
                          {req.application.name}
                        </span>
                      )}
                      <span>
                        {formatDistanceToNow(new Date(req.createdAt), { addSuffix: true, locale: es })}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </Link>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>

      {/* Create Modal */}
      <Dialog open={isModalOpen} onOpenChange={(open) => !open && handleCloseModal()}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto bg-background border-border">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold">Nueva Solicitud</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 mt-4">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <Input
                  placeholder="Título de la solicitud"
                  className="bg-card border-border"
                  {...register("title", { required: true })}
                />
                {errors.title && <span className="text-xs text-destructive mt-1">Requerido</span>}
              </div>
              <Select 
                onValueChange={(value) => register("applicationId").onChange({ target: { value } })}
              >
                <SelectTrigger className="bg-card border-border">
                  <SelectValue placeholder="Aplicación" />
                </SelectTrigger>
                <SelectContent>
                  {applications.map((app: Application) => (
                    <SelectItem key={app.id} value={app.id}>{app.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select 
                onValueChange={(value) => register("environment").onChange({ target: { value } })}
              >
                <SelectTrigger className="bg-card border-border">
                  <SelectValue placeholder="Ambiente" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="DESARROLLO">Desarrollo</SelectItem>
                  <SelectItem value="TEST">Test</SelectItem>
                  <SelectItem value="PREPROD">Pre-Producción</SelectItem>
                  <SelectItem value="PROD">Producción</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Type Toggle */}
            <div className="flex gap-2 p-1 bg-muted rounded-lg w-fit">
              {[
                { value: "FRONT", label: "Interfaz", icon: Layers },
                { value: "API", label: "API", icon: Zap },
              ].map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => {
                    setSelectedType(value as "FRONT" | "API")
                    setSelectedTaskIndex(null)
                    setSelectedScenarioIndex(null)
                  }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    selectedType === value 
                      ? "bg-background text-foreground shadow-sm" 
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>

            {/* Tree Builder */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Input
                  placeholder={
                    selectedType === "FRONT"
                      ? selectedTaskIndex !== null ? "Nueva subtarea..." : "Nueva tarea..."
                      : selectedScenarioIndex !== null ? "Nuevo endpoint..." : "Nuevo escenario..."
                  }
                  value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddItem())}
                  className="flex-1 bg-card border-border"
                />
                <Button type="button" onClick={handleAddItem} disabled={!newItemName.trim()}>
                  <Plus className="w-4 h-4" />
                </Button>
              </div>

              {(selectedTaskIndex !== null || selectedScenarioIndex !== null) && (
                <button
                  type="button"
                  onClick={() => {
                    setSelectedTaskIndex(null)
                    setSelectedScenarioIndex(null)
                  }}
                  className="text-xs text-primary hover:underline"
                >
                  ← Volver a crear {selectedType === "FRONT" ? "tarea" : "escenario"}
                </button>
              )}

              {/* Tree View */}
              <div className="border border-border rounded-lg p-4 min-h-[200px] bg-card/30">
                {selectedType === "FRONT" ? (
                  frontTasks.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      Agrega tareas para el plan de prueba
                    </p>
                  ) : (
                    <div className="space-y-1">
                      {frontTasks.map((task, i) => (
                        <div key={i}>
                          <div
                            onClick={() => setSelectedTaskIndex(i)}
                            className={`group flex items-center gap-2 px-3 py-2 rounded-md cursor-pointer transition-colors ${
                              selectedTaskIndex === i 
                                ? "bg-primary/10 text-primary" 
                                : "hover:bg-muted/50"
                            }`}
                          >
                            <span className="text-xs text-muted-foreground">▸</span>
                            <span className="flex-1 text-sm truncate">{task.title}</span>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation()
                                setFrontTasks(frontTasks.filter((_, idx) => idx !== i))
                                if (selectedTaskIndex === i) setSelectedTaskIndex(null)
                              }}
                              className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-all"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                          {task.subTasks.length > 0 && (
                            <div className="ml-6 border-l border-border pl-3 space-y-1">
                              {task.subTasks.map((sub, j) => (
                                <div
                                  key={j}
                                  className="group flex items-center gap-2 px-2 py-1.5 rounded text-sm text-muted-foreground hover:bg-muted/30 transition-colors"
                                >
                                  <span className="text-xs">•</span>
                                  <span className="flex-1 truncate">{sub.description}</span>
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const updated = [...frontTasks]
                                      updated[i].subTasks = updated[i].subTasks.filter((_, idx) => idx !== j)
                                      setFrontTasks(updated)
                                    }}
                                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-all"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )
                ) : (
                  apiScenarios.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      Agrega escenarios para el plan de prueba
                    </p>
                  ) : (
                    <div className="space-y-1">
                      {apiScenarios.map((scenario, i) => (
                        <div key={i}>
                          <div
                            onClick={() => setSelectedScenarioIndex(i)}
                            className={`group flex items-center gap-2 px-3 py-2 rounded-md cursor-pointer transition-colors ${
                              selectedScenarioIndex === i 
                                ? "bg-primary/10 text-primary" 
                                : "hover:bg-muted/50"
                            }`}
                          >
                            <span className="text-xs text-muted-foreground">▸</span>
                            <span className="flex-1 text-sm truncate">{scenario.name}</span>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation()
                                setApiScenarios(apiScenarios.filter((_, idx) => idx !== i))
                                if (selectedScenarioIndex === i) setSelectedScenarioIndex(null)
                              }}
                              className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-all"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                          {scenario.endpoints.length > 0 && (
                            <div className="ml-6 border-l border-border pl-3 space-y-1">
                              {scenario.endpoints.map((ep, j) => (
                                <div
                                  key={j}
                                  className="group flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-muted/30 transition-colors"
                                >
                                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                                    {ep.method}
                                  </span>
                                  <Input
                                    value={ep.url}
                                    onChange={(e) => {
                                      const updated = [...apiScenarios]
                                      updated[i].endpoints[j].url = e.target.value
                                      setApiScenarios(updated)
                                    }}
                                    placeholder="/api/endpoint"
                                    className="flex-1 h-7 text-xs bg-transparent border-0 focus-visible:ring-0 px-0"
                                  />
                                  <button
                                    type="button"
                                    onClick={() => {
                                      const updated = [...apiScenarios]
                                      updated[i].endpoints = updated[i].endpoints.filter((_, idx) => idx !== j)
                                      setApiScenarios(updated)
                                    }}
                                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-all"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Advanced Options (Hidden by default) */}
            <div className="border-t border-border pt-4">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? "rotate-180" : ""}`} />
                Opciones avanzadas
              </button>
              
              <AnimatePresence>
                {showAdvanced && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="grid grid-cols-2 gap-4 pt-4">
                      <Input
                        placeholder="Azure Work Item ID"
                        className="bg-card border-border"
                        {...register("azureWorkItemId")}
                      />
                      <Input
                        placeholder="Azure Work Item URL"
                        className="bg-card border-border"
                        {...register("azureWorkItemUrl")}
                      />
                      <textarea
                        placeholder="Notas adicionales..."
                        className="col-span-2 min-h-[80px] rounded-md border border-border bg-card px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
                        {...register("additionalNotes")}
                      />
                      <div className="col-span-2 flex items-center gap-3">
                        <input
                          type="checkbox"
                          id="hasAuth"
                          className="rounded border-border"
                          {...register("hasAuth")}
                        />
                        <label htmlFor="hasAuth" className="text-sm text-muted-foreground">
                          Requiere autenticación
                        </label>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-border">
              <Button type="button" variant="ghost" onClick={handleCloseModal}>
                Cancelar
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creando..." : "Crear Solicitud"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
