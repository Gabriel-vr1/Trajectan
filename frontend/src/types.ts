import type { components } from "./api-schema";
export type Event = components["schemas"]["Event"];
export type State = Required<components["schemas"]["State"]>;
export type Forecast = components["schemas"]["ForecastResult"];
export type Narrative = {
  headline: string;
  text: string;
  source_sequence: number;
  profile: string;
  execution_mode?: string;
  moments?: Event[];
  investigation_refs?: string[];
  revisions?: {
    hypothesis: string;
    previous_assessment: string;
    assessment: string;
    previous_sequence: number;
    source_sequence: number;
    basis: string;
  }[];
};
export type Investigation = {
  investigation_id: string;
  source_sequence: number;
  status: string;
  execution_mode: string;
  revision?: number;
  evidence_ids: string[];
  tool_count: number;
  trace: {
    stage: string;
    operation: string;
    detail: string;
    duration_ms: number;
    inference?: { response_id: string; deployment: string; sdk: string };
  }[];
  narratives: Record<string, Narrative>;
  validation: { valid: boolean; errors: string[] } | null;
  observations: Record<string, unknown>;
  relations: { type: string; target: string }[];
};
export type Scenario = {
  source_sequence: number;
  baseline: Forecast;
  alternative: Forecast;
  delta: Record<string, number>;
  delta_standard_errors: Record<string, number>;
  label: string;
};

export type Attribution = {
  previous_sequence: number;
  source_sequence: number;
  delta: number;
  contributions: {
    factor: string;
    home: number;
    standard_error?: number;
    interval_95?: number[];
  }[];
  order?: string;
  residual: number;
  verified: boolean;
  uncertainty: string;
  limitation: string;
  samples: number;
};
