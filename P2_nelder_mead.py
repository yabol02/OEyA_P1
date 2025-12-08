from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon

# Type alias for objective functions
ObjectiveFunction = Callable[[np.ndarray], float]


@dataclass(frozen=True)
class NelderMeadParameters:
    """
    Parameters for the Nelder-Mead algorithm.

    Attributes:
        `rho`: Reflection coefficient (default: 1.0)
        `delta`: Expansion coefficient (default: 2.0)
        `gamma`: Contraction coefficient (default: 0.5)
        `sigma`: Shrinkage coefficient (default: 0.5)
        `max_iterations`: Maximum number of iterations (default: 1000)
        `diameter_tol`: Tolerance for simplex diameter (default: 1e-6)
        `variance_tol`: Tolerance for function value variance (default: 1e-6)
    """

    rho: float = 1.0
    delta: float = 2.0
    gamma: float = 0.5
    sigma: float = 0.5
    max_iterations: int = 1000
    diameter_tol: float = 1e-6
    variance_tol: float = 1e-6

    def __post_init__(self) -> None:
        """
        Validate parameters after initialization.

        Raises:
            `ValueError`: If any parameter is out of valid range.
        """
        if not (0 < self.rho < self.delta):
            raise ValueError(
                f"Reflection coefficient ({self.rho}) must be positive and "
                f"less than expansion coefficient ({self.delta})"
            )
        if self.delta <= 1:
            raise ValueError(
                f"Expansion coefficient ({self.delta}) must be greater than 1"
            )
        if not (0 < self.gamma < 1):
            raise ValueError(
                f"Contraction coefficient ({self.gamma}) must be in (0, 1)"
            )
        if not (0 < self.sigma < 1):
            raise ValueError(f"Shrinkage coefficient ({self.sigma}) must be in (0, 1)")
        if self.max_iterations <= 0:
            raise ValueError("Maximum iterations must be positive")


@dataclass
class OptimizationResult:
    """
    Result of optimization.

    Attributes:
        `x_opt`: Optimal point found
        `f_opt`: Optimal function value
        `iterations`: Number of iterations performed
        `converged`: Whether the algorithm converged
        `simplex`: Final simplex vertices
        `function_values`: Final function values at simplex vertices
        `execution_time`: Time taken for optimization (seconds)
        `function_evaluations`: Total number of function evaluations
        `history`: History of simplex vertices at each iteration (if tracked)
    """

    x_opt: np.ndarray
    f_opt: float
    iterations: int
    converged: bool
    simplex: np.ndarray
    function_values: np.ndarray
    execution_time: float
    function_evaluations: int
    history: Optional[list[np.ndarray]] = None

    def __repr__(self) -> str:
        status = "converged" if self.converged else "max iterations reached"
        return (
            f"OptimizationResult(\n"
            f"  x_opt={self.x_opt},\n"
            f"  f_opt={self.f_opt:.6e},\n"
            f"  iterations={self.iterations},\n"
            f"  function_evaluations={self.function_evaluations},\n"
            f"  execution_time={self.execution_time:.4f}s,\n"
            f"  status={status}\n"
            f")"
        )


class Simplex:
    """
    Represents a simplex for optimization.

    Optimized for performance with minimal memory allocations.
    """

    # For memory optimization
    __slots__ = ("_vertices",)

    def __init__(self, vertices: np.ndarray):
        """
        Initialize simplex with vertices.

        Args:
            `vertices`: Array of shape (n+1, n) containing simplex vertices
        """
        self._vertices = np.asarray(vertices, dtype=np.float64, order="C")
        self._validate()

    def _validate(self) -> None:
        """
        Validate simplex structure.

        Raises:
            `ValueError`: If vertices are not in correct shape.
        """
        if self._vertices.ndim != 2:
            raise ValueError("Vertices must be a 2D array")

        n_vertices, dim = self._vertices.shape
        if n_vertices != dim + 1:
            raise ValueError(
                f"Simplex must have {dim + 1} vertices for {dim}D space, got {n_vertices}"
            )

    @property
    def vertices(self) -> np.ndarray:
        """
        Get simplex vertices.
        """
        return self._vertices

    @property
    def dimension(self) -> int:
        """
        Get dimension of the space.
        """
        return self._vertices.shape[1]

    @property
    def n_vertices(self) -> int:
        """
        Get number of vertices.
        """
        return self._vertices.shape[0]

    def centroid(self, exclude_worst: bool = True) -> np.ndarray:
        """
        Calculate centroid of simplex (optimized).
        """
        if exclude_worst:
            return np.mean(self._vertices[:-1], axis=0)
        return np.mean(self._vertices, axis=0)

    def diameter(self) -> float:
        """
        Calculate diameter using vectorized operations.
        """
        diff = self._vertices[:, np.newaxis, :] - self._vertices[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff * diff, axis=2))
        return np.max(distances)

    def replace_vertex(self, index: int, new_vertex: np.ndarray) -> None:
        """
        Replace a vertex in the simplex (in-place).

        Args:
            `index`: Index of the vertex to replace
            `new_vertex`: New vertex coordinates
        """
        self._vertices[index] = new_vertex

    @classmethod
    def create_standard(cls, x0: np.ndarray, scale: float = 1.0) -> Simplex:
        """
        Create a standard simplex around an initial point.

        Args:
            `x0`: Initial point (center of simplex)
            `scale`: Scale factor for simplex size

        Returns:
            Standard simplex centered at x0
        """
        x0 = np.asarray(x0, dtype=np.float64)
        dim = x0.size
        vertices = np.tile(x0, (dim + 1, 1))
        vertices[1:] += np.eye(dim) * scale

        return cls(vertices)


class NelderMead:
    """
    Nelder-Mead simplex optimization algorithm.
    """

    # For memory optimization
    __slots__ = (
        "_params",
        "_objective",
        "_simplex",
        "_function_values",
        "_iteration",
        "_function_evals",
        "_track_history",
        "_history",
    )

    def __init__(self, parameters: Optional[NelderMeadParameters] = None):
        """
        Initialize optimizer.

        Args:
            `parameters`: Algorithm parameters (uses defaults if None)
        """
        self._params = parameters or NelderMeadParameters()
        self._objective: Optional[ObjectiveFunction] = None
        self._simplex: Optional[Simplex] = None
        self._function_values: Optional[np.ndarray] = None
        self._iteration: int = 0
        self._function_evals: int = 0
        self._track_history: bool = False
        self._history: list[np.ndarray] = []

    @property
    def parameters(self) -> NelderMeadParameters:
        """
        Get algorithm parameters.
        """
        return self._params

    def optimize(
        self,
        objective: ObjectiveFunction,
        x0: Optional[np.ndarray] = None,
        initial_simplex: Optional[np.ndarray] = None,
        track_history: bool = False,
        verbose: bool = False,
    ) -> OptimizationResult:
        """
        Optimize the objective function.

        Args:
            `objective`: Function to minimize, must accept np.ndarray and return float
            `x0`: Initial point (used if initial_simplex is None)
            `initial_simplex`: Initial simplex vertices (n+1 x n array)
            `track_history`: If True, store simplex history for visualization
            `verbose`: If True, print progress information

        Returns:
            Optimization result
        """
        start_time = time.perf_counter()
        self._objective = objective
        self._track_history = track_history
        self._history = []
        self._function_evals = 0

        self._initialize_simplex(x0, initial_simplex)

        if verbose:
            print(f"{'Iter':<6} {'f(x_best)':<15} {'Diameter':<15} {'Operation':<15}")
            print("-" * 51)

        for self._iteration in range(self._params.max_iterations):
            self._sort_simplex()

            if self._track_history:
                self._history.append(self._simplex.vertices.copy())

            if verbose:
                diameter = self._simplex.diameter()
                print(
                    f"{self._iteration:<6} {self._function_values[0]:<15.6e} {diameter:<15.6e}",
                    end=" ",
                )

            if self._check_convergence():
                if verbose:
                    print(f"\nConverged at iteration {self._iteration}")
                break

            operation = self._perform_iteration()

            if verbose:
                print(operation)

        execution_time = time.perf_counter() - start_time

        if verbose:
            print(f"\nOptimization completed in {execution_time:.4f}s")
            print(f"Function evaluations: {self._function_evals}")

        return self._create_result(
            converged=self._iteration < self._params.max_iterations - 1,
            execution_time=execution_time,
        )

    def _initialize_simplex(
        self, x0: Optional[np.ndarray], initial_simplex: Optional[np.ndarray]
    ) -> None:
        """
        Initialize the simplex.
        Args:
            `x0`: Initial point (used if initial_simplex is None)
            `initial_simplex`: Initial simplex vertices (n+1 × n)
        """
        if initial_simplex is not None:
            self._simplex = Simplex(np.asarray(initial_simplex))
        elif x0 is not None:
            x0_array = np.asarray(x0, dtype=np.float64)
            self._simplex = Simplex.create_standard(x0_array)
        else:
            raise ValueError("Either x0 or initial_simplex must be provided")

        self._evaluate_simplex()

    def _evaluate_simplex(self) -> None:
        """
        Evaluate objective function at all simplex vertices.
        """
        n = self._simplex.n_vertices
        self._function_values = np.empty(n, dtype=np.float64)
        for i in range(n):
            self._function_values[i] = self._objective(self._simplex.vertices[i])
            self._function_evals += 1

    def _sort_simplex(self) -> None:
        """
        Sort simplex by function values (best to worst).
        """
        indices = np.argsort(self._function_values)
        self._simplex._vertices = self._simplex.vertices[indices]
        self._function_values = self._function_values[indices]

    def _check_convergence(self) -> bool:
        """
        Check if algorithm has converged.
        """
        if self._simplex.diameter() < self._params.diameter_tol:
            return True

        variance = np.var(self._function_values)
        if variance < self._params.variance_tol:
            return True

        return False

    def _perform_iteration(self) -> str:
        """
        Perform one iteration and return operation name.
        """
        f_best = self._function_values[0]
        f_second_worst = self._function_values[-2]
        f_worst = self._function_values[-1]

        # Reflection
        centroid = self._simplex.centroid(exclude_worst=True)
        x_r = centroid + self._params.rho * (
            centroid - self._simplex.vertices[-1]
        )
        f_r = self._objective(x_r)
        self._function_evals += 1

        if f_best <= f_r < f_second_worst:
            self._accept_point(x_r, f_r)
            return "reflection"
        elif f_r < f_best:
            # Expansion
            x_e = centroid + self._params.delta * (x_r - centroid)
            f_e = self._objective(x_e)
            self._function_evals += 1

            if f_e < f_r:
                self._accept_point(x_e, f_e)
                return "expansion"
            else:
                self._accept_point(x_r, f_r)
                return "reflection"
        else:
            # Contraction
            if f_second_worst <= f_r < f_worst:
                # Outside contraction
                x_ce = centroid + self._params.gamma * (x_r - centroid)
                f_ce = self._objective(x_ce)
                self._function_evals += 1

                if f_ce <= f_r:
                    self._accept_point(x_ce, f_ce)
                    return "out_contraction"
            else:
                # Inside contraction
                x_ci = centroid + self._params.gamma * (
                    centroid - self._simplex.vertices[-1]
                )
                f_ci = self._objective(x_ci)
                self._function_evals += 1

                if f_ci < f_worst:
                    self._accept_point(x_ci, f_ci)
                    return "in_contraction"

            # Shrink
            self._shrink()
            return "shrinkage"

    def _shrink(self) -> None:
        """
        Shrink simplex toward best vertex.
        """
        best = self._simplex.vertices[0]

        for i in range(1, self._simplex.n_vertices):
            new_vertex = best + self._params.sigma * (self._simplex.vertices[i] - best)
            self._simplex.replace_vertex(i, new_vertex)
            self._function_values[i] = self._objective(new_vertex)
            self._function_evals += 1

    def _accept_point(self, point: np.ndarray, value: float) -> None:
        """
        Replace worst vertex with new point.
        """
        self._simplex.replace_vertex(-1, point)
        self._function_values[-1] = value

    def _create_result(
        self, converged: bool, execution_time: float
    ) -> OptimizationResult:
        """
        Create optimization result.
        """
        return OptimizationResult(
            x_opt=self._simplex.vertices[0].copy(),
            f_opt=self._function_values[0],
            iterations=self._iteration + 1,
            converged=converged,
            simplex=self._simplex.vertices.copy(),
            function_values=self._function_values.copy(),
            execution_time=execution_time,
            function_evaluations=self._function_evals,
            history=self._history if self._track_history else None,
        )


class NelderMeadVisualizer:
    """
    Visualization tools for Nelder-Mead optimization.
    """

    @staticmethod
    def plot_optimization_2d(
        result: OptimizationResult,
        objective: ObjectiveFunction,
        bounds: tuple[tuple[float, float], tuple[float, float]],
        n_points: int = 100,
        show_contours: bool = True,
        figsize: tuple[int, int] = (10, 8),
    ) -> plt.Figure:
        """
        Plot 2D optimization result with contours.

        Args:
            `result`: Optimization result
            `objective`: Objective function
            `bounds`: ((x_min, x_max), (y_min, y_max))
            `n_points`: Number of points for contour plot
            `show_contours`: Whether to show contour lines
            `figsize`: Figure size

        Returns:
            Matplotlib figure

        Raises:
            `ValueError`: If problem is not 2D
        """
        if result.x_opt.size != 2:
            raise ValueError("plot_optimization_2d only works for 2D problems")

        fig, ax = plt.subplots(figsize=figsize)

        (x_min, x_max), (y_min, y_max) = bounds
        x = np.linspace(x_min, x_max, n_points)
        y = np.linspace(y_min, y_max, n_points)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)

        for i in range(n_points):
            for j in range(n_points):
                Z[i, j] = objective(np.array([X[i, j], Y[i, j]]))

        if show_contours:
            contour = ax.contour(X, Y, Z, levels=30, alpha=0.6, cmap="viridis")
            ax.clabel(contour, inline=True, fontsize=8)

        contourf = ax.contourf(X, Y, Z, levels=50, alpha=0.3, cmap="viridis")
        plt.colorbar(contourf, ax=ax, label="f(x)")

        simplex = result.simplex
        triangle = Polygon(
            simplex, fill=False, edgecolor="red", linewidth=2, label="Final simplex"
        )
        ax.add_patch(triangle)

        ax.plot(
            simplex[:, 0], simplex[:, 1], "ro", markersize=8, label="Simplex vertices"
        )

        ax.plot(
            result.x_opt[0],
            result.x_opt[1],
            "g*",
            markersize=20,
            label=f"Optimum: f={result.f_opt:.4e}",
            zorder=5,
        )

        ax.set_xlabel("x₁")
        ax.set_ylabel("x₂")
        ax.set_title(f"Nelder-Mead Optimization (Iterations: {result.iterations})")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    @staticmethod
    def animate_optimization_2d(
        result: OptimizationResult,
        objective: ObjectiveFunction,
        bounds: tuple[tuple[float, float], tuple[float, float]],
        n_points: int = 100,
        interval: int = 200,
        save_path: Optional[str] = None,
    ) -> FuncAnimation:
        """
        Create animation of 2D optimization process.

        Args:
            `result`: Optimization result (must have history)
            `objective`: Objective function
            `bounds`: ((x_min, x_max), (y_min, y_max))
            `n_points`: Number of points for contour plot
            `interval`: Delay between frames in milliseconds
            `save_path`: Path to save animation (e.g., 'optimization.gif')

        Returns:
            Animation object

        Raises:
            `ValueError`: If result has no history or is not 2D
        """
        if result.history is None:
            raise ValueError(
                "Result must have history. Use track_history=True in optimize()"
            )

        if result.x_opt.size != 2:
            raise ValueError("animate_optimization_2d only works for 2D problems")

        fig, ax = plt.subplots(figsize=(10, 8))

        (x_min, x_max), (y_min, y_max) = bounds
        x = np.linspace(x_min, x_max, n_points)
        y = np.linspace(y_min, y_max, n_points)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)

        for i in range(n_points):
            for j in range(n_points):
                Z[i, j] = objective(np.array([X[i, j], Y[i, j]]))

        contourf = ax.contourf(X, Y, Z, levels=50, alpha=0.3, cmap="viridis")
        plt.colorbar(contourf, ax=ax, label="f(x)")

        ax.set_xlabel("x₁")
        ax.set_ylabel("x₂")
        ax.grid(True, alpha=0.3)

        simplex_patch = Polygon(
            result.history[0], fill=False, edgecolor="red", linewidth=2
        )
        ax.add_patch(simplex_patch)

        (vertices_plot,) = ax.plot([], [], "ro", markersize=8)
        title = ax.text(0.5, 1.02, "", transform=ax.transAxes, ha="center")

        def init():
            simplex_patch.set_xy(result.history[0])
            vertices_plot.set_data(result.history[0][:, 0], result.history[0][:, 1])
            title.set_text("Iteration: 0")
            return simplex_patch, vertices_plot, title

        def update(frame):
            if frame < len(result.history):
                simplex = result.history[frame]
                simplex_patch.set_xy(simplex)
                vertices_plot.set_data(simplex[:, 0], simplex[:, 1])
                title.set_text(f"Iteration: {frame}")
            return simplex_patch, vertices_plot, title

        anim = FuncAnimation(
            fig,
            update,
            init_func=init,
            frames=len(result.history),
            interval=interval,
            blit=True,
            repeat=True,
        )

        if save_path:
            anim.save(save_path, writer="pillow", fps=1000 // interval)
            print(f"Animation saved to {save_path}")

        return anim

    @staticmethod
    def plot_optimization_3d(
        result: OptimizationResult,
        objective: ObjectiveFunction,
        bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
        n_points: int = 50,
        figsize: tuple[int, int] = (12, 10),
    ) -> plt.Figure:
        """
        Plot 3D optimization result.

        Args:
            `result`: Optimization result
            `objective`: Objective function
            `bounds`: ((x_min, x_max), (y_min, y_max), (z_min, z_max))
            `n_points`: Number of points for surface plot
            `figsize`: Figure size

        Returns:
            Matplotlib figure

        Raises:
            `ValueError`: If problem is not 3D
        """
        if result.x_opt.size != 3:
            raise ValueError("plot_optimization_3d only works for 3D problems")

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")

        (x_min, x_max), (y_min, y_max), _ = bounds
        x = np.linspace(x_min, x_max, n_points)
        y = np.linspace(y_min, y_max, n_points)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)

        z_opt = result.x_opt[2]
        for i in range(n_points):
            for j in range(n_points):
                Z[i, j] = objective(np.array([X[i, j], Y[i, j], z_opt]))

        surf = ax.plot_surface(X, Y, Z, alpha=0.3, cmap="viridis")
        fig.colorbar(surf, ax=ax, label="f(x)", shrink=0.5)

        simplex = result.simplex

        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        for i, j in edges:
            ax.plot(
                [simplex[i, 0], simplex[j, 0]],
                [simplex[i, 1], simplex[j, 1]],
                [simplex[i, 2], simplex[j, 2]],
                "r-",
                linewidth=2,
            )

        ax.scatter(
            simplex[:, 0],
            simplex[:, 1],
            simplex[:, 2],
            c="red",
            s=100,
            label="Simplex vertices",
        )

        ax.scatter(
            result.x_opt[0],
            result.x_opt[1],
            result.x_opt[2],
            c="green",
            marker="*",
            s=300,
            label=f"Optimum: f={result.f_opt:.4e}",
        )

        ax.set_xlabel("x₁")
        ax.set_ylabel("x₂")
        ax.set_zlabel("x₃")
        ax.set_title(f"Nelder-Mead Optimization 3D (Iterations: {result.iterations})")
        ax.legend()

        return fig


def main() -> None:

    # Functions to optimize
    def rosenbrock(x: np.ndarray) -> float:
        """Rosenbrock function (minimum at [1, 1])"""
        return (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2

    def sphere(x: np.ndarray) -> float:
        """Sphere function (minimum at origin)"""
        return np.sum(x**2)

    def himmelblau(x: np.ndarray) -> float:
        """Himmelblau's function (multiple minima)"""
        return (x[0] ** 2 + x[1] - 11) ** 2 + (x[0] + x[1] ** 2 - 7) ** 2

    # Create optimizer
    params = NelderMeadParameters(
        max_iterations=200, diameter_tol=1e-6, variance_tol=1e-9
    )
    optimizer = NelderMead(parameters=params)

    # Visualizations object
    visualizer = NelderMeadVisualizer()

    # Optimize 2D Rosenbrock function
    print("=" * 60)
    print("Optimizing Rosenbrock Function with Visualization")
    print("=" * 60)
    result_rosenbrock = optimizer.optimize(
        rosenbrock, x0=np.array([0.0, 0.0]), track_history=True, verbose=True
    )
    print(result_rosenbrock)
    fig1 = visualizer.plot_optimization_2d(
        result_rosenbrock, rosenbrock, bounds=((-2, 2), (-1, 3))
    )
    plt.show()

    anim1 = visualizer.animate_optimization_2d(
        result_rosenbrock, rosenbrock, bounds=((-2, 2), (-1, 3)), interval=100
    )
    plt.show()

    # Optimize 3D Sphere function
    print("\n" + "=" * 60)
    print("Optimizing 3D Sphere Function")
    print("=" * 60)
    result_sphere = optimizer.optimize(
        sphere, x0=np.array([2.0, 2.0, 2.0]), track_history=False, verbose=True
    )
    print(result_sphere)
    fig2 = visualizer.plot_optimization_3d(
        result_sphere, sphere, bounds=((-3, 3), (-3, 3), (-3, 3))
    )
    plt.show()

    # Optimize 2D Himmelblau's function
    print("\n" + "=" * 60)
    print("Optimizing Himmelblau's Function with Visualization")
    print("=" * 60)
    result_himmelblau = optimizer.optimize(
        himmelblau, x0=np.array([0.0, 0.0]), track_history=True, verbose=True
    )
    print(result_himmelblau)
    fig3 = visualizer.plot_optimization_2d(
        result_himmelblau, himmelblau, bounds=((-5, 5), (-5, 5))
    )
    plt.show()
    anim2 = visualizer.animate_optimization_2d(
        result_himmelblau, himmelblau, bounds=((-5, 5), (-5, 5)), interval=100
    )
    plt.show()


if __name__ == "__main__":
    main()
