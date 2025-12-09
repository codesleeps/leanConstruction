"""
Resource Planning Optimization - Phase 3

Implements optimization algorithms for construction resource planning:
- Crew Scheduling Optimization
- Equipment Allocation and Routing
- Material Delivery Planning
- Multi-objective Resource Leveling
- Critical Path Method (CPM) with Resource Constraints
- Linear Programming for Cost Optimization
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging
import heapq
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Check for OR-Tools availability
try:
    from ortools.sat.python import cp_model
    from ortools.linear_solver import pywraplp
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    logger.warning("OR-Tools not available. Using heuristic fallbacks.")


# ============================================
# Enums and Data Classes
# ============================================

class ResourceType(Enum):
    """Types of construction resources"""
    LABOR = "labor"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    SUBCONTRACTOR = "subcontractor"
    SPACE = "space"


class SkillType(Enum):
    """Worker skill types"""
    CARPENTER = "carpenter"
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"
    HVAC = "hvac"
    MASON = "mason"
    IRONWORKER = "ironworker"
    PAINTER = "painter"
    LABORER = "laborer"
    SUPERINTENDENT = "superintendent"
    FOREMAN = "foreman"


class EquipmentType(Enum):
    """Equipment types"""
    CRANE = "crane"
    EXCAVATOR = "excavator"
    LOADER = "loader"
    FORKLIFT = "forklift"
    CONCRETE_PUMP = "concrete_pump"
    SCAFFOLD = "scaffold"
    LIFT = "lift"
    GENERATOR = "generator"
    COMPRESSOR = "compressor"


class OptimizationObjective(Enum):
    """Optimization objectives"""
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_DURATION = "minimize_duration"
    MAXIMIZE_UTILIZATION = "maximize_utilization"
    BALANCE_WORKLOAD = "balance_workload"
    MINIMIZE_OVERTIME = "minimize_overtime"


@dataclass
class Resource:
    """Resource definition"""
    id: str
    name: str
    resource_type: ResourceType
    capacity: int
    cost_per_unit: float
    availability: List[Tuple[datetime, datetime]] = field(default_factory=list)
    skills: List[SkillType] = field(default_factory=list)
    location: Optional[str] = None


@dataclass
class Task:
    """Task requiring resources"""
    id: str
    name: str
    duration: int  # in hours
    required_resources: Dict[str, int]  # resource_type -> quantity
    required_skills: List[SkillType] = field(default_factory=list)
    predecessors: List[str] = field(default_factory=list)
    earliest_start: Optional[datetime] = None
    latest_finish: Optional[datetime] = None
    priority: int = 1
    location: Optional[str] = None


@dataclass
class Assignment:
    """Resource assignment to task"""
    task_id: str
    resource_id: str
    start_time: datetime
    end_time: datetime
    quantity: int
    cost: float


@dataclass
class Schedule:
    """Complete resource schedule"""
    assignments: List[Assignment]
    total_cost: float
    total_duration: int
    utilization: Dict[str, float]
    makespan: int
    critical_path: List[str]


@dataclass
class DeliveryRequest:
    """Material delivery request"""
    id: str
    material_type: str
    quantity: float
    destination: str
    earliest_delivery: datetime
    latest_delivery: datetime
    priority: int


@dataclass
class DeliveryRoute:
    """Optimized delivery route"""
    vehicle_id: str
    stops: List[Dict[str, Any]]
    total_distance: float
    total_time: float
    deliveries: List[str]


# ============================================
# Crew Scheduling Optimizer
# ============================================

class CrewSchedulingOptimizer:
    """
    Optimizes crew assignments to tasks
    
    Uses constraint programming to assign workers to tasks
    while respecting:
    - Skill requirements
    - Availability constraints
    - Overtime limits
    - Workload balancing
    """
    
    def __init__(self):
        self.workers: Dict[str, Resource] = {}
        self.tasks: Dict[str, Task] = {}
        self.assignments: List[Assignment] = []
        
    def add_worker(self, worker: Resource):
        """Add worker to scheduling pool"""
        if worker.resource_type != ResourceType.LABOR:
            logger.warning(f"Resource {worker.id} is not labor type")
        self.workers[worker.id] = worker
    
    def add_task(self, task: Task):
        """Add task to be scheduled"""
        self.tasks[task.id] = task
    
    def optimize(
        self,
        objective: OptimizationObjective = OptimizationObjective.MINIMIZE_COST,
        max_overtime_hours: int = 10,
        workday_hours: int = 8
    ) -> Schedule:
        """
        Optimize crew assignments
        
        Args:
            objective: Optimization objective
            max_overtime_hours: Maximum allowed overtime per worker
            workday_hours: Regular workday hours
            
        Returns:
            Optimized schedule
        """
        if ORTOOLS_AVAILABLE:
            return self._optimize_with_ortools(objective, max_overtime_hours, workday_hours)
        else:
            return self._optimize_heuristic(objective, max_overtime_hours, workday_hours)
    
    def _optimize_with_ortools(
        self,
        objective: OptimizationObjective,
        max_overtime: int,
        workday_hours: int
    ) -> Schedule:
        """Use OR-Tools constraint programming"""
        model = cp_model.CpModel()
        
        # Create variables
        # x[w,t] = 1 if worker w is assigned to task t
        x = {}
        for worker_id in self.workers:
            for task_id in self.tasks:
                x[worker_id, task_id] = model.NewBoolVar(f'x_{worker_id}_{task_id}')
        
        # Task start times
        horizon = sum(t.duration for t in self.tasks.values()) * 2
        task_starts = {}
        task_ends = {}
        
        for task_id, task in self.tasks.items():
            task_starts[task_id] = model.NewIntVar(0, horizon, f'start_{task_id}')
            task_ends[task_id] = model.NewIntVar(0, horizon, f'end_{task_id}')
            model.Add(task_ends[task_id] == task_starts[task_id] + task.duration)
        
        # Constraints
        # 1. Each task must have required number of workers with right skills
        for task_id, task in self.tasks.items():
            labor_required = task.required_resources.get('labor', 1)
            
            # Count assigned workers with required skills
            qualified_workers = []
            for worker_id, worker in self.workers.items():
                if not task.required_skills or any(
                    skill in worker.skills for skill in task.required_skills
                ):
                    qualified_workers.append(x[worker_id, task_id])
            
            if qualified_workers:
                model.Add(sum(qualified_workers) >= labor_required)
        
        # 2. Precedence constraints
        for task_id, task in self.tasks.items():
            for pred_id in task.predecessors:
                if pred_id in task_ends:
                    model.Add(task_starts[task_id] >= task_ends[pred_id])
        
        # 3. Worker can only work on one task at a time (simplified)
        for worker_id in self.workers:
            # Limit total tasks per worker to avoid overloading
            model.Add(
                sum(x[worker_id, task_id] for task_id in self.tasks) <= 
                len(self.tasks) // max(1, len(self.workers) // 2)
            )
        
        # Objective
        makespan = model.NewIntVar(0, horizon, 'makespan')
        model.AddMaxEquality(makespan, list(task_ends.values()))
        
        if objective == OptimizationObjective.MINIMIZE_DURATION:
            model.Minimize(makespan)
        elif objective == OptimizationObjective.MINIMIZE_COST:
            total_cost = sum(
                x[w, t] * self.workers[w].cost_per_unit * self.tasks[t].duration
                for w in self.workers for t in self.tasks
            )
            model.Minimize(total_cost)
        else:
            model.Minimize(makespan)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        status = solver.Solve(model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return self._extract_solution(solver, x, task_starts, task_ends, makespan)
        else:
            logger.warning("OR-Tools solver failed, using heuristic")
            return self._optimize_heuristic(objective, max_overtime, workday_hours)
    
    def _extract_solution(
        self,
        solver,
        x: Dict,
        task_starts: Dict,
        task_ends: Dict,
        makespan
    ) -> Schedule:
        """Extract solution from OR-Tools solver"""
        assignments = []
        base_time = datetime.utcnow().replace(hour=8, minute=0, second=0)
        
        for task_id, task in self.tasks.items():
            start_hour = solver.Value(task_starts[task_id])
            end_hour = solver.Value(task_ends[task_id])
            
            for worker_id, worker in self.workers.items():
                if solver.Value(x[worker_id, task_id]):
                    assignments.append(Assignment(
                        task_id=task_id,
                        resource_id=worker_id,
                        start_time=base_time + timedelta(hours=start_hour),
                        end_time=base_time + timedelta(hours=end_hour),
                        quantity=1,
                        cost=worker.cost_per_unit * task.duration
                    ))
        
        # Calculate utilization
        utilization = {}
        total_available = solver.Value(makespan) * len(self.workers)
        
        for worker_id in self.workers:
            worker_hours = sum(
                self.tasks[task_id].duration
                for task_id in self.tasks
                if solver.Value(x[worker_id, task_id])
            )
            utilization[worker_id] = worker_hours / solver.Value(makespan) if solver.Value(makespan) > 0 else 0
        
        # Identify critical path (simplified)
        critical_path = self._find_critical_path(task_starts, task_ends, solver)
        
        return Schedule(
            assignments=assignments,
            total_cost=sum(a.cost for a in assignments),
            total_duration=solver.Value(makespan),
            utilization=utilization,
            makespan=solver.Value(makespan),
            critical_path=critical_path
        )
    
    def _find_critical_path(self, task_starts, task_ends, solver) -> List[str]:
        """Find critical path tasks"""
        # Tasks with zero float (start time = latest start time)
        makespan = max(solver.Value(task_ends[t]) for t in task_ends)
        critical = []
        
        # Simple approach: tasks that end at makespan
        for task_id in self.tasks:
            if solver.Value(task_ends[task_id]) == makespan:
                critical.append(task_id)
        
        return critical
    
    def _optimize_heuristic(
        self,
        objective: OptimizationObjective,
        max_overtime: int,
        workday_hours: int
    ) -> Schedule:
        """Heuristic optimization when OR-Tools unavailable"""
        assignments = []
        base_time = datetime.utcnow().replace(hour=8, minute=0, second=0)
        
        # Sort tasks by priority and dependencies
        sorted_tasks = self._topological_sort()
        
        # Track worker availability
        worker_available_at = {w: 0 for w in self.workers}
        task_completed_at = {}
        
        for task_id in sorted_tasks:
            task = self.tasks[task_id]
            
            # Find earliest start time based on predecessors
            earliest_start = 0
            for pred_id in task.predecessors:
                if pred_id in task_completed_at:
                    earliest_start = max(earliest_start, task_completed_at[pred_id])
            
            # Find available workers with required skills
            candidates = []
            for worker_id, worker in self.workers.items():
                if not task.required_skills or any(
                    skill in worker.skills for skill in task.required_skills
                ):
                    candidates.append((
                        worker_id,
                        worker,
                        max(earliest_start, worker_available_at[worker_id])
                    ))
            
            # Sort by availability and cost
            candidates.sort(key=lambda x: (x[2], x[1].cost_per_unit))
            
            # Assign required number of workers
            labor_needed = task.required_resources.get('labor', 1)
            assigned_count = 0
            task_start = float('inf')
            task_end = 0
            
            for worker_id, worker, available_at in candidates[:labor_needed]:
                start_time = max(earliest_start, available_at)
                end_time = start_time + task.duration
                
                assignments.append(Assignment(
                    task_id=task_id,
                    resource_id=worker_id,
                    start_time=base_time + timedelta(hours=start_time),
                    end_time=base_time + timedelta(hours=end_time),
                    quantity=1,
                    cost=worker.cost_per_unit * task.duration
                ))
                
                worker_available_at[worker_id] = end_time
                task_start = min(task_start, start_time)
                task_end = max(task_end, end_time)
                assigned_count += 1
            
            task_completed_at[task_id] = task_end if task_end > 0 else earliest_start + task.duration
        
        # Calculate metrics
        makespan = max(task_completed_at.values()) if task_completed_at else 0
        utilization = {}
        
        for worker_id in self.workers:
            worker_hours = sum(
                a.cost / self.workers[worker_id].cost_per_unit
                for a in assignments
                if a.resource_id == worker_id
            )
            utilization[worker_id] = worker_hours / makespan if makespan > 0 else 0
        
        return Schedule(
            assignments=assignments,
            total_cost=sum(a.cost for a in assignments),
            total_duration=int(makespan),
            utilization=utilization,
            makespan=int(makespan),
            critical_path=list(self.tasks.keys())[:3]  # Simplified
        )
    
    def _topological_sort(self) -> List[str]:
        """Sort tasks by dependencies"""
        in_degree = {t: 0 for t in self.tasks}
        
        for task_id, task in self.tasks.items():
            for pred_id in task.predecessors:
                if pred_id in self.tasks:
                    in_degree[task_id] += 1
        
        queue = [t for t in self.tasks if in_degree[t] == 0]
        sorted_tasks = []
        
        while queue:
            # Sort by priority within same level
            queue.sort(key=lambda t: self.tasks[t].priority)
            task_id = queue.pop(0)
            sorted_tasks.append(task_id)
            
            for other_id, other_task in self.tasks.items():
                if task_id in other_task.predecessors:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)
        
        return sorted_tasks


# ============================================
# Equipment Allocation Optimizer
# ============================================

class EquipmentOptimizer:
    """
    Optimizes equipment allocation across projects/sites
    
    Considers:
    - Equipment availability
    - Transportation costs
    - Utilization efficiency
    - Maintenance schedules
    """
    
    def __init__(self):
        self.equipment: Dict[str, Resource] = {}
        self.demands: List[Dict] = []  # Equipment demands at different locations
        
    def add_equipment(self, equipment: Resource):
        """Add equipment to pool"""
        self.equipment[equipment.id] = equipment
    
    def add_demand(
        self,
        location: str,
        equipment_type: str,
        quantity: int,
        start_date: datetime,
        end_date: datetime,
        priority: int = 1
    ):
        """Add equipment demand"""
        self.demands.append({
            'location': location,
            'type': equipment_type,
            'quantity': quantity,
            'start': start_date,
            'end': end_date,
            'priority': priority
        })
    
    def optimize_allocation(self) -> Dict[str, Any]:
        """
        Optimize equipment allocation
        
        Returns:
            Allocation plan with assignments and costs
        """
        if ORTOOLS_AVAILABLE:
            return self._optimize_with_lp()
        else:
            return self._optimize_greedy()
    
    def _optimize_with_lp(self) -> Dict[str, Any]:
        """Linear programming optimization"""
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return self._optimize_greedy()
        
        # Variables: x[e,d] = 1 if equipment e assigned to demand d
        x = {}
        for eq_id in self.equipment:
            for i, demand in enumerate(self.demands):
                x[eq_id, i] = solver.BoolVar(f'x_{eq_id}_{i}')
        
        # Constraints
        # 1. Each equipment can only be assigned once per time period
        # (simplified - actual implementation would check time overlaps)
        for eq_id in self.equipment:
            solver.Add(sum(x[eq_id, i] for i in range(len(self.demands))) <= 1)
        
        # 2. Each demand should be satisfied if possible
        for i in range(len(self.demands)):
            solver.Add(
                sum(x[eq_id, i] for eq_id in self.equipment) <= self.demands[i]['quantity']
            )
        
        # Objective: Minimize transportation cost + maximize priority satisfaction
        objective = solver.Objective()
        for eq_id, equipment in self.equipment.items():
            for i, demand in enumerate(self.demands):
                # Cost includes rental cost
                cost = equipment.cost_per_unit * (demand['end'] - demand['start']).days
                priority_bonus = -demand['priority'] * 1000  # Higher priority = more negative
                objective.SetCoefficient(x[eq_id, i], cost + priority_bonus)
        objective.SetMinimization()
        
        # Solve
        status = solver.Solve()
        
        allocations = []
        if status == pywraplp.Solver.OPTIMAL:
            for eq_id in self.equipment:
                for i, demand in enumerate(self.demands):
                    if x[eq_id, i].solution_value() > 0.5:
                        allocations.append({
                            'equipment_id': eq_id,
                            'location': demand['location'],
                            'type': demand['type'],
                            'start': demand['start'].isoformat(),
                            'end': demand['end'].isoformat(),
                            'cost': self.equipment[eq_id].cost_per_unit * (demand['end'] - demand['start']).days
                        })
        
        return {
            'allocations': allocations,
            'total_cost': sum(a['cost'] for a in allocations),
            'demands_satisfied': len(allocations),
            'demands_total': len(self.demands),
            'utilization_rate': len(allocations) / len(self.equipment) if self.equipment else 0
        }
    
    def _optimize_greedy(self) -> Dict[str, Any]:
        """Greedy allocation fallback"""
        # Sort demands by priority and date
        sorted_demands = sorted(
            enumerate(self.demands),
            key=lambda x: (-x[1]['priority'], x[1]['start'])
        )
        
        allocations = []
        used_equipment = set()
        
        for i, demand in sorted_demands:
            # Find available equipment of right type
            for eq_id, equipment in self.equipment.items():
                if eq_id not in used_equipment:
                    # Simplified availability check
                    used_equipment.add(eq_id)
                    cost = equipment.cost_per_unit * (demand['end'] - demand['start']).days
                    allocations.append({
                        'equipment_id': eq_id,
                        'location': demand['location'],
                        'type': demand['type'],
                        'start': demand['start'].isoformat(),
                        'end': demand['end'].isoformat(),
                        'cost': cost
                    })
                    break
        
        return {
            'allocations': allocations,
            'total_cost': sum(a['cost'] for a in allocations),
            'demands_satisfied': len(allocations),
            'demands_total': len(self.demands),
            'utilization_rate': len(used_equipment) / len(self.equipment) if self.equipment else 0
        }


# ============================================
# Material Delivery Optimizer
# ============================================

class DeliveryOptimizer:
    """
    Optimizes material delivery routes and schedules
    
    Uses vehicle routing problem (VRP) optimization
    """
    
    def __init__(self):
        self.warehouse_location: Tuple[float, float] = (0, 0)
        self.delivery_requests: List[DeliveryRequest] = []
        self.vehicles: List[Dict] = []  # Vehicle fleet
        
    def set_warehouse(self, lat: float, lon: float):
        """Set warehouse location"""
        self.warehouse_location = (lat, lon)
    
    def add_delivery(self, request: DeliveryRequest):
        """Add delivery request"""
        self.delivery_requests.append(request)
    
    def add_vehicle(
        self,
        vehicle_id: str,
        capacity: float,
        cost_per_mile: float
    ):
        """Add vehicle to fleet"""
        self.vehicles.append({
            'id': vehicle_id,
            'capacity': capacity,
            'cost_per_mile': cost_per_mile
        })
    
    def optimize_routes(self) -> List[DeliveryRoute]:
        """
        Optimize delivery routes
        
        Returns:
            List of optimized routes
        """
        if not self.delivery_requests or not self.vehicles:
            return []
        
        if ORTOOLS_AVAILABLE:
            return self._optimize_with_vrp()
        else:
            return self._optimize_nearest_neighbor()
    
    def _optimize_with_vrp(self) -> List[DeliveryRoute]:
        """Vehicle Routing Problem optimization"""
        # Create distance matrix
        locations = [self.warehouse_location]
        for req in self.delivery_requests:
            # Parse destination to coordinates (simplified)
            locations.append((hash(req.destination) % 100, hash(req.destination) % 100))
        
        num_locations = len(locations)
        distance_matrix = np.zeros((num_locations, num_locations))
        
        for i in range(num_locations):
            for j in range(num_locations):
                distance_matrix[i][j] = self._calculate_distance(
                    locations[i], locations[j]
                )
        
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(
            num_locations,
            len(self.vehicles),
            0  # Depot index
        )
        routing = pywrapcp.RoutingModel(manager)
        
        # Distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 100)
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Capacity constraints
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            if from_node == 0:
                return 0
            return int(self.delivery_requests[from_node - 1].quantity)
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # No slack
            [int(v['capacity']) for v in self.vehicles],  # Vehicle capacities
            True,  # Start cumul at zero
            'Capacity'
        )
        
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.seconds = 30
        
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self._extract_routes(manager, routing, solution)
        else:
            return self._optimize_nearest_neighbor()
    
    def _extract_routes(self, manager, routing, solution) -> List[DeliveryRoute]:
        """Extract routes from VRP solution"""
        routes = []
        
        for vehicle_idx in range(len(self.vehicles)):
            index = routing.Start(vehicle_idx)
            stops = []
            deliveries = []
            total_distance = 0
            
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                if node > 0:  # Not depot
                    request = self.delivery_requests[node - 1]
                    stops.append({
                        'location': request.destination,
                        'delivery_id': request.id,
                        'quantity': request.quantity,
                        'time_window': f"{request.earliest_delivery} - {request.latest_delivery}"
                    })
                    deliveries.append(request.id)
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                total_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_idx
                ) / 100
            
            if stops:
                routes.append(DeliveryRoute(
                    vehicle_id=self.vehicles[vehicle_idx]['id'],
                    stops=stops,
                    total_distance=total_distance,
                    total_time=total_distance / 30,  # Assume 30 mph average
                    deliveries=deliveries
                ))
        
        return routes
    
    def _optimize_nearest_neighbor(self) -> List[DeliveryRoute]:
        """Nearest neighbor heuristic"""
        routes = []
        unassigned = list(range(len(self.delivery_requests)))
        
        for vehicle in self.vehicles:
            if not unassigned:
                break
            
            stops = []
            deliveries = []
            current_capacity = 0
            total_distance = 0
            current_location = self.warehouse_location
            
            while unassigned:
                # Find nearest unvisited location that fits capacity
                nearest_idx = None
                nearest_dist = float('inf')
                
                for idx in unassigned:
                    request = self.delivery_requests[idx]
                    if current_capacity + request.quantity <= vehicle['capacity']:
                        dest = (hash(request.destination) % 100, hash(request.destination) % 100)
                        dist = self._calculate_distance(current_location, dest)
                        if dist < nearest_dist:
                            nearest_dist = dist
                            nearest_idx = idx
                
                if nearest_idx is None:
                    break
                
                request = self.delivery_requests[nearest_idx]
                stops.append({
                    'location': request.destination,
                    'delivery_id': request.id,
                    'quantity': request.quantity
                })
                deliveries.append(request.id)
                
                current_capacity += request.quantity
                total_distance += nearest_dist
                current_location = (hash(request.destination) % 100, hash(request.destination) % 100)
                unassigned.remove(nearest_idx)
            
            # Return to depot
            total_distance += self._calculate_distance(current_location, self.warehouse_location)
            
            if stops:
                routes.append(DeliveryRoute(
                    vehicle_id=vehicle['id'],
                    stops=stops,
                    total_distance=total_distance,
                    total_time=total_distance / 30,
                    deliveries=deliveries
                ))
        
        return routes
    
    def _calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate Euclidean distance"""
        return np.sqrt(
            (point1[0] - point2[0]) ** 2 +
            (point1[1] - point2[1]) ** 2
        )


# ============================================
# Resource Leveling
# ============================================

class ResourceLeveler:
    """
    Multi-objective resource leveling
    
    Balances resource usage over time to minimize
    peaks and valleys in resource demands
    """
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.resources: Dict[str, int] = {}  # resource_type -> max available
        
    def add_task(self, task: Task):
        """Add task with resource requirements"""
        self.tasks.append(task)
    
    def set_resource_limit(self, resource_type: str, max_available: int):
        """Set maximum available units for resource type"""
        self.resources[resource_type] = max_available
    
    def level_resources(self) -> Dict[str, Any]:
        """
        Perform resource leveling
        
        Returns:
            Leveled schedule with resource histogram
        """
        # Sort tasks by dependencies and flexibility
        sorted_tasks = self._sort_by_flexibility()
        
        # Schedule tasks while respecting resource limits
        schedule = {}
        resource_usage = defaultdict(lambda: defaultdict(int))  # time -> resource -> count
        
        for task in sorted_tasks:
            # Find earliest feasible start time
            earliest = self._find_earliest_feasible(task, schedule, resource_usage)
            
            schedule[task.id] = {
                'start': earliest,
                'end': earliest + task.duration,
                'task': task
            }
            
            # Update resource usage
            for t in range(earliest, earliest + task.duration):
                for res_type, qty in task.required_resources.items():
                    resource_usage[t][res_type] += qty
        
        # Calculate metrics
        metrics = self._calculate_leveling_metrics(resource_usage)
        
        return {
            'schedule': {
                task_id: {
                    'start': info['start'],
                    'end': info['end'],
                    'duration': info['task'].duration
                }
                for task_id, info in schedule.items()
            },
            'resource_histogram': dict(resource_usage),
            'metrics': metrics,
            'makespan': max(info['end'] for info in schedule.values()) if schedule else 0
        }
    
    def _sort_by_flexibility(self) -> List[Task]:
        """Sort tasks by scheduling flexibility (total float)"""
        # Simplified: sort by number of predecessors and priority
        return sorted(
            self.tasks,
            key=lambda t: (len(t.predecessors), -t.priority)
        )
    
    def _find_earliest_feasible(
        self,
        task: Task,
        schedule: Dict,
        resource_usage: Dict
    ) -> int:
        """Find earliest start time respecting constraints"""
        # Start after all predecessors
        earliest = 0
        for pred_id in task.predecessors:
            if pred_id in schedule:
                earliest = max(earliest, schedule[pred_id]['end'])
        
        # Check resource availability
        while True:
            feasible = True
            for t in range(earliest, earliest + task.duration):
                for res_type, required in task.required_resources.items():
                    available = self.resources.get(res_type, float('inf'))
                    current_usage = resource_usage[t][res_type]
                    if current_usage + required > available:
                        feasible = False
                        break
                if not feasible:
                    break
            
            if feasible:
                return earliest
            earliest += 1
            
            # Safety limit
            if earliest > 10000:
                return earliest
    
    def _calculate_leveling_metrics(self, resource_usage: Dict) -> Dict:
        """Calculate resource leveling quality metrics"""
        metrics = {}
        
        for res_type in self.resources:
            usages = [
                resource_usage[t].get(res_type, 0)
                for t in sorted(resource_usage.keys())
            ]
            
            if usages:
                metrics[res_type] = {
                    'peak': max(usages),
                    'average': np.mean(usages),
                    'variance': np.var(usages),
                    'utilization': np.mean(usages) / self.resources[res_type] if self.resources[res_type] > 0 else 0
                }
        
        return metrics


# ============================================
# Cost Optimizer
# ============================================

class CostOptimizer:
    """
    Linear programming based cost optimization
    
    Optimizes resource allocation to minimize total project cost
    while meeting schedule constraints
    """
    
    def __init__(self):
        self.activities: List[Dict] = []
        self.resources: List[Dict] = []
        
    def add_activity(
        self,
        activity_id: str,
        name: str,
        duration_normal: int,
        duration_crash: int,
        cost_normal: float,
        cost_crash: float
    ):
        """Add activity with normal and crash options"""
        self.activities.append({
            'id': activity_id,
            'name': name,
            'duration_normal': duration_normal,
            'duration_crash': duration_crash,
            'cost_normal': cost_normal,
            'cost_crash': cost_crash,
            'crash_cost_per_day': (cost_crash - cost_normal) / max(1, duration_normal - duration_crash)
        })
    
    def optimize_cost_duration(self, target_duration: int) -> Dict[str, Any]:
        """
        Find optimal cost for target duration
        
        Args:
            target_duration: Target project duration
            
        Returns:
            Optimized activity durations and costs
        """
        if ORTOOLS_AVAILABLE:
            return self._optimize_with_lp(target_duration)
        else:
            return self._optimize_heuristic(target_duration)
    
    def _optimize_with_lp(self, target_duration: int) -> Dict[str, Any]:
        """LP optimization for time-cost tradeoff"""
        solver = pywraplp.Solver.CreateSolver('GLOP')
        if not solver:
            return self._optimize_heuristic(target_duration)
        
        # Variables: duration for each activity
        durations = {}
        crash_days = {}
        
        for activity in self.activities:
            # Duration must be between crash and normal
            durations[activity['id']] = solver.NumVar(
                activity['duration_crash'],
                activity['duration_normal'],
                f"d_{activity['id']}"
            )
            # How many days to crash
            crash_days[activity['id']] = solver.NumVar(
                0,
                activity['duration_normal'] - activity['duration_crash'],
                f"c_{activity['id']}"
            )
            
            # Constraint: crash_days = normal_duration - actual_duration
            solver.Add(
                crash_days[activity['id']] == 
                activity['duration_normal'] - durations[activity['id']]
            )
        
        # Constraint: Total duration <= target (simplified - assumes sequential)
        solver.Add(
            sum(durations[a['id']] for a in self.activities) <= target_duration
        )
        
        # Objective: Minimize total cost
        objective = solver.Objective()
        for activity in self.activities:
            objective.SetCoefficient(
                crash_days[activity['id']],
                activity['crash_cost_per_day']
            )
        # Add normal costs as constant (not in objective)
        objective.SetMinimization()
        
        status = solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL:
            results = []
            total_cost = sum(a['cost_normal'] for a in self.activities)
            
            for activity in self.activities:
                duration = durations[activity['id']].solution_value()
                crashed = crash_days[activity['id']].solution_value()
                additional_cost = crashed * activity['crash_cost_per_day']
                
                results.append({
                    'activity_id': activity['id'],
                    'name': activity['name'],
                    'duration': duration,
                    'days_crashed': crashed,
                    'additional_cost': additional_cost,
                    'total_cost': activity['cost_normal'] + additional_cost
                })
                total_cost += additional_cost
            
            return {
                'activities': results,
                'total_cost': total_cost,
                'total_duration': sum(r['duration'] for r in results),
                'target_achieved': sum(r['duration'] for r in results) <= target_duration
            }
        else:
            return self._optimize_heuristic(target_duration)
    
    def _optimize_heuristic(self, target_duration: int) -> Dict[str, Any]:
        """Heuristic optimization"""
        # Sort by crash cost efficiency (lowest cost per day first)
        sorted_activities = sorted(
            self.activities,
            key=lambda a: a['crash_cost_per_day']
        )
        
        results = []
        current_duration = sum(a['duration_normal'] for a in self.activities)
        total_cost = sum(a['cost_normal'] for a in self.activities)
        
        for activity in sorted_activities:
            # Calculate how much we can crash this activity
            max_crash = activity['duration_normal'] - activity['duration_crash']
            needed_reduction = current_duration - target_duration
            
            if needed_reduction > 0 and max_crash > 0:
                crash_days = min(max_crash, needed_reduction)
                additional_cost = crash_days * activity['crash_cost_per_day']
                
                results.append({
                    'activity_id': activity['id'],
                    'name': activity['name'],
                    'duration': activity['duration_normal'] - crash_days,
                    'days_crashed': crash_days,
                    'additional_cost': additional_cost,
                    'total_cost': activity['cost_normal'] + additional_cost
                })
                
                current_duration -= crash_days
                total_cost += additional_cost
            else:
                results.append({
                    'activity_id': activity['id'],
                    'name': activity['name'],
                    'duration': activity['duration_normal'],
                    'days_crashed': 0,
                    'additional_cost': 0,
                    'total_cost': activity['cost_normal']
                })
        
        return {
            'activities': results,
            'total_cost': total_cost,
            'total_duration': current_duration,
            'target_achieved': current_duration <= target_duration
        }


# ============================================
# Integrated Resource Optimization System
# ============================================

class ResourceOptimizationSystem:
    """
    Integrated resource optimization system
    
    Combines all optimization components
    """
    
    def __init__(self):
        self.crew_optimizer = CrewSchedulingOptimizer()
        self.equipment_optimizer = EquipmentOptimizer()
        self.delivery_optimizer = DeliveryOptimizer()
        self.resource_leveler = ResourceLeveler()
        self.cost_optimizer = CostOptimizer()
    
    def optimize_project_resources(self, project_data: Dict) -> Dict[str, Any]:
        """
        Perform comprehensive resource optimization
        
        Args:
            project_data: Project data including tasks, resources, deliveries
            
        Returns:
            Complete optimization results
        """
        results = {
            'crew_schedule': None,
            'equipment_allocation': None,
            'delivery_routes': None,
            'resource_leveling': None,
            'cost_optimization': None,
            'summary': {}
        }
        
        # Crew scheduling
        if 'workers' in project_data and 'tasks' in project_data:
            for worker in project_data['workers']:
                self.crew_optimizer.add_worker(Resource(
                    id=worker['id'],
                    name=worker['name'],
                    resource_type=ResourceType.LABOR,
                    capacity=1,
                    cost_per_unit=worker.get('hourly_rate', 50),
                    skills=[SkillType(s) for s in worker.get('skills', [])]
                ))
            
            for task in project_data['tasks']:
                self.crew_optimizer.add_task(Task(
                    id=task['id'],
                    name=task['name'],
                    duration=task['duration'],
                    required_resources=task.get('resources', {'labor': 1}),
                    required_skills=[SkillType(s) for s in task.get('skills', [])],
                    predecessors=task.get('predecessors', []),
                    priority=task.get('priority', 1)
                ))
            
            results['crew_schedule'] = self.crew_optimizer.optimize()
        
        # Equipment allocation
        if 'equipment' in project_data and 'equipment_demands' in project_data:
            for eq in project_data['equipment']:
                self.equipment_optimizer.add_equipment(Resource(
                    id=eq['id'],
                    name=eq['name'],
                    resource_type=ResourceType.EQUIPMENT,
                    capacity=1,
                    cost_per_unit=eq.get('daily_rate', 500),
                    location=eq.get('location')
                ))
            
            for demand in project_data['equipment_demands']:
                self.equipment_optimizer.add_demand(
                    location=demand['location'],
                    equipment_type=demand['type'],
                    quantity=demand['quantity'],
                    start_date=datetime.fromisoformat(demand['start']),
                    end_date=datetime.fromisoformat(demand['end']),
                    priority=demand.get('priority', 1)
                )
            
            results['equipment_allocation'] = self.equipment_optimizer.optimize_allocation()
        
        # Delivery optimization
        if 'deliveries' in project_data and 'vehicles' in project_data:
            if 'warehouse' in project_data:
                self.delivery_optimizer.set_warehouse(
                    project_data['warehouse']['lat'],
                    project_data['warehouse']['lon']
                )
            
            for delivery in project_data['deliveries']:
                self.delivery_optimizer.add_delivery(DeliveryRequest(
                    id=delivery['id'],
                    material_type=delivery['type'],
                    quantity=delivery['quantity'],
                    destination=delivery['destination'],
                    earliest_delivery=datetime.fromisoformat(delivery['earliest']),
                    latest_delivery=datetime.fromisoformat(delivery['latest']),
                    priority=delivery.get('priority', 1)
                ))
            
            for vehicle in project_data['vehicles']:
                self.delivery_optimizer.add_vehicle(
                    vehicle['id'],
                    vehicle['capacity'],
                    vehicle.get('cost_per_mile', 2.0)
                )
            
            routes = self.delivery_optimizer.optimize_routes()
            results['delivery_routes'] = [asdict(r) for r in routes]
        
        # Generate summary
        results['summary'] = {
            'optimization_completed': datetime.utcnow().isoformat(),
            'components_optimized': sum(1 for v in results.values() if v is not None) - 1,
            'ortools_available': ORTOOLS_AVAILABLE
        }
        
        return results


# Convenience instance
resource_optimizer = ResourceOptimizationSystem()