import random
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

# Adjust import based on your project structure
try:
    from ..models import LogEntry, ServiceName
    from ..utils.helpers import generate_id
except ImportError:
    # Fallback for direct execution (not needed in normal run)
    from app.models import LogEntry, ServiceName
    from app.utils.helpers import generate_id


class LogSimulator:
    """
    Simulates realistic log generation for multiple microservices.
    Generates normal logs and injects incident patterns on demand.
    """

    def __init__(self):
        self.services = [
            ServiceName.API_GATEWAY,
            ServiceName.AUTH_SERVICE,
            ServiceName.PAYMENT_SERVICE,
            ServiceName.DATABASE,
            ServiceName.REDIS_CACHE
        ]

        # Different log templates per service
        self.templates = {
            ServiceName.API_GATEWAY: {
                "info": [
                    "Request received: GET /api/v1/users",
                    "Request received: POST /api/v1/payments",
                    "Response sent: 200 OK",
                    "Rate limit check passed for client_id={client_id}",
                    "Route resolved to service: {service}"
                ],
                "warning": [
                    "Request took {duration}ms (threshold 500ms)",
                    "Rate limit nearing threshold: {usage}%",
                    "Retrying request to {service} after timeout",
                    "Invalid API key format from IP {ip}"
                ],
                "error": [
                    "Connection timeout to {service}",
                    "Failed to forward request: 502 Bad Gateway",
                    "Rate limit exceeded for client_id={client_id}",
                    "Circuit breaker open for {service}"
                ]
            },
            ServiceName.AUTH_SERVICE: {
                "info": [
                    "User {user_id} authenticated successfully",
                    "Token validated for session {session_id}",
                    "JWT generated for user {user_id}",
                    "Permission check passed for {resource}"
                ],
                "warning": [
                    "Token expiration in {minutes} minutes",
                    "Multiple failed login attempts for user {user_id}",
                    "Refresh token rotated"
                ],
                "error": [
                    "Invalid JWT signature",
                    "User {user_id} not found",
                    "Authentication failed: invalid credentials",
                    "Token expired for session {session_id}"
                ]
            },
            ServiceName.PAYMENT_SERVICE: {
                "info": [
                    "Payment initiated: amount={amount} currency=USD",
                    "Payment authorized for order {order_id}",
                    "Refund processed: order={order_id} amount={amount}",
                    "Payment method {method} accepted"
                ],
                "warning": [
                    "High payment volume detected: {count}/min",
                    "Payment gateway latency {latency}ms",
                    "Retrying failed payment: order {order_id}"
                ],
                "error": [
                    "Payment declined: insufficient funds",
                    "Gateway timeout after {timeout}s",
                    "Fraud detection triggered for order {order_id}",
                    "Database transaction failed: deadlock detected"
                ]
            },
            ServiceName.DATABASE: {
                "info": [
                    "Connection pool created: size={size}",
                    "Query executed: {query} took {duration}ms",
                    "Index scan used for table {table}",
                    "Transaction committed: {transaction_id}"
                ],
                "warning": [
                    "Slow query detected: {query} took {duration}ms",
                    "Connection pool usage: {usage}%",
                    "Table {table} lock wait timeout"
                ],
                "error": [
                    "Connection refused: pool exhausted",
                    "Deadlock detected: transaction {tx_id} rolled back",
                    "Disk space low: {free_mb}MB remaining",
                    "Query timeout: {query} exceeded {timeout}ms"
                ]
            },
            ServiceName.REDIS_CACHE: {
                "info": [
                    "Cache hit: key={key}",
                    "Cache miss: key={key}",
                    "Key {key} evicted (LRU)",
                    "Memory usage: {used_mb}MB / {max_mb}MB"
                ],
                "warning": [
                    "Memory usage high: {used_percent}%",
                    "Slow command: {command} took {duration}ms",
                    "Replica sync in progress"
                ],
                "error": [
                    "Connection timeout to master",
                    "OOM command not allowed when used memory > maxmemory",
                    "LOADING: Redis loading dataset",
                    "CLUSTERDOWN: Hash slot not served"
                ]
            }
        }

        self.incident_active = False
        self.incident_type = None
        self.incident_start_time = None
        self.affected_services = []

    def _random_value(self, template: str) -> str:
        """Replace placeholders with realistic random values."""
        replacements = {
            "{client_id}": str(random.randint(1000, 9999)),
            "{service}": random.choice([s.value for s in self.services]),
            "{duration}": str(random.randint(100, 5000)),
            "{usage}": str(random.randint(70, 99)),
            "{ip}": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            "{user_id}": f"user_{random.randint(1,1000)}",
            "{session_id}": generate_id("session")[:12],
            "{minutes}": str(random.randint(1, 10)),
            "{resource}": random.choice(["dashboard", "reports", "admin", "profile"]),
            "{amount}": str(round(random.uniform(10, 500), 2)),
            "{order_id}": f"ORD{random.randint(100000, 999999)}",
            "{method}": random.choice(["visa", "mastercard", "paypal", "crypto"]),
            "{count}": str(random.randint(10, 100)),
            "{latency}": str(random.randint(500, 3000)),
            "{timeout}": str(random.randint(5, 30)),
            "{size}": str(random.randint(10, 50)),
            "{query}": random.choice([
                "SELECT * FROM users WHERE id = ?",
                "INSERT INTO payments VALUES (?, ?, ?)",
                "UPDATE orders SET status = ? WHERE id = ?",
                "DELETE FROM sessions WHERE expired = true"
            ]),
            "{table}": random.choice(["users", "payments", "orders", "sessions", "logs"]),
            "{transaction_id}": generate_id("txn")[:8],
            "{free_mb}": str(random.randint(50, 5000)),
            "{key}": random.choice(["session:123", "cache:user:456", "rate_limit:789", "config:app"]),
            "{used_mb}": str(random.randint(500, 8000)),
            "{max_mb}": str(random.randint(8000, 16000)),
            "{used_percent}": str(random.randint(80, 98)),
            "{command}": random.choice(["GET", "SET", "INCR", "LPUSH", "ZADD"]),
            "{tx_id}": str(random.randint(1, 9999))
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        return result

    def generate_log(self, service: ServiceName, level: str = None) -> LogEntry:
        """Generate a single log entry for a given service."""
        if level is None:
            # Probabilities: 80% info, 15% warning, 5% error (amplify errors during incident)
            if self.incident_active:
                # During incident: more errors/warnings
                rand = random.random()
                if rand < 0.5:
                    level = "error"
                elif rand < 0.8:
                    level = "warning"
                else:
                    level = "info"
            else:
                rand = random.random()
                if rand < 0.8:
                    level = "info"
                elif rand < 0.95:
                    level = "warning"
                else:
                    level = "error"

        templates = self.templates.get(service, {}).get(level, ["Unknown log message"])
        template = random.choice(templates)
        message = self._random_value(template)

        # For incident-specific overrides
        if self.incident_active and self.incident_type:
            if self.incident_type == "db_connection_exhaustion" and service == ServiceName.DATABASE:
                if level == "error":
                    message = random.choice([
                        "Connection refused: pool exhausted (max 20 connections)",
                        "FATAL: remaining connection slots are reserved",
                        "Too many clients already, connection rejected"
                    ])
                elif level == "warning":
                    message = random.choice([
                        "Connection pool usage: 98% (19/20 active)",
                        "Waiting for connection: timeout 5000ms"
                    ])
            elif self.incident_type == "payment_timeout" and service == ServiceName.PAYMENT_SERVICE:
                if level == "error":
                    message = random.choice([
                        "Gateway timeout after 30s: payment declined",
                        "HTTP 504: upstream request timeout",
                        "Payment provider unreachable: connection reset"
                    ])
            elif self.incident_type == "redis_memory_exhaustion" and service == ServiceName.REDIS_CACHE:
                if level == "error":
                    message = random.choice([
                        "OOM command not allowed when used memory > maxmemory",
                        "Can't save in background: fork: Cannot allocate memory"
                    ])

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.ms

        return LogEntry(
            timestamp=timestamp,
            service=service,
            level=level.upper(),
            message=message,
            metadata={"incident_active": self.incident_active}
        )

    def trigger_incident(self, incident_type: str, duration_seconds: int = 5):
        """Simulate an incident for a specified duration."""
        self.incident_active = True
        self.incident_type = incident_type
        self.incident_start_time = time.time()

        # Set affected services based on incident type
        if incident_type == "db_connection_exhaustion":
            self.affected_services = [ServiceName.DATABASE, ServiceName.PAYMENT_SERVICE, ServiceName.API_GATEWAY]
        elif incident_type == "payment_timeout":
            self.affected_services = [ServiceName.PAYMENT_SERVICE, ServiceName.API_GATEWAY]
        elif incident_type == "redis_memory_exhaustion":
            self.affected_services = [ServiceName.REDIS_CACHE, ServiceName.AUTH_SERVICE]
        else:
            self.affected_services = random.sample(self.services, k=random.randint(1, 3))

        # Auto-resolve after duration
        def resolve():
            time.sleep(duration_seconds)
            self.incident_active = False
            self.incident_type = None
            self.affected_services = []

        threading.Thread(target=resolve, daemon=True).start()

    def generate_log_batch(self, count: int = 5) -> List[LogEntry]:
        """Generate a batch of log entries (multiple services, random order)."""
        logs = []
        for _ in range(count):
            service = random.choice(self.services)
            logs.append(self.generate_log(service))
        return logs

    def get_incident_info(self) -> Dict[str, Any]:
        """Return current incident status and affected services."""
        return {
            "active": self.incident_active,
            "type": self.incident_type,
            "affected_services": [s.value for s in self.affected_services],
            "started_at": datetime.fromtimestamp(self.incident_start_time).isoformat() if self.incident_start_time else None
        }


# Singleton instance for use across the backend
simulator = LogSimulator()