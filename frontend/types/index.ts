export type AgentPersonaType = 'Skeptical VC' | 'Financial Analyst' | 'Market Realist';
export type SeverityLevelType = 'Critical' | 'High' | 'Medium' | 'Low';
export type SessionStatusType = 'initialized' | 'in_progress' | 'awaiting_user_response' | 'evaluating_round' | 'completed' | 'failed';

export interface StartupPitch {
  id?: string;
  title: string;
  tagline: string;
  problem: string;
  solution: string;
  target_market: string;
  business_model: string;
  traction?: string;
  competition?: string;
  fundraising_goal?: string;
  created_at?: string;
}

export interface AgentChallenge {
  persona: AgentPersonaType;
  reasoning_summary: string;
  question: string;
  severity: SeverityLevelType;
  evidence_citation?: string;
}

export interface AgentReaction {
  persona: AgentPersonaType;
  reaction_summary: string;
  satisfaction_score: number;
  lingering_concern?: string;
}

export interface RoundRecord {
  round_number: number;
  challenges: AgentChallenge[];
  founder_response?: string;
  reactions?: AgentReaction[];
}

export interface WeaknessItem {
  title: string;
  category: string;
  severity: SeverityLevelType;
  description: string;
  recommended_fix: string;
}

export interface PersonaScore {
  persona: AgentPersonaType;
  score: number;
  verdict: string;
  key_takeaway: string;
}

export interface FinalVerdict {
  overall_score: number;
  investment_recommendation: string;
  executive_summary: string;
  survival_odds_percentage: number;
  persona_scores: PersonaScore[];
  ranked_weaknesses: WeaknessItem[];
  priority_action_plan: string[];
}

export interface SessionState {
  session_id: string;
  thread_id: string;
  pitch: StartupPitch;
  current_round: number;
  total_rounds: number;
  status: SessionStatusType;
  current_challenges?: AgentChallenge[];
  current_reactions?: AgentReaction[];
  rounds_history?: RoundRecord[];
  verdict?: FinalVerdict;
  created_at: string;
  updated_at: string;
  error_message?: string;
}
