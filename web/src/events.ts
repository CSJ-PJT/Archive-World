import type { RuntimeEvent } from './types';
export type RuntimeMode = 'mock' | 'live';
export interface EventAdapter { mode: RuntimeMode; status: 'online' | 'offline' | 'mock'; events(): Promise<RuntimeEvent[]>; }
const mockEvents: RuntimeEvent[] = [
  { eventId: 'mock-market-001', eventType: 'ORDER_ACCEPTED', sourceSystem: 'Archive Market', targetSystem: 'Archive Nexus', correlationId: 'mock-correlation-001', orderId: 'demo-order-001', entityId: 'truck-market-nexus', status: 'processing', occurredAt: new Date().toISOString() },
  { eventId: 'mock-nexus-001', eventType: 'PRODUCTION_COMPLETE', sourceSystem: 'Archive Nexus', targetSystem: 'Archive Logistics', correlationId: 'mock-correlation-002', orderId: 'demo-order-002', entityId: 'truck-nexus-logistics', status: 'completed', occurredAt: new Date().toISOString() },
  { eventId: 'mock-ledger-001', eventType: 'SETTLEMENT_POSTED', sourceSystem: 'Archive Logistics', targetSystem: 'Archive Ledger', correlationId: 'mock-correlation-003', entityId: 'ledger-settlement', status: 'completed', occurredAt: new Date().toISOString() }
];
export function createAdapter(mode: RuntimeMode, baseUrl: string): EventAdapter {
  if (mode === 'mock') return { mode, status: 'mock', events: async () => mockEvents };
  return { mode, status: 'offline', async events() { const response = await fetch(`${baseUrl.replace(/\/$/, '')}/api/live-flow/events/recent`, { headers: { Accept: 'application/json' } }); if (!response.ok) throw new Error(`ArchiveOS live-flow HTTP ${response.status}`); const body = await response.json(); return Array.isArray(body) ? body : body.events ?? []; } };
}
