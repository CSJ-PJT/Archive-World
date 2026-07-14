export type District = 'archiveos' | 'market' | 'nexus' | 'logistics' | 'ledger' | 'residential' | 'infrastructure' | 'vehicle';

export interface CityInstance {
  instanceId: string;
  assetId: string;
  district: District;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  lodPolicy: 'auto' | 'candidate';
  selectable: boolean;
  routeGroup: string | null;
  animationBinding: 'route' | null;
  statusBinding: string | null;
  eventBinding: string | null;
}

export interface RuntimeEvent {
  eventId: string; eventType: string; sourceSystem: string; targetSystem: string; correlationId: string;
  orderId?: string; entityId?: string; status: 'created' | 'processing' | 'completed' | 'failed'; occurredAt: string;
}
