import { useState, useEffect } from "react";

interface Incident {
  id: string;
  rootCause: string;
  confidence: number;
  status: string;
}

export function useIncident() {
  const [incident, setIncident] = useState<Incident | null>(null);

  useEffect(() => {
    // Mock incident state
    setIncident({
      id: "incident-1",
      rootCause: "Database connection pool exhaustion",
      confidence: 0.85,
      status: "Active",
    });
  }, []);

  return { incident };
}
