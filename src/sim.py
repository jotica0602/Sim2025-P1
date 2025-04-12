import random
import heapq
import numpy as np
import matplotlib.pyplot as plt
import os

class System:
    def __init__(self, lambda_rate, mu_rate, n_threads, queue_size, sim_time):
        self.lambda_rate = lambda_rate  # Tasa de llegada
        self.mu_rate = mu_rate          # Tasa de servicio
        self.n_threads = n_threads      # Número de hilos
        self.queue_size = queue_size    # Tamaño de la cola
        self.sim_time = sim_time        # Tiempo total de simulación

        # Variables internas
        self.reset_metrics()

    def reset_metrics(self):
        self.total_arrivals = 0
        self.total_served = 0
        self.total_rejected = 0
        self.total_response_time = 0
        self.total_queue_size = 0
        self.total_busy_time = 0
        self.event_queue = []
        self.threads_busy = 0
        self.queue = []

    def generate_inter_arrival_time(self):
        return np.random.exponential(1 / self.lambda_rate)

    def generate_service_time(self):
        return np.random.exponential(1 / self.mu_rate)

    def add_event(self, event_time, event_type, data=None):
        heapq.heappush(self.event_queue, (event_time, event_type, data))

    def handle_arrival(self, current_time):
        self.total_arrivals += 1
        inter_arrival_time = self.generate_inter_arrival_time()
        self.add_event(current_time + inter_arrival_time, 'arrival')

        if self.threads_busy < self.n_threads:
            self.threads_busy += 1
            service_time = self.generate_service_time()
            self.add_event(current_time + service_time, 'departure')
        elif len(self.queue) < self.queue_size:
            self.queue.append(current_time)
        else:
            self.total_rejected += 1

    def handle_departure(self, current_time):
        if self.queue:
            next_request_time = self.queue.pop(0)
            wait_time = current_time - next_request_time
            self.total_response_time += wait_time
            self.total_queue_size += len(self.queue)
            service_time = self.generate_service_time()
            self.add_event(current_time + service_time, 'departure')
        else:
            self.threads_busy -= 1
        self.total_served += 1

    def simulate(self):
        self.reset_metrics()
        current_time = 0
        self.add_event(current_time, 'arrival')

        while self.event_queue:
            event_time, event_type, data = heapq.heappop(self.event_queue)
            if event_time > self.sim_time:
                break
            current_time = event_time
            if event_type == 'arrival' and current_time < self.sim_time:
                self.handle_arrival(current_time)
            elif event_type == 'departure':
                self.handle_departure(current_time)

        # Resultados agregados
        total_requests = self.total_served + self.total_rejected
        avg_response_time = self.total_response_time / self.total_served if self.total_served else 0
        rejection_rate = self.total_rejected / total_requests if total_requests else 0
        avg_queue_size = self.total_queue_size / self.total_served if self.total_served else 0
        server_util = (self.total_served / self.sim_time) / self.n_threads

        return {
            'served': self.total_served,
            'rejected': self.total_rejected,
            'rejection_rate': rejection_rate * 100,
            'avg_response_time': avg_response_time,
            'avg_queue_size': avg_queue_size,
            'server_util': server_util * 100,
        }

# === FUNCIONES DE GRAFICADO Y EXPERIMENTACIÓN ===

def ensure_graph_dir():
    if not os.path.exists('graphs'):
        os.makedirs('graphs')

def plot_vs(x, ys, labels, xlabel, ylabel, title, filename):
    ensure_graph_dir()
    for y, label in zip(ys, labels):
        plt.plot(x, y, marker='o', label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"graphs/{filename}")
    plt.clf()

def experiment_thread_vs_rejection(lambda_rate, mu_rate, sim_time):
    threads = [1, 2, 3, 4, 5, 6]
    rejections = []

    for n in threads:
        system = System(lambda_rate, mu_rate, n, 10, sim_time)
        result = system.simulate()
        rejections.append(result['rejection_rate'])

    plot_vs(threads, [rejections], ["Rechazo (%)"], "Hilos", "Rechazo (%)",
            "Hilos vs Porcentaje de Solicitudes Rechazadas", "threads_vs_rejection.png")

def experiment_queue_vs_response(lambda_rate, mu_rate, sim_time):
    queue_sizes = [0, 5, 10, 15, 20]
    rejections, response_times = [], []

    for q in queue_sizes:
        system = System(lambda_rate, mu_rate, 3, q, sim_time)
        result = system.simulate()
        rejections.append(result['rejection_rate'])
        response_times.append(result['avg_response_time'])

    plot_vs(queue_sizes, [rejections, response_times], ["Rechazo (%)", "Tiempo Resp."],
            "Tamaño de Cola", "Métricas", "Cola vs Rechazo y Tiempo de Respuesta", "queue_vs_response.png")

def experiment_lambda_variation(mu_rate, sim_time):
    lambdas = [2, 4, 6, 8, 10]
    utils, rejections = [], []

    for lam in lambdas:
        system = System(lam, mu_rate, 3, 10, sim_time)
        result = system.simulate()
        utils.append(result['server_util'])
        rejections.append(result['rejection_rate'])

    plot_vs(lambdas, [utils, rejections], ["Uso Servidor (%)", "Rechazo (%)"],
            "λ (tasa llegada)", "Métricas (%)",
            "Tasa de Llegada (λ) vs Uso y Rechazo", "lambda_vs_metrics.png")

def experiment_mu_variation(lambda_rate, sim_time):
    mus = [2, 4, 6, 8, 10]
    utils, rejections = [], []

    for mu in mus:
        system = System(lambda_rate, mu, 3, 10, sim_time)
        result = system.simulate()
        utils.append(result['server_util'])
        rejections.append(result['rejection_rate'])

    plot_vs(mus, [utils, rejections], ["Uso Servidor (%)", "Rechazo (%)"],
            "μ (tasa servicio)", "Métricas (%)",
            "Tasa de Servicio (μ) vs Uso y Rechazo", "mu_vs_metrics.png")

# === EJECUCIÓN DEL EXPERIMENTO ===

lambda_rate = 5
mu_rate = 6
sim_time = 1000

experiment_thread_vs_rejection(lambda_rate, mu_rate, sim_time)
experiment_queue_vs_response(lambda_rate, mu_rate, sim_time)
experiment_lambda_variation(mu_rate, sim_time)
experiment_mu_variation(lambda_rate, sim_time)

print("Simulaciones finalizadas. Gráficos guardados en carpeta 'graphs/'.")
