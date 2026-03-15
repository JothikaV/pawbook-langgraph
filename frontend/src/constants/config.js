// LangGraph nodes configuration
export const LANGGRAPH_NODES = [
  { id: 'START', label: 'START', badge: 'entry' },
  { id: 'agent', label: 'agent', badge: 'LLM node' },
  { id: 'tool_node', label: 'tool_node', badge: 'ToolNode' },
  { id: 'END', label: 'END', badge: 'terminal' },
];

// LangGraph edges
export const LG_EDGES = [
  { label: 'always' },
  { label: 'tool_calls?' },
  { label: 'loop back' },
];

// MCP Servers configuration
export const MCP_SERVERS = [
  {
    id: 'availability',
    name: 'Availability',
    port: 3101,
    icon: '📅',
    tools: ['check_availability', 'list_groomers'],
  },
  {
    id: 'pricing',
    name: 'Pricing Engine',
    port: 3102,
    icon: '💰',
    tools: ['get_pricing', 'list_addons'],
  },
  {
    id: 'booking',
    name: 'Booking',
    port: 3103,
    icon: '✅',
    tools: ['create_booking', 'get_booking', 'cancel_booking'],
  },
  {
    id: 'notification',
    name: 'Notifications',
    port: 3104,
    icon: '📬',
    tools: ['send_notification', 'get_notifications'],
  },
];

// Build tool-to-server map
export const TOOL_TO_SERVER = {};
MCP_SERVERS.forEach(s => s.tools.forEach(t => { TOOL_TO_SERVER[t] = s.id; }));

// Context labels
export const CTX_LABELS = {
  petType: 'Pet Type',
  petSize: 'Pet Size',
  petName: 'Pet Name',
  service: 'Service',
  lastBookingId: 'Booking ID',
};

// Quick prompts
export const QUICK_PROMPTS = [
  'Book a full groom for my golden retriever tomorrow evening',
  'Check evening slots for a cat this weekend',
  'How much for a large dog full groom with nail trim?',
  'What add-ons do you offer?',
];

// Welcome chips
export const WELCOME_CHIPS = [
  '🐕 Book dog grooming',
  '🐈 Groom my cat',
  '📅 Check availability',
  '💰 View pricing',
  '📋 List add-ons',
];

// API endpoints
export const API_BASE_URL = 'http://localhost:3100';
export const CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;
export const STATUS_ENDPOINT = `${API_BASE_URL}/api/status`;
export const HEALTH_ENDPOINT = `${API_BASE_URL}/api/health`;
